from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.docstore.document import Document
from sentence_transformers import CrossEncoder
from typing import List, Tuple
import re, os, warnings

# 警告ログを抑制（検索スコアなど不要なログを出さないため）
warnings.filterwarnings("ignore")

# =========================================
# ① PDF読み込み＆チャンク化の箱（インポートフェーズ）
# =========================================
class PDFRagSystem:
    """
    PDFファイルを読み込んで、検索可能な形式に変換するクラス
    
    役割：
    - PDFをテキストに変換
    - テキストを適切なサイズのチャンク（断片）に分割
    - 384次元のベクトル化（意味検索用）
    - キーワード検索用のBM25辞書を作成
    - Chroma DBに保存（次回以降の検索で再利用可能）
    """
    def __init__(self, persist_dir="./chroma_db"):
        # Chroma DBの保存フォルダを1つの変数で管理（統一して使い回す）
        self.persist_dir = persist_dir
        self.vectorstore = None
        self.docs: List[Document] = []
        
        # Semantic検索用のembeddingモデル（384次元で統一）
        # このモデルは文章の意味を384個の数値で表現する
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Keyword検索用のBM25は仕込み工程で1回だけ作る
        # （検索時には再構築せず、このインスタンスを再利用する）
        self.bm25 = None

    def clean_text(self, text: str) -> str:
        """
        テキストのノイズを除去する関数
        連続する改行を整理して、読みやすい形式にする
        """
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def import_pdf(self, pdf_path: str):
        """
        PDFファイルを読み込んで、検索可能な形式に変換する
        
        処理の流れ：
        1. PDFをテキストに変換
        2. テキストを適切なサイズのチャンクに分割
        3. 短すぎるチャンクを除外
        4. BM25検索器を構築（キーワード検索用）
        5. Chroma DBを生成（意味検索用のベクトルDB）
        """
        # PDFをロード（ページごとに分割されて返ってくる）
        raw_docs = PyPDFLoader(pdf_path).load()

        # チャンキング戦略の設定
        # chunk_size: 1つのチャンクの最大文字数
        # chunk_overlap: チャンク間の重複文字数（文脈を保つため）
        # separators: 分割する際の優先順位（段落→改行→句点→空白の順）
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=420,
            chunk_overlap=80,
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )

        # PDFをチャンクに分割
        chunks = splitter.split_documents(raw_docs)

        # クリーニング後のチャンクをDocument形式で保存
        # 各チャンクに一意のIDを付与（リランキング前後の順番比較に使用）
        cleaned = []
        for idx, c in enumerate(chunks):
            text = self.clean_text(c.page_content)
            # 文章が存在し、短すぎないチャンクだけ採用（120文字以上）
            if text and len(text) > 120:
                # metadataにチャンク識別子を追加（page番号とチャンク番号の組み合わせ）
                chunk_id = f"chunk_{c.metadata.get('page', 0)}_{idx}"
                metadata = c.metadata.copy()
                metadata['chunk_id'] = chunk_id
                cleaned.append(Document(page_content=text, metadata=metadata))

        self.docs = cleaned

        # BM25検索器を1回だけ構築（キーワード検索のための辞書作り）
        # BM25は単語の出現頻度を使って検索する手法
        self.bm25 = BM25Retriever.from_documents(self.docs)
        self.bm25.k = 60  # 候補取得数（多様なキーワード検索が成立する値）

        # Chroma DB の初期化（古いDBが残っていたら削除して新規作成）
        # これにより、次元不一致エラーを防ぐ
        if os.path.exists(self.persist_dir):
            os.system(f"rm -rf {self.persist_dir}")

        # ベクトルDB（Semantic検索用の箱）を生成
        # 各チャンクを384次元のベクトルに変換して保存
        self.vectorstore = Chroma.from_documents(
            self.docs, self.embeddings, persist_directory=self.persist_dir
        )

# =========================================
# ② RAGシステムの箱（検索と回答生成）
# =========================================
class ReRankingRAG:
    """
    リランキング付きRAGシステムのクラス
    
    役割：
    - Semantic検索（意味検索）とBM25検索（キーワード検索）を組み合わせる
    - CrossEncoderを使って検索結果を再ランキング（精度向上）
    - LLMを使って質問に対する結論を生成
    - weightsの比重を変えることで、検索の焦点を調整可能
    """
    def __init__(self, docs: List[Document], persist_dir="./chroma_db"):
        # 検索対象チャンクを保持
        self.docs = docs
        self.persist_dir = persist_dir

        # embeddingモデル（Semantic検索用、384次元で統一）
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # LLMモデル（Ollama llama3）
        # temperature=0.0で一貫性のある回答を生成
        self.llm = Ollama(model="llama3:latest", temperature=0.0)

        # semantic検索器はすでに作成済みのDBを読むだけ（ここでは新規生成しない）
        # 既存のChroma DBから読み込むことで、次元の一貫性を保つ
        self.vectorstore = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings
        )
        self.semantic = self.vectorstore.as_retriever(search_kwargs={"k": 60})

        # Keyword検索器（BM25）はPDF仕込みで作ったものを使うので再構築しない
        # ただし、ReRankingRAGクラス内でも参照できるように再構築が必要
        self.bm25 = BM25Retriever.from_documents(self.docs)
        self.bm25.k = 60  # 候補取得数

        # CrossEncoderリランカー
        # 質問と文書のペアに対して、より正確な関連度スコアを計算する
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def clean_text(self, text: str) -> str:
        """テキストのノイズを除去する関数"""
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    def search(self, question: str, k: int, w_sem: float, w_key: float, candidate_k: int = 60) -> List[Document]:
        """
        ハイブリッド検索 + リランキングを実行する
        
        処理の流れ：
        1. Semantic検索とBM25検索をEnsembleRetrieverで統合
        2. weightsの比重（w_sem, w_key）で検索結果を調整
        3. CrossEncoderで各候補を再評価してスコア計算
        4. スコアの高い順に並び替え（リランキング）
        5. 上位k件を返す
        
        Args:
            question: 検索クエリ（質問文）
            k: 返す文書の数
            w_sem: Semantic検索の重み（0.0〜1.0）
            w_key: BM25検索の重み（0.0〜1.0）
            candidate_k: リランキング前の候補数
        
        Returns:
            リランキング後の上位k件の文書リスト
        """
        # Semantic + Keyword のハイブリッド検索
        # EnsembleRetrieverは2つの検索結果を統合する
        ensemble = EnsembleRetriever(
            retrievers=[self.semantic, self.bm25],
            weights=[w_sem, w_key]
        )
        candidates = ensemble.get_relevant_documents(question)

        # CrossEncoderでスコア計算し並び替え
        # 質問と各候補文書のペアを作成
        pairs: List[Tuple[str, str]] = [(question, d.page_content) for d in candidates]
        # 各ペアの関連度スコアを計算
        scores = self.reranker.predict(pairs)
        # スコアの高い順に並び替え
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

        # 上位k件を返す（スコアは返さない）
        return [doc for doc, _score in ranked[:k]]

    def answer(self, question: str, k: int, w_sem: float, w_key: float, candidate_k: int = 60) -> str:
        """
        質問に対する結論を生成する（LLMの回答から「結論：〜」の1行のみ抽出）
        
        処理の流れ：
        1. search()で関連文書を検索
        2. 検索結果を文脈としてLLMに渡す
        3. LLMが生成した回答から「結論：〜」の行だけ抽出
        
        Args:
            question: 質問文
            k: 検索結果から使用する文書数
            w_sem: Semantic検索の重み
            w_key: BM25検索の重み
            candidate_k: リランキング前の候補数
        
        Returns:
            「結論：〜」の形式の1行のみ（日本語）
        """
        # 検索 → 上位k件の文脈をLLMへ
        top_docs = self.search(question, k, w_sem, w_key, candidate_k)
        context = "\n\n".join(d.page_content for d in top_docs)

        # LLMに渡すプロンプト（結論1行だけ日本語で生成）
        prompt = f"""
【参考情報】
{context}

【質問】
{question}

【指示】
- 必ず日本語で回答する
- 1つの軸に偏らず複数の評価軸で比較する
- 余計な説明はせず「結論：〜」の1行だけ出力してください
""".strip()

        raw_answer = self.llm.invoke(prompt)

        # 結論1行だけ抽出
        for line in raw_answer.split("\n"):
            if line.strip().startswith("結論"):
                return line.strip()

        # 保険：1行抽出できなければ先頭1行だけ返す
        return raw_answer.split("\n")[0].strip()

    def generate_conclusion(self, question: str, k: int, w_sem: float, w_key: float, candidate_k: int = 60) -> str:
        """
        answer()のエイリアス（後方互換性のため）
        """
        return self.answer(question, k, w_sem, w_key, candidate_k)

# =========================================
# ③ 実行フェーズ
# =========================================
if __name__ == "__main__":
    # PDFファイルのパス（プロジェクトルートにあるPDFファイル）
    pdf_path = "linuxtext_ver4.0.0.pdf"

    # ① PDFの仕込み（チャンク/embedding/キーワード検索辞書/ベクトルDB生成）
    # この処理で、PDFが検索可能な形式に変換される
    importer = PDFRagSystem(persist_dir="./chroma_db")
    importer.import_pdf(pdf_path)

    # ② リランキングRAGを構築（検索/結論生成担当）
    # 検索と回答生成のためのシステムを初期化
    rerag = ReRankingRAG(importer.docs, persist_dir="./chroma_db")

    # ②-1 リランキング動作の観察ログ（1回だけ表示）
    # リランキングが実際に順番を変えていることを確認するため、
    # テスト用の質問でリランキング前後の上位3件のIDを表示
    test_question = "Linux 初心者 学習 実務 重要ポイント"
    
    # リランキング前の候補を取得（EnsembleRetrieverの結果）
    ensemble = EnsembleRetriever(
        retrievers=[rerag.semantic, rerag.bm25],
        weights=[0.5, 0.5]  # テスト用のweights
    )
    candidates_before = ensemble.get_relevant_documents(test_question)
    
    # リランキング後の候補を取得（CrossEncoderで再評価）
    pairs: List[Tuple[str, str]] = [(test_question, d.page_content) for d in candidates_before]
    scores = rerag.reranker.predict(pairs)
    ranked = sorted(zip(candidates_before, scores), key=lambda x: x[1], reverse=True)
    candidates_after = [doc for doc, _score in ranked]
    
    # 上位3件のIDを表示（metadataからchunk_idを取得）
    def get_chunk_id(doc: Document) -> str:
        """Documentからchunk_idを取得する（なければフォールバック）"""
        return doc.metadata.get('chunk_id', f"page_{doc.metadata.get('page', 'unknown')}")
    
    before_ids = [get_chunk_id(doc) for doc in candidates_before[:3]]
    after_ids = [get_chunk_id(doc) for doc in candidates_after[:3]]
    
    print("Rerank前 top3 IDs:", before_ids)
    print("Rerank後 top3 IDs:", after_ids)
    print()  # 空行を追加

    # ③ weights比較実験
    # Semantic検索とBM25検索の比重を5段階で変更し、
    # それぞれの比重でLLMが生成する結論がどう変わるかを観察する
    # 
    # weightsの意味：
    # - (0.9, 0.1): Semantic検索を重視（意味の類似性を優先）
    # - (0.7, 0.3): Semantic検索をやや重視
    # - (0.5, 0.5): 両方を均等に重視
    # - (0.3, 0.7): BM25検索をやや重視（キーワードマッチを優先）
    # - (0.1, 0.9): BM25検索を重視（キーワードマッチを優先）
    
    weight_cases = [
        (0.9, 0.1),  # Semantic: 90%, BM25: 10%
        (0.7, 0.3),  # Semantic: 70%, BM25: 30%
        (0.5, 0.5),  # Semantic: 50%, BM25: 50%
        (0.3, 0.7),  # Semantic: 30%, BM25: 70%
        (0.1, 0.9),  # Semantic: 10%, BM25: 90%
    ]

    # 収束しない比較型の質問
    # 1つの観点に収束せず、複数の評価軸（セキュリティ/運用/拡張/学習効率/トラブルシューティング/コミュニティ活用）
    # を同時に比較する問い。キーワード検索でPDF内の多様な用語を拾える内容。
    question = """
Linux を学ぶ初心者が実務で活かせるポイントを、
セキュリティ/運用/拡張/学習効率/トラブルシューティング/コミュニティ活用 の6軸以上で比較し、
semantic:keyword の比重による評価の焦点変化も意識しながら、
結論のみを1行で日本語で述べてください。
""".strip()

    # 各weightsで検索→リランキング→LLM生成を実行
    # 実行ログはLLM生成の結論5件のみ表示（検索スコア・検索ログ・チャンク内容はprintしない）
    for w_sem, w_key in weight_cases:
        result = rerag.answer(
            question=question,
            k=5,  # 検索結果から上位5件を使用
            w_sem=w_sem,
            w_key=w_key,
            candidate_k=60,  # リランキング前の候補数
        )
        print(result)

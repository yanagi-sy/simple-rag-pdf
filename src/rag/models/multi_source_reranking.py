"""
複数ソース対応ReRankingRAGシステム

複数ソース対応のリランキング付きRAGシステム。
"""

from langchain_community.llms import Ollama
from langchain.retrievers import EnsembleRetriever
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from sentence_transformers import CrossEncoder
from typing import List, Tuple, Optional

from .multi_source import MultiSourceRagSystem
from ..utils.text import clean_text


class MultiSourceReRankingRAG:
    """
    複数ソース対応のリランキング付きRAGシステム
    
    既存のReRankingRAGの設計思想を維持しつつ、
    MultiSourceRagSystemで構築したインデックスを使用するように拡張したクラス。
    
    主な機能：
    - MultiSourceRagSystemで構築したインデックスを使用
    - 検索結果にソース情報（source_type, source_name）を含める
    - 既存のReRankingRAGと同じ検索・リランキング・回答生成の流れ
    """
    
    def __init__(self, multi_source_system: MultiSourceRagSystem):
        """
        初期化メソッド
        
        Args:
            multi_source_system: MultiSourceRagSystemのインスタンス
                                （build_index()が呼ばれた後の状態）
        """
        # MultiSourceRagSystemの参照を保持
        self.multi_source_system = multi_source_system
        
        # 検索対象チャンクを保持
        self.docs = multi_source_system.docs
        self.persist_dir = multi_source_system.persist_dir
        
        # embeddingモデル（Semantic検索用、384次元で統一）
        self.embeddings = multi_source_system.embeddings
        
        # LLMモデル（Ollama llama3）
        self.llm = Ollama(model="llama3:latest", temperature=0.0)
        
        # MultiSourceRagSystemで構築済みのvectorstoreを使用
        self.vectorstore = multi_source_system.vectorstore
        self.semantic = self.vectorstore.as_retriever(search_kwargs={"k": 60})
        
        # MultiSourceRagSystemで構築済みのBM25を使用
        self.bm25 = multi_source_system.bm25
        
        # CrossEncoderリランカー
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        
        # プロンプトテンプレート（後で設定可能）
        self.prompt_template: Optional[PromptTemplate] = None
    
    def search(self, question: str, k: int, w_sem: float, w_key: float, candidate_k: int = 60) -> List[Document]:
        """
        ハイブリッド検索 + リランキングを実行する（既存のReRankingRAGと同じ）
        
        検索結果には、各チャンクのmetadataにsource_typeとsource_nameが含まれます。
        これにより、どのソースから来たチャンクかが分かります。
        
        Args:
            question: 検索クエリ（質問文）
            k: 返す文書の数
            w_sem: Semantic検索の重み（0.0〜1.0）
            w_key: BM25検索の重み（0.0〜1.0）
            candidate_k: リランキング前の候補数
        
        Returns:
            リランキング後の上位k件の文書リスト（各文書にsource_typeとsource_nameが含まれる）
        """
        # Semantic + Keyword のハイブリッド検索
        ensemble = EnsembleRetriever(
            retrievers=[self.semantic, self.bm25],
            weights=[w_sem, w_key]
        )
        candidates = ensemble.get_relevant_documents(question)
        
        # CrossEncoderでスコア計算し並び替え
        pairs: List[Tuple[str, str]] = [(question, d.page_content) for d in candidates]
        scores = self.reranker.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        
        # 上位k件を返す（各Documentにはsource_typeとsource_nameが含まれる）
        return [doc for doc, _score in ranked[:k]]
    
    def answer(self, question: str, k: int, w_sem: float, w_key: float, candidate_k: int = 60) -> str:
        """
        質問に対する回答を生成する（既存のReRankingRAGと同じ）
        
        Args:
            question: 質問文
            k: 検索結果から使用する文書数
            w_sem: Semantic検索の重み
            w_key: BM25検索の重み
            candidate_k: リランキング前の候補数
        
        Returns:
            LLMが生成した回答（文字列）
        """
        if self.prompt_template is None:
            raise ValueError("プロンプトテンプレートが設定されていません。")
        
        # 検索 → 上位k件の文脈をLLMへ
        top_docs = self.search(question, k, w_sem, w_key, candidate_k)
        context = "\n\n".join(d.page_content for d in top_docs)
        
        # PromptTemplateを使ってプロンプトを生成
        prompt = self.prompt_template.format(context=context, question=question)
        
        # LLMにプロンプトを渡して回答を生成
        raw_answer = self.llm.invoke(prompt)
        
        return raw_answer.strip()

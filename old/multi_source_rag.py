"""
複数ソース対応RAGシステム

複数のソース（PDF/テキストファイル/手動テキスト）を統合管理するRAGシステム。
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.docstore.document import Document
from typing import List, Optional
import os

from utils import clean_text


class MultiSourceRagSystem:
    """
    複数のソース（PDF/テキストファイル/手動テキスト）を統合管理するRAGシステム
    
    既存のPDFRagSystemの設計思想を維持しつつ、
    複数のソースを1つの知識ベースとして扱えるように拡張したクラス。
    
    主な機能：
    - 複数のPDFファイルを読み込む
    - テキストファイル（.txt）を読み込む
    - 手動で入力したテキストを読み込む
    - すべてのソースを統合して1つの知識ベースとして扱う
    - 各チャンクにソース情報（source_type, source_name）を付与
    """
    
    def __init__(self, persist_dir="./chroma_db"):
        """
        初期化メソッド
        
        Args:
            persist_dir: ベクトルデータベースを保存するフォルダのパス
        """
        # Chroma DBの保存フォルダ
        self.persist_dir = persist_dir
        
        # ベクトルストア（後で初期化される）
        self.vectorstore = None
        
        # すべてのソースから読み込んだチャンクを統合したリスト
        self.docs: List[Document] = []
        
        # 読み込んだソースの情報を管理するリスト
        # 各要素は {"type": "pdf/text_file/manual_text", "name": "ファイル名 or 識別名"}
        self.sources: List[dict] = []
        
        # Semantic検索用のembeddingモデル（既存と同じ384次元）
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Keyword検索用のBM25（後で初期化される）
        self.bm25 = None
    
    def add_pdf(self, pdf_path: str, source_name: Optional[str] = None):
        """
        PDFファイルを追加するメソッド
        
        既存のPDFRagSystemのimport_pdfメソッドのロジックを再利用し、
        ソース情報をmetadataに付与します。
        
        Args:
            pdf_path: PDFファイルのパス
            source_name: ソース名（Noneの場合はファイル名を使用）
        """
        # ソース名が指定されていない場合は、ファイル名を使用
        if source_name is None:
            source_name = os.path.basename(pdf_path)
        
        # PDFを読み込む
        raw_docs = PyPDFLoader(pdf_path).load()
        
        # チャンキング戦略の設定
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=420,
            chunk_overlap=80,
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )
        
        # PDFをチャンクに分割
        chunks = splitter.split_documents(raw_docs)
        
        # チャンクをクリーニングして、ソース情報を付与
        for idx, c in enumerate(chunks):
            text = clean_text(c.page_content)
            
            if text and len(text) > 120:
                # metadataにチャンク識別子を追加
                chunk_id = f"chunk_{c.metadata.get('page', 0)}_{idx}"
                metadata = c.metadata.copy()
                metadata['chunk_id'] = chunk_id
                
                # ソース情報をmetadataに追加
                metadata['source_type'] = 'pdf'
                metadata['source_name'] = source_name
                
                cleaned_doc = Document(page_content=text, metadata=metadata)
                self.docs.append(cleaned_doc)
        
        # ソース情報を記録
        self.sources.append({
            "type": "pdf",
            "name": source_name,
            "path": pdf_path
        })
    
    def add_text_file(self, text_path: str, source_name: Optional[str] = None):
        """
        テキストファイルを追加するメソッド
        
        .txtファイルを読み込んで、チャンクに分割して追加します。
        
        Args:
            text_path: テキストファイルのパス
            source_name: ソース名（Noneの場合はファイル名を使用）
        """
        # ソース名が指定されていない場合は、ファイル名を使用
        if source_name is None:
            source_name = os.path.basename(text_path)
        
        # テキストファイルを読み込む
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except UnicodeDecodeError:
            # UTF-8で読めない場合は、Shift_JISを試す
            with open(text_path, 'r', encoding='shift_jis') as f:
                text_content = f.read()
        
        # テキストをDocument形式に変換
        raw_doc = Document(
            page_content=text_content,
            metadata={"page": 0}
        )
        
        # チャンキング戦略の設定
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=420,
            chunk_overlap=80,
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )
        
        # テキストをチャンクに分割
        chunks = splitter.split_documents([raw_doc])
        
        # チャンクをクリーニングして、ソース情報を付与
        for idx, c in enumerate(chunks):
            text = clean_text(c.page_content)
            
            if text and len(text) > 120:
                # metadataにチャンク識別子を追加
                chunk_id = f"chunk_0_{idx}"
                metadata = c.metadata.copy()
                metadata['chunk_id'] = chunk_id
                
                # ソース情報をmetadataに追加
                metadata['source_type'] = 'text_file'
                metadata['source_name'] = source_name
                
                cleaned_doc = Document(page_content=text, metadata=metadata)
                self.docs.append(cleaned_doc)
        
        # ソース情報を記録
        self.sources.append({
            "type": "text_file",
            "name": source_name,
            "path": text_path
        })
    
    def add_manual_text(self, text_content: str, source_name: str):
        """
        手動で入力したテキストを追加するメソッド
        
        UI上で直接入力したテキストを読み込んで、チャンクに分割して追加します。
        
        Args:
            text_content: テキストの内容
            source_name: ソース名（ユーザーが指定した識別名）
        """
        # テキストをDocument形式に変換
        raw_doc = Document(
            page_content=text_content,
            metadata={"page": 0}
        )
        
        # チャンキング戦略の設定
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=420,
            chunk_overlap=80,
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )
        
        # テキストをチャンクに分割
        chunks = splitter.split_documents([raw_doc])
        
        # チャンクをクリーニングして、ソース情報を付与
        for idx, c in enumerate(chunks):
            text = clean_text(c.page_content)
            
            if text and len(text) > 120:
                # metadataにチャンク識別子を追加
                chunk_id = f"chunk_0_{idx}"
                metadata = c.metadata.copy()
                metadata['chunk_id'] = chunk_id
                
                # ソース情報をmetadataに追加
                metadata['source_type'] = 'manual_text'
                metadata['source_name'] = source_name
                
                cleaned_doc = Document(page_content=text, metadata=metadata)
                self.docs.append(cleaned_doc)
        
        # ソース情報を記録
        self.sources.append({
            "type": "manual_text",
            "name": source_name,
            "path": None  # 手動入力なのでパスはなし
        })
    
    def build_index(self):
        """
        すべてのソースを統合して、検索可能なインデックスを構築するメソッド
        
        このメソッドは、すべてのソースを追加した後に1回だけ呼び出します。
        既存のPDFRagSystemと同じように、BM25とChroma DBを構築します。
        """
        if not self.docs:
            raise ValueError("チャンクが存在しません。先にソースを追加してください。")
        
        # Chroma DBの初期化（古いDBが残っていたら削除して新規作成）
        if os.path.exists(self.persist_dir):
            os.system(f"rm -rf {self.persist_dir}")
        
        # BM25検索器を構築（キーワード検索用）
        self.bm25 = BM25Retriever.from_documents(self.docs)
        self.bm25.k = 60  # 候補取得数
        
        # ベクトルDB（Semantic検索用）を生成
        self.vectorstore = Chroma.from_documents(
            self.docs, self.embeddings, persist_directory=self.persist_dir
        )
    
    def get_source_info(self) -> List[dict]:
        """
        読み込んだソースの情報を取得するメソッド
        
        Returns:
            ソース情報のリスト
        """
        return self.sources.copy()
    
    def remove_source(self, source_index: int):
        """
        ソースを削除するメソッド
        
        指定されたインデックスのソースと、そのソースから生成されたチャンクを削除します。
        削除後は、build_index()を再度呼び出す必要があります。
        
        Args:
            source_index: 削除するソースのインデックス（0から始まる）
        
        Raises:
            IndexError: 指定されたインデックスが範囲外の場合
        """
        if source_index < 0 or source_index >= len(self.sources):
            raise IndexError(f"ソースインデックス {source_index} が範囲外です。")
        
        # 削除するソースの情報を取得
        source_to_remove = self.sources[source_index]
        source_type = source_to_remove["type"]
        source_name = source_to_remove["name"]
        
        # 該当するソースのチャンクを削除
        self.docs = [
            doc for doc in self.docs
            if not (doc.metadata.get('source_type') == source_type and 
                   doc.metadata.get('source_name') == source_name)
        ]
        
        # ソース情報からも削除
        self.sources.pop(source_index)
        
        # BM25とvectorstoreをクリア（再構築が必要）
        self.bm25 = None
        self.vectorstore = None

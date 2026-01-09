"""
PDF読み込み処理

PDFファイルを読み込んで、検索可能な形式に変換するモジュール。
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.docstore.document import Document
from typing import List, Optional
import os

from ..utils.text import clean_text


class PDFRagSystem:
    """
    PDFファイルまたはテキストファイルを読み込んで、検索可能な形式に変換するクラス
    
    役割：
    - PDFまたはテキストファイルを読み込む
    - テキストを適切なサイズのチャンク（断片）に分割
    - 384次元のベクトル化（意味検索用）
    - キーワード検索用のBM25辞書を作成
    - Chroma DBに保存（次回以降の検索で再利用可能）
    """
    def __init__(self, persist_dir="./chroma_db", chunk_size=1200, chunk_overlap=200, min_chunk_length=300):
        """
        初期化メソッド
        
        Args:
            persist_dir: ベクトルデータベースを保存するフォルダのパス
                        デフォルトは "./chroma_db"（現在のフォルダ内に作成）
            chunk_size: 1つのチャンクの最大文字数（デフォルト: 1200文字）
            chunk_overlap: チャンク間の重複文字数（デフォルト: 200文字）
            min_chunk_length: 最小チャンク長（これより短いチャンクは除外、デフォルト: 300文字）
        """
        # Chroma DBの保存フォルダを1つの変数で管理（統一して使い回す）
        self.persist_dir = persist_dir
        
        # チャンク設定を保存
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_length = min_chunk_length
        
        # ベクトルストア（後で初期化される）
        self.vectorstore = None
        
        # チャンク化された文書のリスト
        self.docs: List[Document] = []
        
        # 読み込んだファイルのパスを保存
        self.file_path: Optional[str] = None
        self.file_type: Optional[str] = None  # "pdf" or "text"
        
        # Semantic検索用のembeddingモデル（384次元で統一）
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Keyword検索用のBM25（後で初期化される）
        self.bm25 = None

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
        # PDFをテキストに変換
        raw_docs = PyPDFLoader(pdf_path).load()

        # テキストを適切なサイズのチャンクに分割
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,      # 1つのチャンクの最大文字数
            chunk_overlap=self.chunk_overlap, # チャンク間の重複文字数
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )

        # PDFをチャンクに分割
        chunks = splitter.split_documents(raw_docs)

        # チャンクをクリーニングして整理
        cleaned = []
        for idx, c in enumerate(chunks):
            # テキストをクリーニング（不要な改行などを削除）
            text = clean_text(c.page_content)
            
            # 文章が存在し、短すぎないチャンクだけ採用
            if text and len(text) > self.min_chunk_length:
                # metadataにチャンク識別子を追加
                chunk_id = f"chunk_{c.metadata.get('page', 0)}_{idx}"
                metadata = c.metadata.copy()
                metadata['chunk_id'] = chunk_id
                cleaned.append(Document(page_content=text, metadata=metadata))

        # クリーニング済みのチャンクを保存
        self.docs = cleaned

        # キーワード検索用のBM25検索器を構築
        self.bm25 = BM25Retriever.from_documents(self.docs)
        self.bm25.k = 60  # 候補取得数

        # Chroma DB の初期化（古いDBが残っていたら削除して新規作成）
        if os.path.exists(self.persist_dir):
            os.system(f"rm -rf {self.persist_dir}")

        # ベクトルDB（Semantic検索用）を生成
        self.vectorstore = Chroma.from_documents(
            self.docs,
            self.embeddings,
            persist_directory=self.persist_dir
        )
    
    def import_text_file(self, text_path: str):
        """
        テキストファイルを読み込んで、検索可能な形式に変換する
        
        処理の流れ：
        1. テキストファイルを読み込む
        2. テキストを適切なサイズのチャンクに分割
        3. 短すぎるチャンクを除外
        4. BM25検索器を構築（キーワード検索用）
        5. Chroma DBを生成（意味検索用のベクトルDB）
        
        Args:
            text_path: テキストファイルのパス
        """
        self.file_path = text_path
        self.file_type = "text"
        
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
            metadata={"page": 0, "source": text_path}
        )
        
        # テキストを適切なサイズのチャンクに分割
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,      # 1つのチャンクの最大文字数
            chunk_overlap=self.chunk_overlap, # チャンク間の重複文字数
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )
        
        # テキストをチャンクに分割
        chunks = splitter.split_documents([raw_doc])
        
        # チャンクをクリーニングして整理
        cleaned = []
        for idx, c in enumerate(chunks):
            # テキストをクリーニング（不要な改行などを削除）
            text = clean_text(c.page_content)
            
            # 文章が存在し、短すぎないチャンクだけ採用
            if text and len(text) > self.min_chunk_length:
                # metadataにチャンク識別子を追加
                chunk_id = f"chunk_0_{idx}"
                metadata = c.metadata.copy()
                metadata['chunk_id'] = chunk_id
                cleaned.append(Document(page_content=text, metadata=metadata))
        
        # クリーニング済みのチャンクを保存
        self.docs = cleaned
        
        # キーワード検索用のBM25検索器を構築
        self.bm25 = BM25Retriever.from_documents(self.docs)
        self.bm25.k = 60  # 候補取得数
        
        # Chroma DB の初期化（古いDBが残っていたら削除して新規作成）
        if os.path.exists(self.persist_dir):
            os.system(f"rm -rf {self.persist_dir}")
        
        # ベクトルDB（Semantic検索用）を生成
        self.vectorstore = Chroma.from_documents(
            self.docs,
            self.embeddings,
            persist_directory=self.persist_dir
        )
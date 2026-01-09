"""
ソース管理モジュール

単一のPDFファイルまたはテキストファイルを管理するモジュール。

このモジュールは、以下の機能を提供します：
- PDFファイルの選択: 単一のPDFファイルを選択して読み込む
- テキストファイルの選択: .txtファイルを選択して読み込む
- 読み込んだファイルの表示: ファイル名をラベルに表示
"""

import os
from typing import Optional

import tkinter as tk
from tkinter import filedialog, messagebox

from src.rag import PDFRagSystem


class SourceManager:
    """
    ソース管理クラス
    
    単一のファイル（PDFまたはテキストファイル）を読み込んで管理します。
    """
    
    def __init__(self, ui_instance):
        """
        初期化メソッド
        
        Args:
            ui_instance: RAGTerminalUIのインスタンス（他のコンポーネントにアクセスするため）
        """
        self.ui = ui_instance
    
    def select_pdf_file(self):
        """
        単一のPDFファイルを選択するメソッド
        
        ファイル選択ダイアログを開いて、ユーザーにPDFファイルを選択させます。
        選択されたファイルが、PDFRagSystemに読み込まれます。
        """
        # 単一ファイル選択ダイアログを表示
        file_path = filedialog.askopenfilename(
            title="PDFファイルを選択",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        # ファイルが選択された場合、PDFファイルを読み込む
        if file_path:
            self.load_pdf_file(file_path)
    
    def select_text_file(self):
        """
        テキストファイルを選択するメソッド
        
        ファイル選択ダイアログを開いて、ユーザーにテキストファイル（.txt）を選択させます。
        選択されたファイルが、PDFRagSystemに読み込まれます。
        """
        # テキストファイル選択ダイアログを表示
        file_path = filedialog.askopenfilename(
            title="テキストファイルを選択",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        # ファイルが選択された場合、テキストファイルを読み込む
        if file_path:
            self.load_text_file(file_path)
    
    def load_pdf_file(self, pdf_path: str):
        """
        PDFファイルをPDFRagSystemに読み込むメソッド
        
        Args:
            pdf_path: PDFファイルのパス
        """
        try:
            # PDFRagSystemを初期化（chunk_size=1200, chunk_overlap=200）
            pdf_rag = PDFRagSystem(
                persist_dir="./chroma_db",
                chunk_size=1200,
                chunk_overlap=200,
                min_chunk_length=300
            )
            
            # PDFファイルを読み込む（自動的にインデックスも構築される）
            pdf_rag.import_pdf(pdf_path)
            
            # RAG統合コンポーネントに保存
            self.ui.rag_integration.pdf_rag_system = pdf_rag
            self.ui.pdf_rag_system = pdf_rag
            
            # ファイル名を表示
            self.update_file_display(os.path.basename(pdf_path), "PDF")
            
            # 成功メッセージを表示
            self.ui.message_handler.add_system_message(
                f"PDFファイルを読み込みました: {os.path.basename(pdf_path)}\n"
                f"チャンク数: {len(pdf_rag.docs)}\n"
                f"質問を開始できます。"
            )
        except Exception as e:
            self.ui.message_handler.add_error_message(f"PDFファイルの読み込みに失敗しました: {str(e)}")
    
    def load_text_file(self, text_path: str):
        """
        テキストファイルをPDFRagSystemに読み込むメソッド
        
        Args:
            text_path: テキストファイルのパス
        """
        try:
            # PDFRagSystemを初期化（chunk_size=1200, chunk_overlap=200）
            pdf_rag = PDFRagSystem(
                persist_dir="./chroma_db",
                chunk_size=1200,
                chunk_overlap=200,
                min_chunk_length=300
            )
            
            # テキストファイルを読み込む（自動的にインデックスも構築される）
            pdf_rag.import_text_file(text_path)
            
            # RAG統合コンポーネントに保存
            self.ui.rag_integration.pdf_rag_system = pdf_rag
            self.ui.pdf_rag_system = pdf_rag
            
            # ファイル名を表示
            self.update_file_display(os.path.basename(text_path), "TXT")
            
            # 成功メッセージを表示
            self.ui.message_handler.add_system_message(
                f"テキストファイルを読み込みました: {os.path.basename(text_path)}\n"
                f"チャンク数: {len(pdf_rag.docs)}\n"
                f"質問を開始できます。"
            )
        except Exception as e:
            self.ui.message_handler.add_error_message(f"テキストファイルの読み込みに失敗しました: {str(e)}")
    
    def update_file_display(self, filename: str, file_type: str):
        """
        読み込んだファイル名を表示するメソッド
        
        Args:
            filename: ファイル名
            file_type: ファイルタイプ（"PDF" または "TXT"）
        """
        if self.ui.file_label:
            self.ui.file_label.config(text=f"[{file_type}] {filename}")

"""
メッセージ表示モジュール

チャット表示エリアにメッセージを表示する機能を提供するモジュール。

このモジュールは、以下のメッセージタイプを表示します：
- システムメッセージ: 青、太字（システムからの通知）
- ユーザーメッセージ: ライトブルー（ユーザーが入力した質問）
- アシスタントメッセージ: パステルブルー（LLMが生成した回答）
- エラーメッセージ: 赤（エラーが発生した場合）

各メッセージには、タイムスタンプが自動的に追加されます。
"""

import tkinter as tk
from datetime import datetime


class MessageHandler:
    """
    メッセージ表示クラス
    
    チャット表示エリアにシステムメッセージ、ユーザーメッセージ、
    アシスタントメッセージ、エラーメッセージを表示します。
    """
    
    def __init__(self, chat_display):
        """
        初期化メソッド
        
        Args:
            chat_display: チャット表示エリア（ScrolledTextウィジェット）
        """
        self.chat_display = chat_display
    
    def add_system_message(self, message: str):
        """
        システムメッセージを追加するメソッド
        
        システムからの通知メッセージ（例：「PDFファイルを読み込んでいます」）
        をチャット表示エリアに追加します。
        
        Args:
            message: 表示するメッセージ（文字列）
        """
        # テキストエリアを編集可能にする
        self.chat_display.config(state=tk.NORMAL)
        
        # 現在時刻を取得してタイムスタンプとして表示
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # タイムスタンプを追加（"timestamp"タグでスタイルを適用）
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # システムメッセージを追加（"system"タグでスタイルを適用）
        self.chat_display.insert(tk.END, f"SYSTEM: {message}\n\n", "system")
        
        # テキストエリアを編集不可に戻す（ユーザーが直接編集できないように）
        self.chat_display.config(state=tk.DISABLED)
        
        # 最新のメッセージまで自動的にスクロール
        self.chat_display.see(tk.END)
    
    def add_user_message(self, message: str):
        """
        ユーザーメッセージを追加するメソッド
        
        ユーザーが入力した質問をチャット表示エリアに追加します。
        
        Args:
            message: ユーザーのメッセージ（質問文）
        """
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # タイムスタンプを追加
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # ユーザーメッセージを追加（"user"タグでスタイルを適用）
        self.chat_display.insert(tk.END, f"USER: {message}\n\n", "user")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def add_assistant_message(self, message: str):
        """
        アシスタントメッセージを追加するメソッド
        
        LLMが生成した回答をチャット表示エリアに追加します。
        
        Args:
            message: アシスタントのメッセージ（LLMの回答）
        """
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # タイムスタンプを追加
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # アシスタントメッセージを追加（"assistant"タグでスタイルを適用）
        self.chat_display.insert(tk.END, f"ASSISTANT: {message}\n\n", "assistant")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def add_error_message(self, message: str):
        """
        エラーメッセージを追加するメソッド
        
        エラーが発生した場合に、エラーメッセージをチャット表示エリアに追加します。
        
        Args:
            message: エラーメッセージ（エラーの内容）
        """
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # タイムスタンプを追加
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # エラーメッセージを追加（"error"タグでスタイルを適用）
        self.chat_display.insert(tk.END, f"ERROR: {message}\n\n", "error")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def clear_chat(self):
        """
        チャット履歴をクリアするメソッド
        
        チャット表示エリアの内容をクリアします。
        このメソッドは、ユーザーが「クリア」ボタンをクリックしたときに呼ばれます。
        
        注意：
        - このメソッドはチャット表示エリアの内容のみをクリアします
        - 会話履歴（conversation_history）はクリアしません（呼び出し側で処理する必要があります）
        """
        # テキストエリアを編集可能にする
        self.chat_display.config(state=tk.NORMAL)
        
        # テキストエリアの内容をすべて削除
        self.chat_display.delete("1.0", tk.END)
        
        # テキストエリアを編集不可に戻す
        self.chat_display.config(state=tk.DISABLED)

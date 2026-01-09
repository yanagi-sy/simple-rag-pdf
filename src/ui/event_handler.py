"""
イベントハンドラーモジュール

ユーザーの操作（キーボード入力、ボタンクリックなど）に対するイベントハンドラーを提供するモジュール。

このモジュールは、以下のイベントを処理します：
- Enterキー: メッセージを送信（Shift+Enterの場合は改行）
- メッセージ送信: 質問をRAGシステムに送信し、回答を生成

すべての重い処理（検索、LLMの回答生成）は別スレッドで実行されるため、
UIがフリーズすることはありません。
"""

import tkinter as tk


class EventHandler:
    """
    イベントハンドラークラス
    
    ユーザーの操作に対するイベント処理を行います。
    """
    
    def __init__(self, ui_instance):
        """
        初期化メソッド
        
        Args:
            ui_instance: RAGTerminalUIのインスタンス（他のコンポーネントにアクセスするため）
        """
        self.ui = ui_instance
    
    def on_enter_key(self, event):
        """
        Enterキーが押されたときの処理
        
        - Enterキーのみ: メッセージを送信
        - Shift+Enter: 改行（通常の動作）
        
        Args:
            event: イベントオブジェクト（押されたキーの情報などが含まれる）
        
        Returns:
            str or None: "break"を返すとイベントの伝播を停止、Noneを返すと通常の動作を許可
        """
        # Shift+Enterの場合は改行を許可（通常の動作）
        # event.state & 0x1 = Shiftキーが押されているかどうかをチェック
        if event.state & 0x1:  # Shiftキーが押されている
            return None  # Noneを返す = 通常の動作（改行）を許可
        
        # Enterキーのみの場合は送信
        self.ui._send_message()
        
        # "break"を返す = 通常の動作（改行）をキャンセル
        return "break"
    
    def on_shift_enter(self, event):
        """
        Shift+Enterキーが押されたときの処理（改行）
        
        改行を許可するため、Noneを返します（通常の動作を許可）。
        
        Args:
            event: イベントオブジェクト
        
        Returns:
            None: 通常の動作（改行）を許可
        """
        return None
    
    def send_message(self):
        """
        メッセージを送信するメソッド
        
        このメソッドは、ユーザーが質問を入力して送信したときに呼ばれます。
        
        処理の流れ：
        1. 入力フィールドから質問を取得
        2. ユーザーの質問をチャット表示エリアに表示
        3. RAG統合コンポーネントに質問を送信（検索と回答生成を実行）
        """
        # 入力フィールドからテキストを取得
        user_input = self.ui.input_field.get("1.0", tk.END).strip()
        
        # 入力が空の場合は何もしない
        if not user_input:
            return
        
        # 入力フィールドをクリア（次の質問を入力しやすくするため）
        self.ui.input_field.delete("1.0", tk.END)
        
        # ユーザーメッセージを表示
        self.ui.message_handler.add_user_message(user_input)
        
        # RAG統合コンポーネントに質問を送信（検索と回答生成を実行）
        self.ui.rag_integration.send_message(user_input)

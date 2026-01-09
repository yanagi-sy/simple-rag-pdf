"""
RAG Terminal UI - メインクラス

Tkinterを用いたターミナル風チャットUIのメインクラス。
分割されたモジュール（UI構築、メッセージ表示、イベントハンドラー、ソース管理、RAG統合）を統合します。
"""

import tkinter as tk
from typing import Optional

# 分割されたモジュールをインポート
from .ui_builder import UIBuilder
from .message_handler import MessageHandler
from .event_handler import EventHandler
from .source_manager import SourceManager
from .rag_integration import RAGIntegration


class RAGTerminalUI:
    """
    RAG Terminal UI メインクラス
    
    Tkinterを用いたターミナル風チャットUIを提供します。
    単一のPDFファイルまたはテキストファイルを読み込んで、対話型の質問応答システムを構築します。
    
    このクラスは、以下のコンポーネントを統合します：
    - UIBuilder: UIウィジェットの構築
    - MessageHandler: メッセージの表示
    - EventHandler: ユーザー操作のイベント処理
    - SourceManager: ファイル（PDF/テキストファイル）の管理
    - RAGIntegration: RAGシステムとの統合
    """
    
    def __init__(self, root: tk.Tk):
        """
        初期化メソッド
        
        このメソッドは、アプリケーションを起動する際に最初に呼ばれます。
        UIの設定や、各コンポーネントの準備を行います。
        
        Args:
            root: Tkinterのルートウィンドウ（メインウィンドウ）
        """
        # =========================================
        # ウィンドウの基本設定
        # =========================================
        self.root = root
        self.root.title("RAG Terminal UI - 単一ファイル対応質問応答システム")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e1e")
        
        # =========================================
        # コンポーネントの初期化
        # =========================================
        # まず、RAG統合コンポーネントを初期化（プロンプトテンプレートを設定するため）
        self.rag_integration = RAGIntegration(self)
        
        # RAGシステムのインスタンス変数（RAG統合コンポーネントへの参照を保持）
        # これらの変数は、後でファイルが読み込まれたときに更新される
        self.pdf_rag_system: Optional = None
        self.rag_system: Optional = None
        self.prompt_template = self.rag_integration.prompt_template
        
        # 会話履歴の管理（将来、会話履歴を活用する機能を追加する場合に備えて保存）
        self.conversation_history = []
        
        # =========================================
        # UIの構築
        # =========================================
        # メインフレームを作成
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 上部フレームを構築（ファイル選択ボタン、ファイル名表示、検索重み設定）
        top_widgets = UIBuilder.build_top_frame(main_frame, self)
        self.file_label = top_widgets['file_label']
        self.semantic_weight = top_widgets['semantic_weight']
        self.keyword_weight = top_widgets['keyword_weight']
        
        # チャット表示エリアを構築
        self.chat_display = UIBuilder.build_chat_display(main_frame)
        
        # 入力エリアを構築
        self.input_field = UIBuilder.build_input_area(main_frame, self)
        
        # =========================================
        # コンポーネントの初期化（UIウィジェットを渡す）
        # =========================================
        # メッセージハンドラーを初期化（チャット表示エリアを渡す）
        self.message_handler = MessageHandler(self.chat_display)
        
        # イベントハンドラーを初期化
        self.event_handler = EventHandler(self)
        
        # ソースマネージャーを初期化
        self.source_manager = SourceManager(self)
        
        # =========================================
        # 初期メッセージの表示
        # =========================================
        # ユーザーへの案内メッセージを表示
        self.message_handler.add_system_message(
            "RAG Terminal UI にようこそ！\n"
            "PDFファイルまたはテキストファイルを選択して読み込んでください。\n"
            "ファイルが読み込まれたら、質問を開始できます。"
        )
    
    # =========================================
    # ソース管理メソッド（SourceManagerへの委譲）
    # =========================================
    
    def _select_pdf_file(self):
        """PDFファイルを選択するメソッド（SourceManagerに委譲）"""
        self.source_manager.select_pdf_file()
    
    def _select_text_file(self):
        """テキストファイルを選択するメソッド（SourceManagerに委譲）"""
        self.source_manager.select_text_file()
    
    # =========================================
    # RAG統合メソッド（RAGIntegrationへの委譲）
    # =========================================
    # （インデックス構築は不要になったため、削除）
    
    # =========================================
    # イベントハンドラーメソッド（EventHandlerへの委譲）
    # =========================================
    
    def _on_enter_key(self, event):
        """Enterキーが押されたときの処理（EventHandlerに委譲）"""
        return self.event_handler.on_enter_key(event)
    
    def _on_shift_enter(self, event):
        """Shift+Enterキーが押されたときの処理（EventHandlerに委譲）"""
        return self.event_handler.on_shift_enter(event)
    
    def _send_message(self):
        """メッセージを送信するメソッド（EventHandlerに委譲）"""
        self.event_handler.send_message()
    
    def _clear_chat(self):
        """チャット履歴をクリアするメソッド（MessageHandlerに委譲）"""
        self.message_handler.clear_chat()
        self.conversation_history.clear()
        # クリア完了メッセージを表示
        self.message_handler.add_system_message("チャット履歴をクリアしました。")
    
    # =========================================
    # 後方互換性のためのメソッド（非推奨）
    # =========================================
    
    def _add_system_message(self, message: str):
        """システムメッセージを追加するメソッド（後方互換性のため、MessageHandlerに委譲）"""
        self.message_handler.add_system_message(message)
    
    def _add_user_message(self, message: str):
        """ユーザーメッセージを追加するメソッド（後方互換性のため、MessageHandlerに委譲）"""
        self.message_handler.add_user_message(message)
    
    def _add_assistant_message(self, message: str):
        """アシスタントメッセージを追加するメソッド（後方互換性のため、MessageHandlerに委譲）"""
        self.message_handler.add_assistant_message(message)
    
    def _add_error_message(self, message: str):
        """エラーメッセージを追加するメソッド（後方互換性のため、MessageHandlerに委譲）"""
        self.message_handler.add_error_message(message)


def main():
    """
    メイン関数
    
    この関数は、アプリケーションを起動する際に最初に呼ばれます。
    Tkinterのウィンドウを作成し、RAGTerminalUIクラスのインスタンスを作成して、
    アプリケーションを実行します。
    """
    # Tkinterのルートウィンドウを作成
    root = tk.Tk()
    
    # RAGTerminalUIクラスのインスタンスを作成
    app = RAGTerminalUI(root)
    
    # メインループを開始（ユーザーの操作を待ち受ける）
    root.mainloop()


if __name__ == "__main__":
    """
    このスクリプトが直接実行された場合のみ、main()関数を呼び出す
    
    if __name__ == "__main__": の意味：
    - このファイルが直接実行された場合: __name__ は "__main__" になる
    - このファイルが他のファイルからインポートされた場合: __name__ は "src.ui.terminal" になる
    
    これにより、このファイルをインポートしても、main()が自動的に実行されない
    """
    main()

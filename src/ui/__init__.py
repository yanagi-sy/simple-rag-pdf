"""
UIモジュール

ユーザーインターフェースを提供するモジュール。

このモジュールは、以下のコンポーネントで構成されています：
- terminal: メインクラス（RAGTerminalUI）
- ui_builder: UIウィジェットの構築
- message_handler: メッセージの表示
- event_handler: ユーザー操作のイベント処理
- source_manager: ソース（PDF/テキストファイル/手動テキスト）の管理
- rag_integration: RAGシステムとの統合
"""

from .terminal import RAGTerminalUI
from .ui_builder import UIBuilder
from .message_handler import MessageHandler
from .event_handler import EventHandler
from .source_manager import SourceManager
from .rag_integration import RAGIntegration

__all__ = [
    'RAGTerminalUI',
    'UIBuilder',
    'MessageHandler',
    'EventHandler',
    'SourceManager',
    'RAGIntegration',
]

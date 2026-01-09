"""
UI構築モジュール

ターミナル風チャットUIのウィジェット（ボタン、テキストエリアなど）を構築するモジュール。

このモジュールは、UIウィジェットの作成と配置を担当します：
- 上部フレーム: ソース追加ボタン、ソース一覧、検索重み設定
- チャット表示エリア: 会話履歴を表示するスクロール可能なテキストエリア
- 入力エリア: ユーザーが質問を入力するテキストフィールドと送信・クリアボタン

各ウィジェットは、ダークテーマ（GitHub風）で統一されたデザインになっています。
"""

import tkinter as tk
from tkinter import scrolledtext


class UIBuilder:
    """
    UI構築クラス
    
    Tkinterのウィジェットを配置して、ユーザーが操作できるインターフェースを構築します。
    すべてのメソッドは静的メソッド（@staticmethod）として実装されており、
    クラスのインスタンスを作成せずに使用できます。
    
    設計方針：
    - UIの構築ロジックをこのクラスに集約することで、メインクラスのコードを簡潔に保つ
    - 各ウィジェットの作成ロジックを分離することで、保守性を向上
    - ダークテーマで統一されたデザインを提供
    """
    
    @staticmethod
    def build_top_frame(main_frame, ui_instance):
        """
        上部フレームを構築するメソッド
        
        ファイル選択ボタン、読み込んだファイル表示、検索重み設定などを配置します。
        
        構築されるウィジェット：
        1. ファイル選択ボタン群
           - 「PDF選択」ボタン
           - 「テキストファイル選択」ボタン
        2. 読み込んだファイル表示エリア
           - ファイル名を表示するラベル
        3. 検索重み設定
           - Semantic検索の重みスライダー
           - Keyword検索の重みスライダー
        
        Args:
            main_frame: メインフレーム（親コンテナ）
            ui_instance: RAGTerminalUIのインスタンス（コールバック関数にアクセスするため）
        
        Returns:
            dict: 構築されたウィジェットの参照を格納した辞書
                - 'file_label': 読み込んだファイル名を表示するLabelウィジェット
                - 'semantic_weight': Semantic検索の重みを保持するDoubleVar
                - 'keyword_weight': Keyword検索の重みを保持するDoubleVar
        """
        # 上部フレームを作成
        top_frame = tk.Frame(main_frame, bg="#1e1e1e")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # ファイル選択ボタン群を配置
        button_frame = tk.Frame(top_frame, bg="#1e1e1e")
        button_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        # PDF選択ボタン
        pdf_button = tk.Button(
            button_frame,
            text="PDF選択",
            command=ui_instance._select_pdf_file,
            bg="#2d2d2d",
            fg="#c9d1d9",
            activebackground="#3d3d3d",
            activeforeground="#c9d1d9",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            font=("Consolas", 9)
        )
        pdf_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # テキストファイル選択ボタン
        text_file_button = tk.Button(
            button_frame,
            text="テキストファイル選択",
            command=ui_instance._select_text_file,
            bg="#2d2d2d",
            fg="#c9d1d9",
            activebackground="#3d3d3d",
            activeforeground="#c9d1d9",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            font=("Consolas", 9)
        )
        text_file_button.pack(side=tk.LEFT)
        
        # 読み込んだファイル表示エリア
        file_display_frame = tk.Frame(top_frame, bg="#1e1e1e")
        file_display_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # ファイル名のラベル
        tk.Label(
            file_display_frame,
            text="読み込んだファイル:",
            bg="#1e1e1e",
            fg="#c9d1d9",
            font=("Consolas", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # ファイル名を表示するラベル
        file_label = tk.Label(
            file_display_frame,
            text="なし",
            bg="#0d1117",
            fg="#c9d1d9",
            font=("Consolas", 9),
            relief=tk.FLAT,
            padx=10,
            pady=5,
            anchor=tk.W
        )
        file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 検索重みの設定
        weight_frame = tk.Frame(top_frame, bg="#1e1e1e")
        weight_frame.pack(side=tk.RIGHT)
        
        # Semantic検索の重みラベル
        tk.Label(
            weight_frame,
            text="Semantic:",
            bg="#1e1e1e",
            fg="#c9d1d9",
            font=("Consolas", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Semantic検索の重みを調整するスライダー
        semantic_weight = tk.DoubleVar(value=0.5)
        semantic_scale = tk.Scale(
            weight_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=semantic_weight,
            bg="#2d2d2d",
            fg="#c9d1d9",
            troughcolor="#1e1e1e",
            activebackground="#3d3d3d",
            length=100,
            font=("Consolas", 8)
        )
        semantic_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        # Keyword検索の重みラベル
        tk.Label(
            weight_frame,
            text="Keyword:",
            bg="#1e1e1e",
            fg="#c9d1d9",
            font=("Consolas", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Keyword検索の重みを調整するスライダー
        keyword_weight = tk.DoubleVar(value=0.5)
        keyword_scale = tk.Scale(
            weight_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=keyword_weight,
            bg="#2d2d2d",
            fg="#c9d1d9",
            troughcolor="#1e1e1e",
            activebackground="#3d3d3d",
            length=100,
            font=("Consolas", 8)
        )
        keyword_scale.pack(side=tk.LEFT)
        
        # 構築したウィジェットの参照を返す
        return {
            'file_label': file_label,
            'semantic_weight': semantic_weight,
            'keyword_weight': keyword_weight
        }
    
    @staticmethod
    def build_chat_display(main_frame):
        """
        チャット表示エリアを構築するメソッド
        
        会話履歴を表示するスクロール可能なテキストエリアを作成します。
        
        Args:
            main_frame: メインフレーム（親コンテナ）
        
        Returns:
            scrolledtext.ScrolledText: チャット表示エリアのウィジェット
        """
        # チャット表示フレームを作成
        chat_frame = tk.Frame(main_frame, bg="#1e1e1e")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # スクロール可能なテキストエリアを作成
        chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg="#0d1117",
            fg="#c9d1d9",
            insertbackground="#c9d1d9",
            selectbackground="#264f78",
            selectforeground="#ffffff",
            font=("Consolas", 11),
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=15,
            state=tk.DISABLED
        )
        chat_display.pack(fill=tk.BOTH, expand=True)
        
        # ターミナル風のスタイルを設定
        chat_display.tag_configure("system", foreground="#58a6ff", font=("Consolas", 11, "bold"))
        chat_display.tag_configure("user", foreground="#79c0ff", font=("Consolas", 11))
        chat_display.tag_configure("assistant", foreground="#a5d6ff", font=("Consolas", 11))
        chat_display.tag_configure("error", foreground="#f85149", font=("Consolas", 11))
        chat_display.tag_configure("timestamp", foreground="#6e7681", font=("Consolas", 9))
        
        return chat_display
    
    @staticmethod
    def build_input_area(main_frame, ui_instance):
        """
        入力エリアを構築するメソッド
        
        ユーザーが質問を入力するテキストフィールドと送信・クリアボタンを作成します。
        
        Args:
            main_frame: メインフレーム（親コンテナ）
            ui_instance: RAGTerminalUIのインスタンス（コールバック関数にアクセスするため）
        
        Returns:
            tk.Text: 入力フィールドのウィジェット
        """
        # 入力フレームを作成
        input_frame = tk.Frame(main_frame, bg="#1e1e1e")
        input_frame.pack(fill=tk.X)
        
        # 入力フィールドを作成
        input_field = tk.Text(
            input_frame,
            height=3,
            bg="#0d1117",
            fg="#c9d1d9",
            insertbackground="#c9d1d9",
            selectbackground="#264f78",
            selectforeground="#ffffff",
            font=("Consolas", 11),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # キーボードイベントを設定
        input_field.bind("<Return>", ui_instance._on_enter_key)
        input_field.bind("<Shift-Return>", ui_instance._on_shift_enter)
        
        # 送信ボタン
        send_button = tk.Button(
            input_frame,
            text="送信",
            command=ui_instance._send_message,
            bg="#238636",
            fg="#ffffff",
            activebackground="#2ea043",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            font=("Consolas", 10, "bold"),
            cursor="hand2"
        )
        send_button.pack(side=tk.RIGHT)
        
        # クリアボタン
        clear_button = tk.Button(
            input_frame,
            text="クリア",
            command=ui_instance._clear_chat,
            bg="#da3633",
            fg="#ffffff",
            activebackground="#f85149",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=15,
            pady=10,
            font=("Consolas", 10),
            cursor="hand2"
        )
        clear_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # 初期フォーカスを設定
        input_field.focus_set()
        
        return input_field

# 単一ファイル対応RAGシステム

単一のPDFファイルまたはテキストファイルに対応したRAG（Retrieval-Augmented Generation）システムです。

## 概要

このシステムは、1つのPDFファイルまたはテキストファイルを読み込んで、対話型の質問応答システムを構築します。ハイブリッド検索（セマンティック検索とキーワード検索）とリランキングを使用して、精度の高い回答を生成します。

### 主な機能

- **単一ファイル対応**: PDFファイルまたはテキストファイルを1つ読み込む
- **ハイブリッド検索**: セマンティック検索とキーワード検索（BM25）を組み合わせ
- **リランキング**: CrossEncoderを使用して検索結果の精度を向上
- **ターミナル風UI**: Tkinterベースの対話型チャットインターフェース
- **チャンク設定**: chunk_size=1200、chunk_overlap=200で最適化

## システム構成

### ディレクトリ構成

```
simple_rag.py/
├── src/                               # ソースコード
│   ├── __init__.py
│   ├── rag/                           # RAGシステムコア
│   │   ├── __init__.py
│   │   ├── loaders/                   # データローダー
│   │   │   ├── __init__.py
│   │   │   └── pdf.py                 # PDF/テキスト読み込み処理（PDFRagSystem）
│   │   ├── models/                    # RAGモデル
│   │   │   ├── __init__.py
│   │   │   └── single_source.py       # 単一ソース対応ReRankingRAG
│   │   └── utils/                     # ユーティリティ関数
│   │       ├── __init__.py
│   │       └── text.py                # テキストクリーニング関数
│   └── ui/                            # ユーザーインターフェース
│       ├── __init__.py
│       ├── terminal.py                # メインクラス（RAGTerminalUI）
│       ├── ui_builder.py              # UI構築（ウィジェットの作成と配置）
│       ├── message_handler.py         # メッセージ表示（システム/ユーザー/アシスタント/エラー）
│       ├── event_handler.py           # イベントハンドラー（キーボード入力、メッセージ送信）
│       ├── source_manager.py          # ソース管理（PDF/テキストファイル）
│       └── rag_integration.py         # RAG統合（質問応答処理）
├── scripts/                           # 実行スクリプト
│   └── run_ui.sh                      # UI起動スクリプト
├── examples/                          # サンプルコード
│   ├── chatbot_example.py
│   └── prompt_template_demo.py
├── chroma_db/                         # ベクトルデータベース（自動生成）
├── old/                               # 古いファイル（リファクタリング前のファイルを保持）
├── pdf_rag.py                         # 後方互換性のためのインポートリダイレクト
├── README.md                          # このファイル
└── venv311/                           # 仮想環境
```

### クラス構成

```
src/rag/loaders/pdf.py
└── PDFRagSystem                       # PDFまたはテキストファイルを読み込むクラス
    - import_pdf(pdf_path): PDFファイルを読み込む
    - import_text_file(text_path): テキストファイルを読み込む
    - chunk_size: 1200（デフォルト）
    - chunk_overlap: 200（デフォルト）
    - min_chunk_length: 300（デフォルト）

src/rag/models/single_source.py
└── ReRankingRAG                       # 単一ソース対応の検索と回答生成を行うクラス
    - search(): ハイブリッド検索とリランキング
    - answer(): LLMで回答を生成

src/rag/utils/text.py
└── clean_text()                       # テキストクリーニング関数

src/ui/terminal.py
└── RAGTerminalUI                      # メインクラス（各コンポーネントを統合）

src/ui/ui_builder.py
└── UIBuilder                          # UI構築クラス（ウィジェットの作成と配置）

src/ui/message_handler.py
└── MessageHandler                     # メッセージ表示クラス（チャット表示エリアへの出力）

src/ui/event_handler.py
└── EventHandler                       # イベントハンドラークラス（ユーザー操作の処理）

src/ui/source_manager.py
└── SourceManager                      # ソース管理クラス（PDF/テキストファイルの管理）

src/ui/rag_integration.py
└── RAGIntegration                     # RAG統合クラス（質問応答処理）
```

## インストール

### 必要な環境

- Python 3.11以上
- Ollama（LLM用、llama3:latestモデルが必要）
- Tkinter（UI用、通常はPythonに同梱）

### インストール手順

1. **仮想環境を作成・アクティベート**:
```bash
python3 -m venv venv311
source venv311/bin/activate  # macOS/Linux
# または
venv311\Scripts\activate  # Windows
```

2. **必要なパッケージをインストール**:
```bash
pip install langchain langchain-community langchain-text-splitters sentence-transformers chromadb ollama
```

3. **Ollamaを起動してllama3モデルをダウンロード**:
```bash
ollama pull llama3:latest
```

## 使用方法

### UIを使用した使用方法

#### ターミナルからの実行方法

**方法1: 実行スクリプトを使用（推奨）**

```bash
# プロジェクトディレクトリに移動
cd /Users/yutakoyanagi/simple_rag.py

# 実行スクリプトを実行
./scripts/run_ui.sh
```

**方法2: 手動で仮想環境をアクティベートして実行**

```bash
# プロジェクトディレクトリに移動
cd /Users/yutakoyanagi/simple_rag.py

# 仮想環境をアクティベート
source venv311/bin/activate

# アプリを実行
python -m src.ui.terminal
```

**方法3: ワンライナーで実行**

```bash
cd /Users/yutakoyanagi/simple_rag.py && source venv311/bin/activate && python -m src.ui.terminal
```

#### 実行前の確認事項

1. **Ollamaが起動していることを確認**:
   ```bash
   # 別のターミナルで実行
   ollama serve
   ```

2. **llama3モデルがインストールされていることを確認**:
   ```bash
   # インストール済みモデルを確認
   ollama list
   
   # llama3:latest が表示されない場合はインストール
   ollama pull llama3:latest
   ```

#### UIの操作手順

1. **ファイルの選択**:
   - 「PDF選択」ボタンでPDFファイルを選択
   - または「テキストファイル選択」ボタンでテキストファイルを選択

2. **ファイルの読み込み**:
   - ファイルが自動的に読み込まれ、インデックスが構築されます
   - チャンク数が表示されます

3. **質問応答**:
   - 質問を入力フィールドに入力
   - 「送信」ボタンをクリック、またはEnterキーを押す
   - 回答がチャット表示エリアに表示されます

#### 実行時の出力例

正常に起動すると、以下のようなメッセージが表示されます：

```
仮想環境をアクティベートしました
Pythonパス: /Users/yutakoyanagi/simple_rag.py/venv311/bin/python
アプリを起動しています...
```

その後、Tkinterのウィンドウが開きます。

### プログラムから使用する方法

```python
from src.rag import PDFRagSystem, ReRankingRAG
from langchain.prompts import PromptTemplate

# PDFRagSystemを初期化（chunk_size=1200, chunk_overlap=200）
pdf_rag = PDFRagSystem(
    persist_dir="./chroma_db",
    chunk_size=1200,
    chunk_overlap=200,
    min_chunk_length=300
)

# PDFファイルを読み込む（自動的にインデックスも構築される）
pdf_rag.import_pdf("document.pdf")

# または、テキストファイルを読み込む
# pdf_rag.import_text_file("notes.txt")

# ReRankingRAGシステムを初期化
rag_system = ReRankingRAG(
    docs=pdf_rag.docs,
    persist_dir=pdf_rag.persist_dir
)

# プロンプトテンプレートを設定
template = """あなたは日本語の質問応答システムです。以下の文脈から質問に答えてください。
【文脈】
{context}
【質問】
{question}
【回答の際の注意点】
・文脈に書かれている事実のみを使用する
・推測や一般知識を混ぜない
・答えられない場合は正直にその旨を伝える
・丁寧で分かりやすい日本語で回答する
【回答】"""

rag_system.prompt_template = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# 質問に回答
question = "この文書の主な内容は何ですか？"
answer = rag_system.answer(question, k=5, w_sem=0.5, w_key=0.5, candidate_k=60)
print(answer)
```

## 処理フロー

### データフロー

```
ユーザー入力
    ↓
[UI] ファイル選択（PDFまたはテキストファイル）
    ↓
[PDFRagSystem] ファイル読み込み・チャンク化（chunk_size=1200, chunk_overlap=200）
    ↓
[PDFRagSystem] インデックス構築（BM25 + ベクトルDB）
    ↓
[UI] ユーザーが質問を入力
    ↓
[ReRankingRAG] ハイブリッド検索（Semantic + Keyword）
    ↓
[ReRankingRAG] リランキング（CrossEncoder）
    ↓
[ReRankingRAG] LLMで回答生成
    ↓
[UI] 回答を表示
```

### フェーズ1: ファイルの読み込み

#### PDFファイルの読み込み

1. **ユーザー操作**: 「PDF選択」ボタンをクリック
2. **ファイル選択**: ファイル選択ダイアログでPDFファイルを選択
3. **PDF読み込み処理**:
   - `PyPDFLoader`でPDFを読み込む（ページごとに分割）
   - `RecursiveCharacterTextSplitter`でチャンクに分割（chunk_size=1200, chunk_overlap=200）
   - 短すぎるチャンク（300文字未満）を除外
   - 各チャンクにmetadataを付与
   - BM25検索器を構築（キーワード検索用）
   - Chroma DBを生成（意味検索用のベクトルDB）

#### テキストファイルの読み込み

1. **ユーザー操作**: 「テキストファイル選択」ボタンをクリック
2. **ファイル選択**: ファイル選択ダイアログでテキストファイルを選択
3. **テキスト読み込み処理**:
   - ファイルをUTF-8で読み込む（失敗した場合はShift_JISを試す）
   - `RecursiveCharacterTextSplitter`でチャンクに分割（chunk_size=1200, chunk_overlap=200）
   - 短すぎるチャンク（300文字未満）を除外
   - 各チャンクにmetadataを付与
   - BM25検索器を構築（キーワード検索用）
   - Chroma DBを生成（意味検索用のベクトルDB）

### フェーズ2: 質問応答

1. **質問の送信**:
   - ユーザーが質問を入力フィールドに入力
   - 「送信」ボタンをクリック、またはEnterキーを押す

2. **検索処理**:
   - **ハイブリッド検索**: Semantic検索とKeyword検索を組み合わせ（重みはUIで調整可能）
   - **リランキング**: CrossEncoderを使用して検索結果を再ランキング（精度向上）
   - 上位5件のチャンクを取得

3. **回答生成**:
   - 検索結果を文脈として、プロンプトテンプレートを適用
   - LLM（Ollama llama3:latest）にプロンプトを送信
   - 生成された回答をチャット表示エリアに表示

## チャンク設定

### デフォルト設定

- **chunk_size**: 1200文字（1つのチャンクの最大文字数）
- **chunk_overlap**: 200文字（チャンク間の重複文字数）
- **min_chunk_length**: 300文字（これより短いチャンクは除外）

### チャンク設定の変更方法

PDFRagSystemの初期化時に指定できます：

```python
from src.rag import PDFRagSystem

# カスタムチャンク設定でPDFRagSystemを初期化
pdf_rag = PDFRagSystem(
    persist_dir="./chroma_db",
    chunk_size=1500,        # チャンクサイズを1500文字に変更
    chunk_overlap=250,      # オーバーラップを250文字に変更
    min_chunk_length=400    # 最小チャンク長を400文字に変更
)
```

### チャンク設定の推奨値

| 用途 | chunk_size | chunk_overlap | 説明 |
|------|-----------|---------------|------|
| 標準（デフォルト） | 1200 | 200 | 一般的な文書用（推奨） |
| 長い文書 | 1500-2000 | 250-300 | 技術文書や長文書用 |
| 短い文書 | 800-1000 | 150-200 | 短い文書やメモ用 |
| 高精度 | 600-800 | 100-150 | より細かく分割して精度を上げる |

### 設定の影響

- **chunk_sizeが大きい**: 各チャンクに多くの情報を含むが、検索精度が下がる可能性
- **chunk_sizeが小さい**: 検索精度が上がるが、文脈が分断される可能性
- **chunk_overlapが大きい**: チャンク間の連続性が保たれるが、重複が増える
- **min_chunk_lengthが大きい**: 短いチャンクが除外され、チャンク数が減る

## 技術詳細

### 使用技術

- **LangChain**: ドキュメント処理とRAGパイプライン構築
- **Chroma**: ベクトルデータベース（意味検索用）
- **BM25**: キーワード検索アルゴリズム
- **sentence-transformers**: セマンティック検索用の埋め込みモデル（all-MiniLM-L6-v2）
- **CrossEncoder**: リランキング用モデル（ms-marco-MiniLM-L-6-v2）
- **Ollama**: LLMの実行環境（llama3:latest）

### 検索方法

1. **Semantic検索（意味検索）**:
   - 質問と文書をベクトル化して、コサイン類似度で検索
   - 意味的に類似した文書を取得

2. **Keyword検索（キーワード検索）**:
   - BM25アルゴリズムを使用
   - キーワードマッチングで検索

3. **ハイブリッド検索**:
   - Semantic検索とKeyword検索の結果を重み付きで結合
   - 重みはUIで調整可能（デフォルト: Semantic=0.5, Keyword=0.5）

4. **リランキング**:
   - CrossEncoderを使用して検索結果を再ランキング
   - 質問と各チャンクの関連性を再評価して精度を向上

## トラブルシューティング

### よくある問題

1. **Ollamaが起動していない**:
   - エラー: `Connection refused` または `Ollama is not running`
   - 解決方法: `ollama serve` を実行してOllamaを起動

2. **llama3モデルがインストールされていない**:
   - エラー: `model 'llama3:latest' not found`
   - 解決方法: `ollama pull llama3:latest` を実行

3. **Tkinterが利用できない**:
   - エラー: `No module named '_tkinter'`
   - 解決方法: システムのPythonを使用するか、Tkinterをインストール

4. **メモリ不足**:
   - エラー: `Out of memory` または `Killed`
   - 解決方法: chunk_sizeを小さくするか、より小さなファイルを使用

## ライセンス

このプロジェクトのライセンス情報は、プロジェクトのルートディレクトリにあるLICENSEファイルを参照してください。

#!/bin/bash
# RAG Terminal UI 実行スクリプト
# 仮想環境をアクティベートしてアプリを実行

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

# 仮想環境をアクティベート
if [ -f "venv311/bin/activate" ]; then
    source venv311/bin/activate
    echo "仮想環境をアクティベートしました"
else
    echo "エラー: venv311/bin/activate が見つかりません"
    exit 1
fi

# Pythonのパスを確認
if ! command -v python &> /dev/null; then
    echo "エラー: Pythonが見つかりません"
    exit 1
fi

echo "Pythonパス: $(which python)"
echo "アプリを起動しています..."

# 仮想環境のPythonで実行
python -m src.ui.terminal


#!/bin/bash

echo "🧹 VSCode のアンインストールを開始します..."

# アプリ本体を削除
if [ -d "/Applications/Visual Studio Code.app" ]; then
    echo "📦 VSCodeアプリケーションを削除中..."
    sudo rm -rf "/Applications/Visual Studio Code.app"
fi

# 設定・拡張・キャッシュなどを削除
echo "🗑️ 設定ファイルとキャッシュを削除中..."
rm -rf ~/Library/Application\ Support/Code
rm -rf ~/.vscode
rm -rf ~/Library/Caches/com.microsoft.VSCode
rm -rf ~/Library/Saved\ Application\ State/com.microsoft.VSCode.savedState
rm -rf ~/Library/Preferences/com.microsoft.VSCode.plist

# ゴミ箱内のVSCode関連ファイル削除
echo "🗑️ ゴミ箱内のVSCode関連ファイルを削除中..."
find ~/.Trash -name "*VSCode*" -exec rm -rf {} +

# プロジェクト内 .vscode フォルダがある場合の削除
if [ -d ".vscode" ]; then
    echo "⚠️ 警告: プロジェクト内に.vscodeフォルダが存在します"
    echo "🗑️ .vscodeフォルダを削除します..."
    rm -rf .vscode
fi

echo "✅ VSCode の完全アンインストールが完了しました！" 
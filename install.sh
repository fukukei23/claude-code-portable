#!/bin/bash
# Claude Code Portable - 息子PCセットアップスクリプト
# 実行場所: 息子PC（WSL2 Ubuntu）
# 使用方法: bash install.sh

set -e

echo "=============================================="
echo "  Claude Code Portable セットアップ"
echo "=============================================="
echo ""

# 1. 前提チェック
echo "🔍 前提チェック中..."

if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code CLI がインストールされていません"
    echo ""
    echo "以下のコマンドでインストールしてください:"
    echo "  curl -fsSL https://cli.claude.ai/install.sh | bash"
    echo ""
    echo "インストール後、このスクリプトを再実行してください。"
    exit 1
fi

echo "✅ Claude Code CLI: インストール済み"

if ! command -v git &> /dev/null; then
    echo "❌ Git がインストールされていません"
    echo ""
    echo "以下のコマンドでインストールしてください:"
    echo "  sudo apt update && sudo apt install -y git"
    exit 1
fi

echo "✅ Git: インストール済み"
echo ""

# 2. 対話入力
echo "=============================================="
echo "  設定情報の入力"
echo "=============================================="
echo ""

read -p "ユーザー名 (例: musuko): " USERNAME
while [ -z "$USERNAME" ]; do
    echo "⚠️ ユーザー名は必須です"
    read -p "ユーザー名 (例: musuko): " USERNAME
done

echo ""
read -sp "MiniMax API KEY: " MINIMAX_KEY
echo ""
while [ -z "$MINIMAX_KEY" ]; do
    echo "⚠️ API KEYは必須です"
    read -sp "MiniMax API KEY: " MINIMAX_KEY
    echo ""
done

echo ""
read -p "メールアドレス (send-emailスキル用・スキップ可能): " EMAIL
EMAIL=${EMAIL:-""}

echo ""
read -sp "Gmail SMTP パスワード (スキップ可能・空Enter): " SMTP_PASS
echo ""

echo ""
echo "=============================================="
echo "  セットアップ開始"
echo "=============================================="
echo ""

# 3. ディレクトリ作成
echo "📁 ディレクトリ作成中..."
mkdir -p "$HOME/.claude"
mkdir -p "$HOME/bin"
mkdir -p "$HOME/projects"
echo "✅ ディレクトリ作成完了"

# 4. ファイル配置
echo "📦 設定ファイルをコピー中..."
if [ -d "config/claude" ]; then
    cp -r config/claude/* "$HOME/.claude/"
    echo "✅ .claude/ 配下にコピー完了"
else
    echo "⚠️ config/claude/ が見つかりません"
    exit 1
fi

if [ -d "config/bin" ]; then
    cp -r config/bin/* "$HOME/bin/" 2>/dev/null || true
    echo "✅ bin/ 配下にコピー完了"
fi

# 5. プレースホルダー置換
echo "🔄 プレースホルダーを置換中..."
find "$HOME/.claude" -type f 2>/dev/null | while read -r file; do
    # ユーザー名置換
    sed -i "s/__USERNAME__/$USERNAME/g" "$file" 2>/dev/null || true
done

# 6. secrets.env 生成
echo "🔐 secrets.env を生成中..."
cat > "$HOME/.secrets.env" << EOF
export MINIMAX_API_KEY=$MINIMAX_KEY
EOF

if [ -n "$EMAIL" ]; then
    echo "export YOUR_EMAIL=$EMAIL" >> "$HOME/.secrets.env"
fi

if [ -n "$SMTP_PASS" ]; then
    echo "export GMAIL_SMTP_PASSWORD=$SMTP_PASS" >> "$HOME/.secrets.env"
    echo "export GMAIL_SMTP_USER=$EMAIL" >> "$HOME/.secrets.env"
fi

echo "✅ secrets.env 生成完了"

# 7. SSOTテンプレート配置
if [ ! -d "$HOME/projects/obsidian-ssot" ]; then
    echo "📝 Obsidian Vault を初期化中..."
    cp -r ssot-template "$HOME/projects/obsidian-ssot"
    cd "$HOME/projects/obsidian-ssot"
    git init
    git add .
    git commit -m "Initial commit - Claude Code Portable"
    echo "✅ Obsidian Vault 初期化完了"
else
    echo "⚠️ obsidian-ssot は既に存在します"
    if [ ! -f "$HOME/projects/obsidian-ssot/00_SYSTEM/README.md" ]; then
        read -p "Vault内にREADMEがありません。ssot-templateで上書きしますか？(y/N): " OVERWRITE
        if [ "$OVERWRITE" = "y" ] || [ "$OVERWRITE" = "Y" ]; then
            cp -r ssot-template/* "$HOME/projects/obsidian-ssot/"
            echo "✅ README付きテンプレートをコピーしました"
        else
            echo "⏭️ スキップ"
        fi
    else
        echo "⏭️ README済みのためスキップ"
    fi
fi

# 8. settings.json更新（MiniMax直結設定）
echo "⚙️ settings.json を更新中..."
SETTINGS_FILE="$HOME/.claude/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    # settings.local.json を作成して MiniMax 設定を記述
    cat > "$HOME/.claude/settings.local.json" << EOF
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic"
  }
}
EOF
    echo "✅ MiniMax 直結設定を追加"
fi

echo ""
echo "=============================================="
echo "  動作確認"
echo "=============================================="
echo ""

# 9. 動作確認
echo "Claude Code CLI バージョン確認..."
claude --version || echo "⚠️ Claude 起動テスト失敗（claude loginが必要な場合があります）"

echo ""
echo "=============================================="
echo ""
echo "✅ セットアップ完了！"
echo ""
echo "次のステップ:"
echo "1. claude login （初回のみ）"
echo "2. claude （Claude Code起動）"
echo ""
echo "Obsidian Vault: $HOME/projects/obsidian-ssot/"
echo ""
echo "=============================================="

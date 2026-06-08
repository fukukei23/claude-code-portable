# Claude Code Portable

息子のPC用 Claude Code セットアップパッケージ

## 構成

```
claude-code-portable/
├── config/
│   ├── claude/          # .claude/ 設定ファイル一式
│   │   ├── CLAUDE.md    # グローバル命令
│   │   ├── settings.json
│   │   ├── settings.local.json
│   │   ├── skills/      # スキル一式
│   │   ├── scripts/     # ユーティリティスクリプト
│   │   └── memory/      # Memory Index
│   └── bin/             # ~/bin/ ユーティリティ
├── ssot-template/       # 空のObsidian Vaultテンプレート
│   ├── 00_SYSTEM/
│   ├── 01_DECISIONS/
│   ├── 10_DAILY/
│   ├── 20_PUBLISHING/
│   ├── 30_RESEARCH/
│   ├── 40_CAREER/
│   └── 99_ARCHIVE/
├── create-package.sh    # パッケージ生成スクリプト（配布元用）
├── install.sh           # セットアップスクリプト（配布先用）
└── README.md           # このファイル
```

## 使い方

### 配布先（息子PC）での手順

1. このディレクトリをUSBまたはGitHubからコピー
2. `bash install.sh` を実行
3. 質問に従って入力:
   - ユーザー名（例: musuko）
   - MiniMax API KEY
   - メールアドレス
4. `claude` で動作確認

## 前提条件

- WSL2 + Ubuntu
- Claude Code CLI (`curl -fsSL https://cli.claude.ai/install.sh | bash`)
- Git

## マスクされている情報

- メールアドレス → `__YOUR_EMAIL__`, `__DEST_EMAIL__`
- ユーザー名 → `__USERNAME__`
- APIキー → `__MINIMAX_API_KEY__`, `__GMAIL_SMTP_USER__`, `__ZAI_API_KEY__`
- パス → `/home/__USERNAME__/`

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| Claude 起動しない | `claude login` を実行 |
| APIエラー | API KEYが正しく入力されているか確認 |
| 文字化け | `sudo apt install -y fonts-noto-cjk` |

## ライセンス

個人使用限定。obsidian-ssot はパブリック化禁止。

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
├── ssot-template/       # Obsidian Vault 雛形（各フォルダにREADME付き）
│   ├── 00_SYSTEM/       # 運用ルール・全体マップ・バックログ
│   ├── 01_DECISIONS/    # 技術判断・設計決定（ADR）
│   ├── 10_DAILY/        # 日々の作業ログ
│   ├── 20_PUBLISHING/   # Zenn・ブログ記事ドラフト
│   ├── 30_RESEARCH/     # 調査・研究メモ
│   ├── 40_CAREER/       # 就職活動・キャリア関連
│   └── 99_ARCHIVE/      # 完了・不要ファイル保管庫
├── install.sh           # セットアップスクリプト
└── README.md            # このファイル
```

## 使い方

### 息子PCでの手順

1. このディレクトリをGitHubからclone
   ```bash
   git clone https://github.com/fukukei23/claude-code-portable.git
   cd claude-code-portable
   ```
2. `bash install.sh` を実行
3. 質問に従って入力:
   - ユーザー名（例: musuko）
   - MiniMax API KEY
   - メールアドレス（空Enterでスキップ可）
4. `claude login` で認証（初回のみ）
5. `claude` で起動確認

## 前提条件

- WSL2 + Ubuntu
- Claude Code CLI (`curl -fsSL https://cli.claude.ai/install.sh | bash`)
- Git

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| Claude 起動しない | `claude login` を実行 |
| APIエラー | API KEYが正しく入力されているか確認 |
| 文字化け | `sudo apt install -y fonts-noto-cjk` |

## ライセンス

個人使用限定。obsidian-ssot はパブリック化禁止。

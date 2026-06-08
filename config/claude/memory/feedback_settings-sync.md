---
name: settings-sync
description: Claude Code設定変更時にSSOTの対応ファイルも必ず同時更新するルール
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2ba6c476-1586-42f1-92a2-3a98623cf086
---

## 設定変更時のSSOT同期ルール

**Why:** 設定ファイルだけ変更してSSOT側が古いままになると、次セッションで差分が生じる。

**How to apply:**
- `~/.claude/settings.json` や `settings.local.json` を変更したら、`01_DECISIONS/claude-code/config/` のコピーも同時更新
- Hooks（SessionStart, PreToolUse等）を変更したら、`00_SYSTEM/自動化.md` の状態・履歴も更新
- MCPサーバー設定を変更したら、`00_SYSTEM/MCPツール使い分けガイド.md` も更新

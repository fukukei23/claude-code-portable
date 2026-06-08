---
name: playwright-disable-note
description: デスクトップアプリMCP 223.8k問題の調査記録（全て復旧済み）
metadata: 
  node_type: memory
  type: project
  originSessionId: eb341d04-9abd-449c-a285-1921baf2ba86
---

## デスクトップアプリ MCP tools 223.8k 問題（2026-05-20）

### 結論
**デスクトップアプリ（Claude Code Desktop）の223.8k MCP toolsはユーザー設定では制御不可。**
6回の設定変更（MCP server削除、profiles無効化、plugin cache削除、marketplace削除、installed_plugins削除）で全て223.8k固定。
CLIでは同一構成で16.3k。デスクトップアプリ内部のツール定義シリアライズ差異と推定。

### 実施した変更（全て復旧済み）
1. ✅ sync-secrets-to-settings.sh から5サーバーのjq同期を削除（linear, sentry, supabase, tavily, stripe）
2. ✅ settings.json から5サーバーを削除（9→4）
3. ✅ MCP profiles一時無効化→復旧
4. ✅ plugin cache一時無効化→復旧
5. ✅ Windows marketplaces一時無効化→復旧
6. ✅ playwright + claude-mem一時無効化→復旧

### 有効だった修正
- **sync-secrets-to-settings.sh**: 5サーバーの再生成を防止（これはCLI側でも有効）
- **settings.json 5サーバー削除**: CLI側でコンテキスト削減に有効

### 効かなかった修正
- デスクトップアプリの223.8k表示は一切変動なし

### 回避策
- WSL CLI版を使用（53.1k/200k = 27%で正常動作）
- デスクトップアプリはAnthropicのアップデート待ち

### Why: デスクトップアプリが会話開始できない（コンテキストオーバー）
### How to apply: CLI版をメインで使用。デスクトップアプリは最新版へのアップデートを確認

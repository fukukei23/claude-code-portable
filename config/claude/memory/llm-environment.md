---
name: llm-environment
description: WSL CLI版とWindows Desktop版のLLM・MCP構成の違い。外部LLM呼び出しの可否判断に必要
metadata: 
  node_type: memory
  type: project
  originSessionId: 57e57ac2-3b67-4674-a9f6-b272e91c5411
---

# WSL CLI版のLLM環境構成

## 基本原則
**WSL CLI版はセッション自体がGLM-5.1で動作している。自分自身がLLMなので、外部LLMコマンド（glm_ask等）は存在しないし呼び出し不要。**

## MCP構成の違い

| 項目 | WSL CLI版 | Windows Desktop版 |
|------|-----------|-------------------|
| 動作LLM | GLM-5.1（glm-rate-proxy経由） | Sonnet/Opus（Anthropic直） |
| glm MCP | 設定あるがツール未接続・不要 | 利用可能 |
| minimax MCP | 設定あるがツール未接続 | 利用可能（明示的呼び出し用） |
| フォールバック | GLM不可時→MiniMax（自動） | 不要 |

## 具体的な注意
- スキルに「LLMに問い合わせる」とあっても、bashで`glm_ask`を叩くのは**間違い**
- 分類判定や分析は**自分自身（GLM）で直接実行**する
- MiniMaxを明示的に使いたい場合はユーザー指示が必要
- この知識はスキル作成・修正時にも参照すること

## 関連
- [[glm-rate-proxy]] — ローカルプロキシのトラブルシューティング
- CLAUDE.md「LLM利用ポリシー」— 全体ルール

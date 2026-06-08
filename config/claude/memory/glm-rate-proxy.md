---
name: glm-rate-proxy
description: ZAI API 429対策ローカルプロキシのステータス確認・モデル判別・トラブルシューティング
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8f9c4605-dcd2-4897-b03e-ec9219806df3
---

# GLM Rate Proxy

## 場所
- プロキシ本体: `~/.claude/scripts/glm-rate-proxy/`
- 起動スクリプト: `~/.claude/scripts/start-glm-proxy.sh`（SessionStart hook）
- ログ: `/tmp/glm-proxy.log`
- 設定: `~/.config/glm-rate-proxy/config.json`

## 現在のLLMモデル確認方法

1. **プロキシ経由かの確認**: `echo $ANTHROPIC_BASE_URL`
   - `http://127.0.0.1:8787` → プロキシ経由（ピーク時間はMiniMax）
   - `https://api.z.ai/...` → ZAI直結（常にGLM-5.1）
2. **プロキシのルーティング先**: `curl -s http://127.0.0.1:8787/proxy/status | python3 -m json.tool`
3. **システムプロンプトの表記**: `You are powered by the model GLM-5.1` — 起動時固定のため実際のルーティング先と一致しない場合がある

**注意**: `/status` は404。正しくは `/proxy/status`

## ステータスフィールド

| フィールド | 意味 |
|---|---|
| mode | normal / peak_block / usage_block |
| provider | 現在のルーティング先（zai / minimax） |
| peak_block | ピーク時間帯ブロックが有効か |
| request_count | プロキシ経由のリクエスト数（0=未使用＝バイパス中） |
| usage_pct | 使用量割合 |

## プロキシバイパス問題（2026-05-29 解決済み）

- **症状**: プロキシ起動済みでも request_count=0
- **根本原因**: `sync-secrets-to-settings.sh` が `.secrets.env` の直結URLで settings.json を上書き → .bashrcのexport env varが無視される
- **解決策**: `sync-secrets-to-settings.sh` の `source` 直後にプロキシ生存チェックを追加（2026-05-29）
  - プロキシ生存 → `ANTHROPIC_BASE_URL` を `http://127.0.0.1:8787` に上書き
  - プロキシ死亡 → `.secrets.env` の直結URLをそのまま使用（安全なフォールバック）
- **安全性**: プロキシ死亡時は自動的にGLM直結にフォールバック。セッション起動のたびに再判定

## セッション途中のプロキシ死亡時の対処

**症状**: セッション中で突然API接続エラー（例: "Connection refused", "timeout"）

**対処手順**:

1. **焦らず待つ**: 最初の数秒は-network-retry期待で自動リトライ
2. **手動再起動**:
   ```bash
   pkill -f glm_rate_proxy; sleep 1
   cd ~/.claude/scripts/glm-rate-proxy && PYTHONPATH=src nohup python3 -m glm_rate_proxy > /tmp/glm-proxy.log 2>&1 &
   sleep 2
   curl -sf http://127.0.0.1:8787/proxy/status
   ```
3. **確認**: `curl -s http://127.0.0.1:8787/proxy/status | python3 -m json.tool`
4. **接続確認**: 少し待ってから会話恢复
5. **起動しない場合**: ログ確認 `tail /tmp/glm-proxy.log`
   - ポート競合 → `lsof -i :8787` で確認
   - ImportError → `pip3 install aiohttp` 等

## トラブルシューティング

### プロキシが起動しない
1. `cat /tmp/glm-proxy.log` でログ確認
2. `pgrep -f "python3 -m glm_rate_proxy"` でプロセス確認
3. `PYTHONPATH=src python3 -m glm_rate_proxy` で手動起動してエラー確認
4. 起動失敗時は settings.json が ZAI 直結 URL に自動フォールバック

### settings.json の URL がプロキシに向かない
- Hook実行順序: sync-secrets-to-settings.sh → start-glm-proxy.sh
- start-glm-proxy.sh が最後に ANTHROPIC_BASE_URL を設定する設計
- 順序が逆だと sync が上書きしてしまう

### 429 が解消しない
1. プロキシが生きてるか: `curl -sf http://127.0.0.1:8787/proxy/status`
2. 使用率確認: status レスポンスの usage フィールド
3. 5時間ウィンドウリセット待ち（Max: 1,600 prompts / 5h）

### プロキシ経由で変なエラー
- gzip 関連: upstream.py が accept-encoding: identity を送信 + gzip フォールバック付き
- "Server disconnected": urllib.request 経由（aiohttp ClientSession は使用しない）

## アーキテクチャ概要
- Claude Code → localhost:8787 → ZAI API / MiniMax API
- 使用率 <80%: GLM-5.1, 80-95%: GLM-4.7, >95%: GLM-4.7-Flash（無料）
- ピーク時間帯（13-19時）: 強制的にMiniMaxにルーティング
- 429時: GLM-4.7-Flash → MiniMax M2.7 → 503
- **⑦エラー時（2026-05-29追加）**: 429/500/502/タイムアウト/接続エラー → MiniMax M2.7に自動切替

## ⑦全エラー時MiniMaxフォールバック（2026-05-29追加）

| エラー種類 | 動作 |
|---|---|
| 429（レートリミット） | GLM-4.7 → MiniMax |
| 500/502/503（サーバーエラー） | → MiniMax |
| タイムアウト（1200s） | → MiniMax |
| 接続エラー | → MiniMax |
| MiniMaxもエラー | 503返す |

**フォールバックチェーン全景**:
```
①正常 → ZAI(GLM-5.1)
②ピーク時間帯(13-19時) → MiniMax
③429エラー → GLM-4.7 → MiniMax
④その他エラー(500/502/タイムアウト等) → MiniMax【NEW】
⑤MiniMax死亡 → 503返す
```

**コード変更**: `proxy.py` に `_handle_upstream_error` メソッド追加（2026-05-29）

## 実際のモデル名キャプチャ（2026-05-29追加）

- ステータスAPIに `last_actual_model` フィールドを追加
- ZAI/MiniMaxのAPIレスポンスに含まれる `model` フィールド（例: `"glm-5.1"`, `"MiniMax-M2.7"`）を自動キャプチャ
- 正常系・429フォールバック・エラーフォールバック全経路でキャプチャ
- プロキシ再起動で null にリセット（永続なし）
- 確認: `curl -s http://127.0.0.1:8787/proxy/status | python3 -m json.tool` → `last_actual_model` を確認

## コンテキストリミット時のフォールバック限界（2026-06-05 判明）

**症状**: コンテキストが長すぎると「context window limit」エラーになり、MiniMaxフォールバックも発動しない

**原因**: Claude Code本体が**APIリクエストを送る前に**コンテキスト長を判定してエラーを出す。プロキシにリクエストが届かないため、フォールバックのしようがない。

**ログで確認**: プロキシログにエラーが1行も出ていない（全て200 OK）。つまりエラーはプロキシ外で発生。

**対策**:
- コンテキストが長くなったら早めに `/compact` する
- `/compact` も失敗する場合は `/new-session` で切り替え
- この問題はプロキシ側では解決不可（Claude Code本体の仕様）

**注意**: コンテキストリミットで `/compact` も死ぬのは「鶏と卵」問題。圧縮要求自体がコンテキスト上限を超えるため。

## 関連
- 詳細ドキュメント: `obsidian-ssot/01_DECISIONS/claude-code/2026-05-28_ピークブロック不具合修正.md`
- 設定ファイル同期: [[feedback_settings-sync]]

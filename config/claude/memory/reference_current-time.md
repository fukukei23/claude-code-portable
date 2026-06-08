---
name: current-time-check
description: 時刻を確認するたびに date コマンドで現在時刻を取得。ピーク時間帯（13-19時）はMiniMax、それ以外はGLM-5.1
metadata: 
  node_type: memory
  type: reference
  originSessionId: 89014130-79d9-4572-90a0-3bd76d32b015
---

# 現在時刻の確認

## 確認コマンド
```bash
date "+%Y-%m-%d %H:%M:%S"
```

## LLM切替ルール
| 時間帯 | モデル |
|--------|--------|
| 13:00〜19:00（ピーク） | MiniMax |
| 上記以外 | GLM-5.1 |

## 用途
- LLM切替ガイド確認時
- 「今何モデル？」と質問された時
- 任何時刻確認が有益な場面

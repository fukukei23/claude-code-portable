---
name: teishutsu-skill
description: 「提案して」軽量スキルとbrainstorming重量スキルの2段構え設計
metadata: 
  node_type: memory
  type: project
  originSessionId: 00b715c0-8da8-4497-9043-42b3be856879
---

## 「提案して」スキル体系（2段構え）

1. **「提案して」（軽量・入口）** → 新規カスタムスキル
   - さっと2〜3の選択肢＋推奨案を提示
   - 内容の複雑さで質問の有無を自動調整
   - SSOT記録なし（会話内のみ）
   - トリガー: 「提案して」「提案」「どう思う」「教えて」「アドバイス」等

2. **brainstorming（重量・深掘り）** → 既存 `superpowers:brainstorming`
   - 提案の中から気になるものを設計まで詰める
   - 設計書作成→ユーザー確認→実装計画のフルフロー

**Why:** ユーザーの「提案して」は単なるアイデア出しではなく、現状分析→選択肢→推奨→実装可能な形まで含む複合要求。軽量版で素早く応えつつ、深掘りが必要な時だけ重いフローに移行する。

**How to apply:**
- 「提案して」スキルが推奨案を出した後、「これ深掘りしたい」と言われたらbrainstormingを発動
- brainstorming側の入口としても機能する

[[feedback_proactive-suggestion]]

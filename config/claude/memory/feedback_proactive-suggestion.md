---
name: proactive-suggestion
description: 実装方針決定時にユーザーに聞かれる前にベストプラクティスを先に提案するルール
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2ba6c476-1586-42f1-92a2-3a98623cf086
---

## 自発的提案の義務

**Why:** ユーザーはコードが読めない素人なので、プロの視点から気づくべき点を自分で提案してほしい。

**How to apply:**
- 実装方針を決定する時、ユーザー指示を待たずにベストプラクティス・業界標準を先に提案する
- 対象: UX / アーキテクチャ / テスト / セキュリティ / 性能 すべて
- ソース: `00_SYSTEM/共通ルール/ルール.md`

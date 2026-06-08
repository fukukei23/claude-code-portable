---
name: ブランチ運用規律
description: NexusCore等の個人プロジェクトではfeatureブランチをmainにマージし忘れないようにする指針
type: feedback
originSessionId: 6b753c85-e8d7-4d6c-8f84-b3f26cde890b
---
## ブランチ運用: 個人開発は常にmainで作業する

**Why:** feature/failに18コミットの作業が残り、mainと乖離してマージに多大な手間がかかった。個人開発では並列ブランチの管理コストがメリットを上回る。

**How to apply:**
- NexusCore等の個人プロジェクトは**常にmainで直接コミット・push**
- featureブランチは使わない（CI用の一時ブランチのみ）
- 作業が終わったらその場でpush。セッション終了前に必ずpush確認
- リモートに残った古いfeatureブランチは定期的に削除

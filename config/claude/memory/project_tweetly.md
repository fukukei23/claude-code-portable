---
name: project-tweetly
description: tweetly — X自動化OSSの名残。クローン済みだが未成功、保留中
metadata: 
  node_type: memory
  type: project
  originSessionId: a13a8046-afa8-4f5b-bdf1-14e2105140a8
---

## tweetly（~/projects/tweetly/）

**何**: beydemirfurkan製のX（Twitter）自動化OSS。MCP対応でAIエージェントからツイート投稿・いいね・RT・検索などを自動操作できる。

**現状**: クローンして試したが、**Xのツイート自動化はできなかった**。名残として `~/projects/tweetly/` に置いている。

**なぜ残している**: いつかできるかもしれないから保留。削除はしない。

**技術スタック**: NestJS 11 + Next.js 16 + PostgreSQL + Patchright（ブラウザ自動化）

**あなたのコミット**: なし（他人のリポジトリのクローンのまま）

**リモート**: `https://github.com/beydemirfurkan/tweetly.git`

**フロントエンド起動**: `cd ~/projects/tweetly && HOSTNAME=0.0.0.0 PORT=3020 npm --prefix frontend run dev` → `localhost:3020`

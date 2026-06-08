#!/bin/bash
# SSOT自動バックアップ（Cron用）
# 30分ごとに実行: */30 * * * * /home/__USERNAME__/bin/ssot-auto-sync.sh

REPO="/home/__USERNAME__/projects/obsidian-ssot"
LOG="/tmp/ssot-sync.log"

cd "$REPO" || exit 1

# サブモジュールを最新に更新
git submodule update --remote --merge 50_PROJECTS/ 2>/dev/null

# 先にpull（リモートの変更を取り込む）
git pull --rebase origin main >> "$LOG" 2>&1

# 変更がない場合は終了
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
    exit 0
fi

# commit & push
git add -A
git diff --cached --quiet && exit 0

git -c user.name="__USERNAME__23" -c user.email="__USERNAME__23@users.noreply.github.com" \
  commit -m "Auto backup: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG" 2>&1

git push origin main >> "$LOG" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') synced" >> "$LOG"

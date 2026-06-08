#!/usr/bin/env bash
# archive-backlog-done.sh
# バックログの [x] 行を自動で完了済みセクションに移動する
# Usage: archive-backlog-done.sh [backlog-path]

BACKLOG="${1:-$HOME/projects/obsidian-ssot/00_SYSTEM/バックログ.md}"

if [ ! -f "$BACKLOG" ]; then
    echo "バックログファイルが見つかりません: $BACKLOG"
    exit 1
fi

# [x] 行を含むセクション（P0/P1/P2）から抽出
DONE_LINES=$(awk '
/^## P[012]/ { in_active=1; next }
/^## 完了済み/ { in_active=0; in_done=1; next }
/^## / { in_active=0; in_done=0; next }
in_active && /^\- \[x\]/ { print }
' "$BACKLOG")

if [ -z "$DONE_LINES" ]; then
    echo "移動対象なし（完了済みタスクはありません）"
    exit 0
fi

echo "移動対象:"
echo "$DONE_LINES"
echo ""

# 一時ファイルで処理
TMP=$(mktemp)
awk -v done="$DONE_LINES" '
BEGIN { done_count = split(done, done_arr, "\n") }

/^## 完了済み/ {
    # 完了済みセクションの先頭に移動
    print
    for (i = 1; i <= done_count; i++) {
        if (done_arr[i] != "") print done_arr[i]
    }
    in_done = 1
    next
}

/^## / { in_active = 0; in_done = 0 }

/^## P[012]/ { in_active = 1; next }

in_active && /^\- \[x\]/ { next }  # P0/P1/P2内の[x]行を削除
in_active && /^  / && prev_was_x { next }  # [x]行の次のインデント行も削除

{ print; prev_was_x = 0 }
in_active && /^\- \[x\]/ { prev_was_x = 1 }
' "$BACKLOG" > "$TMP"

# 差分確認
DIFF=$(diff "$BACKLOG" "$TMP")
if [ -z "$DIFF" ]; then
    echo "変更なし"
    rm "$TMP"
    exit 0
fi

mv "$TMP" "$BACKLOG"
echo "完了済みセクションに移動しました"

#!/bin/bash
# claude-config-sync.sh
# ~/.claude/ → obsidian-ssot + claude-config への自動同期
# 呼び出し: SessionStop hook または手動実行

set -euo pipefail

# === パス定義 ===
CLAUDE_DIR="/home/__USERNAME__/.claude"
SSOT_DIR="/home/__USERNAME__/projects/obsidian-ssot/01_DECISIONS/claude-code/設定ファイル"
CONFIG_REPO="/home/__USERNAME__/projects/claude-config"
SANITIZE_SCRIPT="$CLAUDE_DIR/scripts/sanitize-settings.py"
LOG="/tmp/claude-config-sync.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"; }

# === 1. obsidian-ssot へのコピー（そのまま） ===
sync_to_ssot() {
  log "Syncing to obsidian-ssot..."

  cp "$CLAUDE_DIR/CLAUDE.md" "$SSOT_DIR/CLAUDE.md"
  log "  CLAUDE.md → obsidian-ssot OK"

  cp "$CLAUDE_DIR/settings.json" "$SSOT_DIR/settings.json"
  log "  settings.json → obsidian-ssot OK"

  if [ -f "$CLAUDE_DIR/settings.local.json" ]; then
    cp "$CLAUDE_DIR/settings.local.json" "$SSOT_DIR/settings-cli.local.json"
    log "  settings.local.json → obsidian-ssot OK"
  fi
}

# === 2. claude-config へのコピー（シークレット除去） ===
sync_to_config_repo() {
  log "Syncing to claude-config..."

  cp "$CLAUDE_DIR/CLAUDE.md" "$CONFIG_REPO/CLAUDE.md"
  log "  CLAUDE.md → claude-config OK"

  # settings.json → settings.example.json（シークレット除去）
  python3 "$SANITIZE_SCRIPT" "$CLAUDE_DIR/settings.json" "$CONFIG_REPO/settings.example.json"
  log "  settings.json → settings.example.json (sanitized) OK"

  # settings.local.json → settings.local.example.json
  if [ -f "$CLAUDE_DIR/settings.local.json" ]; then
    python3 "$SANITIZE_SCRIPT" "$CLAUDE_DIR/settings.local.json" "$CONFIG_REPO/settings.local.example.json"
    log "  settings.local.json → settings.local.example.json (sanitized) OK"
  fi

  # ディレクトリ同期（plugins/ は除外 — home配下のパス問題あり）
  for dir in skills scripts agents shared-rules workflows scheduled-tasks docs lib; do
    if [ -d "$CLAUDE_DIR/$dir" ]; then
      rsync -a --delete \
        --exclude='*.jsonl' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='node_modules/' \
        --exclude='loop.log' \
        --exclude='state.json' \
        --exclude='home/' \
        "$CLAUDE_DIR/$dir/" "$CONFIG_REPO/$dir/" 2>/dev/null || true
      log "  $dir/ → claude-config OK"
    fi
  done

  # メモリ同期
  if [ -d "$CLAUDE_DIR/memory" ]; then
    rsync -a --delete \
      --exclude='*.jsonl' \
      "$CLAUDE_DIR/memory/" "$CONFIG_REPO/memory/" 2>/dev/null || true
    log "  memory/ → claude-config OK"
  fi
}

# === 3. claude-config の auto commit & push ===
auto_commit_config() {
  cd "$CONFIG_REPO" || return 1

  if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
    log "claude-config: no changes to commit"
    return 0
  fi

  git add -A
  git diff --cached --quiet && return 0

  git -c user.name="__USERNAME__23" -c user.email="__USERNAME__23@users.noreply.github.com" \
    commit -m "Auto sync: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG" 2>&1

  git push origin main >> "$LOG" 2>&1
  log "claude-config: committed and pushed"
}

# === メイン ===
main() {
  log "=== claude-config-sync start ==="

  sync_to_ssot
  sync_to_config_repo
  auto_commit_config

  log "=== claude-config-sync done ==="
}

main "$@"

#!/usr/bin/env python3
"""バックログの自動完了チェック機能.

サブコマンド:
  prompt   - 7日以上経過の未完了タスクを確認プロンプトとして出力
  match    - git履歴と照合して自動で [x] にする
  archive  - 完了済みセクションの2ヶ月以上前タスクをアーカイブ
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# --- パス設定 ---
SSOT_PATH = Path.home() / "projects/obsidian-ssot"
BACKLOG = SSOT_PATH / "00_SYSTEM/バックログ.md"
ARCHIVE_DIR = SSOT_PATH / "99_ARCHIVE"
REPO_INDEX = SSOT_PATH / "00_SYSTEM/repo-index.yaml"
GIT_SINCE_DAYS = 30

# --- プロジェクト→リポジトリ マッピング（フォールバック） ---
HARDCODED_PROJECT_MAP = {
    "NexusCore":           Path.home() / "projects/NexusCore",
    "reserve-optimizer":   Path.home() / "projects/reserve-optimizer",
    "atelier-kyo-manager": Path.home() / "projects/atelier-kyo-manager",
    "atelier":             Path.home() / "projects/atelier-kyo-manager",
    "BUYMA":               Path.home() / "projects/atelier-kyo-manager",
    "openclaw":            Path.home() / "projects/openclaw-workspace",
    "krotam":              Path.home() / "projects/krotam",
    "orchestrix":          Path.home() / "projects/orchestrix",
    "contextforge":        Path.home() / "projects/contextforge",
    "mnp_manager":         Path.home() / "projects/mnp_manager",
    "stit-irg-template":   Path.home() / "projects/stit-irg-template",
    "sentinel-governance": Path.home() / "projects/sentinel-governance",
    "claude-config":       Path.home() / "projects/claude-config",
    "zenn":                Path.home() / "projects/zenn",
    "obsidian-ssot":       SSOT_PATH,
    "tweetly":             Path.home() / "projects/tweetly",
    "python-reading-guide":Path.home() / "projects/python-reading-guide",
    "ssot-guide":          Path.home() / "projects/ssot-guide",
    "claude-code-guide":   Path.home() / "projects/claude-code-guide",
    "claude-cost-optimizer":Path.home() / "projects/claude-cost-optimizer",
}


@dataclass
class Task:
    line_text: str       # "- [ ] タスク名 — 補足（M/D）"
    section: str         # "P0", "P1", "P2"
    date_str: str        # "5/19" など
    keywords: list[str] = field(default_factory=list)
    indent_lines: list[str] = field(default_factory=list)


def load_project_map() -> dict[str, Path]:
    """repo-index.yaml からプロジェクト→リポジトリマッピングを読み込む."""
    mapping = dict(HARDCODED_PROJECT_MAP)
    try:
        if not REPO_INDEX.exists():
            return mapping
        content = REPO_INDEX.read_text(encoding="utf-8")
        for match in re.finditer(r"^  - name: (\S+)$", content, re.MULTILINE):
            name = match.group(1)
            if name not in mapping:
                repo_path = Path.home() / "projects" / name
                if repo_path.exists():
                    mapping[name] = repo_path
    except Exception:
        pass
    return mapping


def parse_backlog() -> list[Task]:
    """バックログをパースして未完了タスクのリストを返す."""
    if not BACKLOG.exists():
        return []
    text = BACKLOG.read_text(encoding="utf-8")
    tasks = []
    current_section = None

    for line in text.split("\n"):
        m = re.match(r"^## P([012]):", line)
        if m:
            current_section = m.group(1)
            continue
        if line.startswith("## 完了済み") or line.startswith("## ["):
            current_section = None
            continue
        if current_section and re.match(r"^\- \[ \]", line):
            date_m = re.search(r"（(\d+/\d+)）", line)
            date_str = date_m.group(1) if date_m else ""
            task = Task(line_text=line, section=current_section, date_str=date_str)
            tasks.append(task)

    return tasks


def extract_project(task_text: str) -> Optional[str]:
    """タスクテキストからプロジェクト名を抽出."""
    # 【v3レビューP0】PROJECT: ... 形式
    m = re.search(r"【[^】]+】\s*(\S+?):", task_text)
    if m:
        return m.group(1)
    # PROJECT: ... 形式
    m = re.search(r"^(\S+?):", task_text)
    if m:
        return m.group(1)
    return None


def extract_keywords(task_text: str) -> list[str]:
    """タスクテキストからgit grep用キーワードを抽出."""
    text = re.sub(r"【[^】]+】", "", task_text)
    text = re.sub(r"^[^—]*—", "—", text)  # プロジェクト名: を除去
    text = re.sub(r"—.*$", "", text)        # — 以降除去
    text = re.sub(r"（[^）]*）", "", text)   # 日付除去

    tokens = re.split(r"[\s/\-_]+", text)
    keywords = [t for t in tokens if len(t) >= 3 and not re.match(r"^[a-zA-Z]+$", t) or (len(t) >= 3 and re.match(r"^[a-zA-Z]", t))]
    # ASCIIトークン優先
    ascii_kw = [k for k in keywords if re.match(r"^[a-zA-Z]", k)]
    non_ascii = [k for k in keywords if not re.match(r"^[a-zA-Z]", k)]
    return ascii_kw + non_ascii


def get_elapsed_days(date_str: str) -> Optional[int]:
    """date_str (M/D) から経過日数を計算."""
    if not date_str:
        return None
    m = re.match(r"(\d+)/(\d+)", date_str)
    if not m:
        return None
    month, day = int(m.group(1)), int(m.group(2))
    try:
        done_date = datetime(datetime.now().year, month, day)
        if done_date > datetime.now():
            done_date = datetime(datetime.now().year - 1, month, day)
        return (datetime.now() - done_date).days
    except ValueError:
        return None


def git_search(repo_path: Path, keywords: list[str]) -> Optional[str]:
    """リポジトリのgit logからキーワードを検索."""
    since = (datetime.now() - timedelta(days=GIT_SINCE_DAYS)).strftime("%Y-%m-%d")
    for kw in keywords[:3]:
        if len(kw) < 3:
            continue
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "log", "--oneline", f"--since={since}", f"--grep={kw}", "-3"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split("\n")[0]
        except Exception:
            pass
    return None


# =============================================================================
# prompt サブコマンド
# =============================================================================
def cmd_prompt() -> int:
    """7日以上経過の未完了タスクを確認プロンプトとして出力."""
    tasks = parse_backlog()
    if not tasks:
        return 0

    stale = []
    for task in tasks:
        days = get_elapsed_days(task.date_str)
        if days is not None and days >= 7:
            stale.append((task, days))

    if not stale:
        return 0

    out = ["<system-reminder>", "[バックログ確認依頼]", "以下の未完了タスクが7日以上経過しています：", ""]
    current_section = None
    for task, days in stale:
        if task.section != current_section:
            out.append(f"**P{task.section}**")
            current_section = task.section
        # タスク名のみ抽出
        name = re.sub(r"^\- \[ \]", "", task.line_text).strip()
        name = re.sub(r"—.*$", "", name).strip()
        out.append(f"  ⚠ 「{name}」— {days}日経過（{task.date_str}〜）")
    out.append("")
    out.append("ユーザーに状況を確認し、完了ならチェックしてください。")
    out.append("</system-reminder>")

    print("\n".join(out))
    return 0


# =============================================================================
# match サブコマンド
# =============================================================================
def mark_as_done(task_line: str, match_info: str) -> bool:
    """バックログのタスクを [x] に変更."""
    if not BACKLOG.exists():
        return False
    text = BACKLOG.read_text(encoding="utf-8")
    new_line = task_line.replace("- [ ]", "- [x]", 1)
    # 既に [x] なら何もしない
    if new_line == task_line:
        return False
    if new_line not in text:
        return False
    new_text = text.replace(new_line, new_line.rstrip() + f" — {match_info}", 1)
    BACKLOG.write_text(new_text, encoding="utf-8")
    return True


def cmd_match() -> int:
    """git履歴と照合して自動で [x] にする."""
    tasks = parse_backlog()
    project_map = load_project_map()

    done_count = 0
    for task in tasks:
        project = extract_project(task.line_text)
        if not project or project not in project_map:
            continue
        repo_path = project_map[project]
        if not repo_path.exists():
            continue
        keywords = extract_keywords(task.line_text)
        if not keywords:
            continue
        match = git_search(repo_path, keywords)
        if match:
            if mark_as_done(task.line_text, f"git一致: {match}"):
                print(f"✅ 自動完了: {task.line_text[:60]}... → {match}")
                done_count += 1

    if done_count == 0:
        print("自動完了の候補なし（全タスク未実施、または一致なし）")
    else:
        print(f"\n📋 {done_count}件を自動完了しました。PostToolUse hookが完了済みセクションに移動します。")
    return 0


# =============================================================================
# archive サブコマンド
# =============================================================================
def parse_done_date(line: str) -> Optional[datetime]:
    """完了済みタスクの日付をパース."""
    patterns = [
        (r"（(\d{4})-(\d{2})-(\d{2})", "%Y-%m-%d"),
        (r"(\d+)/(\d+)日?", None),
    ]
    for pat, fmt in patterns:
        m = re.search(pat, line)
        if m:
            if fmt:
                try:
                    return datetime.strptime(m.group(0), fmt)
                except ValueError:
                    pass
            else:
                try:
                    month, day = int(m.group(1)), int(m.group(2))
                    return datetime(datetime.now().year, month, day)
                except ValueError:
                    pass
    return None


def cmd_archive() -> int:
    """完了済みセクションの2ヶ月以上前タスクをアーカイブ."""
    if not BACKLOG.exists():
        return 0
    text = BACKLOG.read_text(encoding="utf-8")

    # 完了済みセクションを抽出
    m = re.search(r"(## 完了済み\n)(.*)", text, re.DOTALL)
    if not m:
        print("完了済みセクションなし")
        return 0

    done_section = m.group(2)
    lines = done_section.split("\n")

    archive_items = []
    remaining = []
    for line in lines:
        if re.match(r"^- \[x\]", line):
            date = parse_done_date(line)
            if date and (datetime.now() - date).days > 60:
                archive_items.append(line)
            else:
                remaining.append(line)
        elif line.startswith("## "):
            remaining.append(line)
        elif line.strip():
            if remaining and remaining[-1].startswith("- [x]"):
                remaining.append(line)
            else:
                remaining.append(line)

    if not archive_items:
        print("アーカイブ対象なし（2ヶ月以上前の完了タスクなし）")
        return 0

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    archive_file = ARCHIVE_DIR / f"バックログ_アーカイブ_{now.strftime('%Y-%m')}.md"

    header = f"## {now.strftime('%Y年%-m月')} アーカイブ\n\n"
    if archive_file.exists():
        content = archive_file.read_text(encoding="utf-8")
    else:
        content = f"# バックログアーカイブ\n\n{header}"
    for item in archive_items:
        content += item + "\n"
    archive_file.write_text(content, encoding="utf-8")

    # 元ファイルを更新
    new_text = text.replace(m.group(2), "\n".join(remaining), 1)
    BACKLOG.write_text(new_text, encoding="utf-8")

    print(f"✅ {len(archive_items)}件を {archive_file.name} にアーカイブ")
    for item in archive_items[:3]:
        print(f"   {item[:70]}")
    if len(archive_items) > 3:
        print(f"   ... 他{len(archive_items)-3}件")
    return 0


# =============================================================================
# main
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="バックログ自動完了チェック")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("prompt", help="7日以上経過タスクを確認プロンプト出力")
    sub.add_parser("match", help="git履歴と照合して自動完了")
    sub.add_parser("archive", help="2ヶ月以上前をアーカイブ")

    args = parser.parse_args()

    if args.cmd == "prompt":
        return cmd_prompt()
    elif args.cmd == "match":
        return cmd_match()
    elif args.cmd == "archive":
        return cmd_archive()


if __name__ == "__main__":
    sys.exit(main())
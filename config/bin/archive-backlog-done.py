#!/usr/bin/env python3
"""バックログの [x] タスクを完了済みセクションに自動移動する."""

import re
import sys
from pathlib import Path

BACKLOG = Path.home() / "projects/obsidian-ssot/00_SYSTEM/バックログ.md"


def parse_sections(text):
    """バックログをセクション単位でパースする."""
    sections = []
    current_header = None
    current_lines = []

    for line in text.split("\n"):
        if line.startswith("## "):
            if current_header is not None:
                sections.append((current_header, current_lines))
            current_header = line
            current_lines = []
        else:
            current_lines.append(line)

    if current_header is not None:
        sections.append((current_header, current_lines))

    return sections


def extract_done_items(lines):
    """[x] 行とその直後のインデント行を抽出し、残りを返す."""
    done = []
    remaining = []
    i = 0
    while i < len(lines):
        if re.match(r"^- \[x\]", lines[i]):
            done.append(lines[i])
            i += 1
            # 直後のインデント行（詳細）も一緒に
            while i < len(lines) and lines[i].startswith("  "):
                done.append(lines[i])
                i += 1
        else:
            remaining.append(lines[i])
            i += 1
    return done, remaining


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else BACKLOG
    if not path.exists():
        print(f"バックログファイルが見つかりません: {path}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    sections = parse_sections(text)

    all_done = []
    new_sections = []

    for header, lines in sections:
        if header in ("## P0: 今すぐやるべき", "## P1: 近いうちにやる", "## P2: いつかやる"):
            done, remaining = extract_done_items(lines)
            all_done.extend(done)
            new_sections.append((header, remaining))
        else:
            new_sections.append((header, lines))

    if not all_done:
        print("移動対象なし")
        return

    # 完了済みセクションに挿入
    result = []
    for header, lines in new_sections:
        result.append(header)
        if header == "## 完了済み":
            for d in all_done:
                result.append(d)
        result.extend(lines)

    output = "\n".join(result)
    if output == text:
        print("変更なし")
        return

    path.write_text(output, encoding="utf-8")
    print(f"{len([l for l in all_done if l.startswith('- [x]')])}件を完了済みに移動しました")
    for d in all_done:
        if d.startswith("- [x]"):
            print(f"  {d}")


if __name__ == "__main__":
    main()

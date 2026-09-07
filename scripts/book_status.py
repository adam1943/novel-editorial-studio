#!/usr/bin/env python3
"""Project-level status for a long-form novel workspace.

Reports word progress, chapter gaps, subplot stalls and foreshadow overdue rows.
All findings are clues for the reviewer, not verdicts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
CHAPTER_NUM = re.compile(r"第\s*([0-9]{1,5}|[零一二三四五六七八九十百千万]+)\s*章")
ARABIC = re.compile(r"(?<!\d)(\d{1,5})(?!\d)")

CN_DIGITS = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
CN_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10000}

DEFAULT_MANUSCRIPT_DIRS = ["正文", "manuscript", "chapters"]
SUBPLOT_FILES = ["支线进度板.md", "subplot_board.md"]
HOOK_FILES = ["伏笔台账.md", "pending_hooks.md"]


def cn_to_int(text: str):
    if text.isdigit():
        return int(text)
    total = section = current = 0
    for ch in text:
        if ch in CN_DIGITS:
            current = CN_DIGITS[ch]
        elif ch in CN_UNITS:
            unit = CN_UNITS[ch]
            if unit == 10000:
                section = (section + max(current, 1)) * unit
                total += section
                section = 0
            else:
                section += max(current, 1) * unit
            current = 0
        else:
            return None
    return (total + section + current) or None


def chapter_number(path: Path, text: str):
    for source in (path.name, text[:200]):
        m = CHAPTER_NUM.search(source)
        if m:
            value = cn_to_int(m.group(1))
            if value:
                return value
    m = ARABIC.search(path.stem)
    return int(m.group(1)) if m else None


def find_manuscript_files(root: Path):
    for name in DEFAULT_MANUSCRIPT_DIRS:
        candidate = root / name
        if candidate.is_dir():
            return sorted(x for x in candidate.rglob("*.md") if x.is_file())
    return sorted(x for x in root.rglob("*.md") if x.is_file() and CHAPTER_NUM.search(x.name))


def read_table_rows(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells:
            rows.append(cells)
    return rows


def chapter_column(header, keywords):
    """Pick the column that holds a chapter number, by header keyword."""
    for idx, name in enumerate(header):
        if any(k in name for k in keywords):
            return idx
    return None


def cell_chapter(cells, index):
    if index is not None and index < len(cells):
        m = ARABIC.search(cells[index])
        if m:
            return int(m.group(1))
        return None
    numbers = [int(m.group(1)) for m in ARABIC.finditer(" ".join(cells))]
    return max(numbers) if numbers else None


def first_existing(root: Path, names):
    for name in names:
        p = root / name
        if p.is_file():
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Long-form novel project status.")
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--target-words", type=int, default=2_000_000)
    ap.add_argument("--stall-limit", type=int, default=15, help="Chapters a subplot may stay idle")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    files = find_manuscript_files(root)
    chapters = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        chapters.append(
            {"path": str(path), "chapter": chapter_number(path, text), "words": len(CJK.findall(text))}
        )

    numbered = sorted([c for c in chapters if c["chapter"]], key=lambda c: c["chapter"])
    total_words = sum(c["words"] for c in chapters)
    numbers = [c["chapter"] for c in numbered]
    gaps = []
    duplicates = []
    if numbers:
        seen = {}
        for c in numbered:
            seen.setdefault(c["chapter"], []).append(c["path"])
        duplicates = [{"chapter": k, "paths": v} for k, v in seen.items() if len(v) > 1]
        expected = set(range(min(numbers), max(numbers) + 1))
        gaps = sorted(expected - set(numbers))

    latest = numbers[-1] if numbers else 0
    avg_words = round(total_words / len(chapters)) if chapters else 0
    remaining = max(args.target_words - total_words, 0)
    est_chapters_left = round(remaining / avg_words) if avg_words else None

    stalls = []
    subplot_file = first_existing(root, SUBPLOT_FILES)
    if subplot_file:
        rows = read_table_rows(subplot_file)
        if rows:
            header, body = rows[0], rows[1:]
            col = chapter_column(header, ("上次推进", "推进章", "最近章", "章号", "last"))
            for row in body:
                last = cell_chapter(row, col)
                if last is not None and latest - last > args.stall_limit:
                    stalls.append({"line": row[0], "last_chapter": last, "idle": latest - last})

    overdue = []
    hook_file = first_existing(root, HOOK_FILES)
    if hook_file:
        rows = read_table_rows(hook_file)
        if rows:
            header, body = rows[0], rows[1:]
            col = chapter_column(header, ("兑现章", "预期兑现", "期限", "due"))
            for row in body:
                joined = " ".join(row)
                if any(word in joined for word in ("已兑现", "已回收", "已放弃", "closed")):
                    continue
                due = cell_chapter(row, col)
                if due is not None and latest > due:
                    overdue.append({"hook": row[0], "due": due, "late_by": latest - due})

    report = {
        "root": str(root),
        "chapters": len(chapters),
        "latest_chapter": latest,
        "total_words": total_words,
        "avg_words": avg_words,
        "target_words": args.target_words,
        "progress": round(total_words / args.target_words * 100, 2) if args.target_words else None,
        "estimated_chapters_left": est_chapters_left,
        "chapter_gaps": gaps,
        "duplicate_chapters": duplicates,
        "subplot_stalls": stalls,
        "overdue_hooks": overdue,
        "unnumbered_files": [c["path"] for c in chapters if not c["chapter"]],
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"root={report['root']}")
        print(
            f"chapters={report['chapters']} latest={report['latest_chapter']} "
            f"words={report['total_words']} avg={report['avg_words']} progress={report['progress']}%"
        )
        if est_chapters_left is not None:
            print(f"estimated chapters left to target: {est_chapters_left}")
        if gaps:
            print(f"chapter gaps: {gaps[:20]}{' ...' if len(gaps) > 20 else ''}")
        for d in duplicates:
            print(f"duplicate chapter {d['chapter']}: {d['paths']}")
        for s in stalls:
            print(f"subplot stalled: {s['line']} last={s['last_chapter']} idle={s['idle']}")
        for o in overdue:
            print(f"overdue hook: {o['hook']} due={o['due']} late_by={o['late_by']}")
        if report["unnumbered_files"]:
            print(f"unnumbered files: {len(report['unnumbered_files'])}")

    return 1 if (gaps or duplicates) else 0


if __name__ == "__main__":
    raise SystemExit(main())

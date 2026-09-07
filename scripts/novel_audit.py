#!/usr/bin/env python3
"""Mechanical audit for Chinese long-form manuscript chapters.

Findings are evidence for a reviewer, not verdicts.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
SENTENCE_SPLIT = re.compile(r"[。！？!?；;\n]+")
CHAPTER_NUM = re.compile(r"第\s*([0-9]{1,5}|[零一二三四五六七八九十百千万]+)\s*章")
ARABIC_IN_NAME = re.compile(r"(?<!\d)(\d{1,5})(?!\d)")
DIALOGUE_LINE = re.compile(r"[\u201c\"'\u2018\u300a]")
URL = re.compile(r"(https?://|www\.|\.com|\.cn/|微信|QQ群|公众号)", re.IGNORECASE)
PLACEHOLDER = re.compile(r"(TODO|TBD|FIXME|待补|待定|占位|\bXXX\b|\[\s*\?\s*\])", re.IGNORECASE)
LIST_LINE = re.compile(r"^\s*([-*+]|\d+[.、)]|[一二三四五六七八九十]+[、.)])\s+")

AI_MARKERS = ["仿佛", "忽然", "竟然", "不禁", "宛如", "猛地", "似乎", "顿时"]
TEMPLATE_PHRASES = [
    "本章必须",
    "状态变化",
    "核心动机",
    "信息落差",
    "人物弧光",
    "执行边界",
    "章末压力",
    "值得注意的是",
    "不难看出",
    "总而言之",
    "综上所述",
    "在这个过程中",
    "众所周知",
]
FATIGUE_WORDS = [
    "瞳孔骤缩",
    "不可置信",
    "深不可测",
    "毛骨悚然",
    "淡淡一笑",
    "眼神一冷",
    "心头一颤",
    "莫名的",
    "说不出的",
    "气息一沉",
]
EMOTION_LABELS = ["感到恐惧", "感到愤怒", "感到悲伤", "内心复杂", "百感交集", "心情复杂"]

CN_DIGITS = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
CN_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10000}


def cn_to_int(text: str):
    if text.isdigit():
        return int(text)
    total = 0
    section = 0
    current = 0
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
    m = ARABIC_IN_NAME.search(path.stem)
    return int(m.group(1)) if m else None


def cjk_count(text: str) -> int:
    return len(CJK.findall(text))


def sentences(text: str):
    out = []
    for chunk in SENTENCE_SPLIT.split(text):
        chunk = re.sub(r"\s+", " ", chunk).strip()
        if cjk_count(chunk) >= 8:
            out.append(chunk)
    return out


def paragraphs(text: str):
    return [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]


def issue(dim: str, severity: str, detail: str, evidence: str = "") -> dict:
    return {"dim": dim, "severity": severity, "detail": detail, "evidence": evidence}


def audit_text(path: Path, text: str, min_words: int, max_words: int) -> dict:
    words = cjk_count(text)
    paras = paragraphs(text)
    body_paras = [p for p in paras if not p.startswith("#")]
    sents = sentences(text)
    issues = []

    if words < min_words:
        issues.append(issue("字数", "warn", f"正文 {words} 字，低于下限 {min_words}"))
    elif words > max_words:
        issues.append(issue("字数", "warn", f"正文 {words} 字，高于上限 {max_words}"))

    for m in PLACEHOLDER.finditer(text):
        issues.append(issue("机械问题", "block", "存在占位符或未替换模板", m.group(0)))
    bad_char = "\ufffd"
    if bad_char in text:
        issues.append(issue("机械问题", "block", f"存在乱码替换符 {text.count(bad_char)} 处"))
    for m in URL.finditer(text):
        issues.append(issue("格式规范", "block", "正文含外链或联系方式", m.group(0)))

    open_quotes = text.count("\u201c")
    close_quotes = text.count("\u201d")
    if open_quotes != close_quotes:
        issues.append(issue("机械问题", "warn", f"引号不配对：{open_quotes} 开 {close_quotes} 闭"))

    list_lines = [p for p in body_paras if LIST_LINE.match(p)]
    if list_lines:
        issues.append(issue("列表化叙述", "warn", f"正文出现 {len(list_lines)} 行清单式罗列", list_lines[0][:40]))

    per_3000 = max(words / 3000, 0.34)
    marker_hits = {w: text.count(w) for w in AI_MARKERS if text.count(w)}
    marker_total = sum(marker_hits.values())
    if marker_total / per_3000 > 3:
        top = ", ".join(f"{k}x{v}" for k, v in sorted(marker_hits.items(), key=lambda x: -x[1])[:4])
        issues.append(issue("套话密度", "warn", f"AI 标记词每 3000 字 {marker_total / per_3000:.1f} 次", top))

    for phrase in TEMPLATE_PHRASES:
        count = text.count(phrase)
        if count:
            level = "warn" if count > 1 else "note"
            issues.append(issue("说明书腔", level, f"模板表达 {phrase} x{count}", phrase))

    for phrase in FATIGUE_WORDS:
        count = text.count(phrase)
        if count >= 2:
            issues.append(issue("词汇疲劳", "warn", f"疲劳词 {phrase} x{count}", phrase))

    for phrase in EMOTION_LABELS:
        if phrase in text:
            issues.append(issue("情感标签", "note", f"情绪贴标签 {phrase}", phrase))

    dup_sentences = [s for s, c in Counter(sents).items() if c > 1]
    if dup_sentences:
        issues.append(issue("重复句", "warn", f"章内重复句 {len(dup_sentences)} 条", dup_sentences[0][:40]))

    if len(body_paras) >= 8:
        lengths = [cjk_count(p) for p in body_paras]
        mean = statistics.fmean(lengths)
        stdev = statistics.pstdev(lengths)
        if mean > 0 and stdev / mean < 0.25:
            issues.append(issue("段落节奏", "warn", f"段长过度均匀，变异系数 {stdev / mean:.2f}"))
        long_paras = [p for p in body_paras if cjk_count(p) > 320]
        if long_paras:
            issues.append(issue("格式规范", "note", f"超长段落 {len(long_paras)} 段", long_paras[0][:30]))

    if body_paras:
        dialogue = sum(1 for p in body_paras if DIALOGUE_LINE.search(p))
        ratio = dialogue / len(body_paras)
        if ratio < 0.15:
            issues.append(issue("流水账", "note", f"对话段占比 {ratio:.0%}，偏低"))
        elif ratio > 0.8:
            issues.append(issue("悬空对白", "note", f"对话段占比 {ratio:.0%}，动作落点可能不足"))

    severities = Counter(i["severity"] for i in issues)
    return {
        "path": str(path),
        "chapter": chapter_number(path, text),
        "words": words,
        "paragraphs": len(body_paras),
        "sentences": len(sents),
        "counts": {k: severities.get(k, 0) for k in ("block", "warn", "note")},
        "issues": issues,
        "sentence_pool": sents,
    }


def collect(paths):
    files = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(x for x in p.rglob("*.md") if x.is_file()))
        elif p.is_file():
            files.append(p)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description="Mechanical audit for novel chapters.")
    ap.add_argument("paths", nargs="+", help="Chapter files or directories")
    ap.add_argument("--min-words", type=int, default=2000)
    ap.add_argument("--max-words", type=int, default=3200)
    ap.add_argument("--json", action="store_true", help="Emit structured JSON")
    ap.add_argument("--cross-repeat", type=int, default=2, help="Flag sentences repeated across files")
    args = ap.parse_args()

    files = collect(args.paths)
    if not files:
        print("No markdown files found.", file=sys.stderr)
        return 2

    reports = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        reports.append(audit_text(path, text, args.min_words, args.max_words))

    pool = Counter()
    for r in reports:
        pool.update(set(r["sentence_pool"]))
    cross = {s for s, c in pool.items() if c >= args.cross_repeat} if len(files) > 1 else set()
    for r in reports:
        hits = [s for s in set(r["sentence_pool"]) if s in cross]
        if hits:
            r["issues"].append(issue("跨章重复", "warn", f"与其他章重复句 {len(hits)} 条", hits[0][:40]))
            r["counts"]["warn"] += 1
        del r["sentence_pool"]

    total = Counter()
    for r in reports:
        total.update(r["counts"])
    summary = {
        "files": len(reports),
        "total_words": sum(r["words"] for r in reports),
        "block": total.get("block", 0),
        "warn": total.get("warn", 0),
        "note": total.get("note", 0),
    }

    if args.json:
        print(json.dumps({"summary": summary, "chapters": reports}, ensure_ascii=False, indent=2))
    else:
        for r in reports:
            print(
                f"{r['path']} chapter={r['chapter']} words={r['words']} "
                f"block={r['counts']['block']} warn={r['counts']['warn']} note={r['counts']['note']}"
            )
            for i in r["issues"]:
                tail = f" | {i['evidence']}" if i["evidence"] else ""
                print(f"  [{i['severity']}] {i['dim']}: {i['detail']}{tail}")
        print(
            f"TOTAL files={summary['files']} words={summary['total_words']} "
            f"block={summary['block']} warn={summary['warn']} note={summary['note']}"
        )

    return 1 if summary["block"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

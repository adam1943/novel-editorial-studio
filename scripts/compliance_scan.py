#!/usr/bin/env python3
"""Keyword and format pre-screen for platform submission.

This is a triage aid. A hit is not a violation, and a clean scan is not approval.
Judgment stays with the reviewer, per references/platform-compliance.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")

RED_LINES = {
    "未成年涉性": ["幼女", "萝莉的身体", "未成年.{0,6}(裸|性|欲)"],
    "露骨性描写": ["性交", "交合", "呻吟着.{0,8}(进入|抽)", "下体.{0,6}(插|入)"],
    "自杀自残方法": ["割腕的方法", "上吊的.{0,4}(步骤|方法)", "如何自杀", "服药自尽的剂量"],
    "制毒制爆": ["制毒", "冰毒配方", "土制炸弹", "炸药配方", "枪械改装"],
    "违禁交易": ["卖淫", "毒品交易.{0,6}(渠道|价格)", "器官买卖"],
    "仇恨歧视": ["劣等民族", "该死的.{0,3}族", "残废活该"],
    "现实政治敏感": ["政治局", "国家主席", "中央军委"],
}

HIGH_RISK = {
    "血腥细节": ["内脏", "肠子", "脑浆", "血肉模糊", "剖开"],
    "亲密戏越界": ["赤裸", "喘息", "衣衫尽褪", "缠绵"],
    "犯罪手法": ["撬锁", "配钥匙", "洗钱", "销赃", "下药"],
    "赌博": ["赌场", "押注", "老虎机"],
    "药物滥用": ["兴奋剂", "镇痛剂上瘾", "吸食"],
    "医疗法律建议": ["建议服用", "剂量为", "根据刑法第"],
}

FORMAT_CHECKS = {
    "外链联系方式": r"(https?://|www\.|微信|QQ群|公众号|加我)",
    "作者的话": r"(作者的话|求推荐票|求月票|读者朋友们|本章说)",
    "平台互推": r"(起点|番茄小说|七猫|晋江|纵横)",
    "占位符": r"(TODO|TBD|待补|待定|占位|XXX)",
    "异常符号": r"([\u200b-\u200f\u2060\ufeff]|[!?]{3,}|[。]{2,})",
    "全角字母数字": r"[\uff21-\uff3a\uff41-\uff5a\uff10-\uff19]",
}


def cjk_count(text: str) -> int:
    return len(CJK.findall(text))


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def scan_text(path: Path, text: str, min_words: int, max_words: int) -> dict:
    words = cjk_count(text)
    findings = []

    for bucket, patterns in RED_LINES.items():
        for pat in patterns:
            for m in re.finditer(pat, text):
                findings.append(
                    {
                        "severity": "block",
                        "category": bucket,
                        "line": line_of(text, m.start()),
                        "evidence": m.group(0)[:30],
                        "action": "改内容本身，不做技术性变形",
                    }
                )

    for bucket, patterns in HIGH_RISK.items():
        for pat in patterns:
            hits = list(re.finditer(pat, text))
            if hits:
                findings.append(
                    {
                        "severity": "warn",
                        "category": bucket,
                        "line": line_of(text, hits[0].start()),
                        "evidence": f"{hits[0].group(0)[:20]} x{len(hits)}",
                        "action": "降低强度或转场留白",
                    }
                )

    for name, pat in FORMAT_CHECKS.items():
        for m in re.finditer(pat, text):
            findings.append(
                {
                    "severity": "block" if name in {"外链联系方式", "占位符"} else "warn",
                    "category": name,
                    "line": line_of(text, m.start()),
                    "evidence": repr(m.group(0))[:30],
                    "action": "按平台格式基线修正",
                }
            )

    if words < min_words or words > max_words:
        findings.append(
            {
                "severity": "warn",
                "category": "章节字数",
                "line": 1,
                "evidence": f"{words} 字",
                "action": f"调整到 {min_words}-{max_words} 区间",
            }
        )

    counts = Counter(f["severity"] for f in findings)
    return {
        "path": str(path),
        "words": words,
        "counts": {"block": counts.get("block", 0), "warn": counts.get("warn", 0)},
        "findings": findings,
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
    ap = argparse.ArgumentParser(description="Platform compliance pre-screen.")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--min-words", type=int, default=2000)
    ap.add_argument("--max-words", type=int, default=3200)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    files = collect(args.paths)
    if not files:
        print("No markdown files found.", file=sys.stderr)
        return 2

    reports = [
        scan_text(p, p.read_text(encoding="utf-8", errors="replace"), args.min_words, args.max_words)
        for p in files
    ]
    total = Counter()
    for r in reports:
        total.update(r["counts"])

    summary = {
        "files": len(reports),
        "block": total.get("block", 0),
        "warn": total.get("warn", 0),
        "note": "线索仅供复核，命中不等于违规，未命中不等于安全",
    }

    if args.json:
        print(json.dumps({"summary": summary, "files": reports}, ensure_ascii=False, indent=2))
    else:
        for r in reports:
            print(f"{r['path']} words={r['words']} block={r['counts']['block']} warn={r['counts']['warn']}")
            for f in r["findings"]:
                print(f"  [{f['severity']}] {f['category']} line {f['line']}: {f['evidence']} -> {f['action']}")
        print(f"TOTAL files={summary['files']} block={summary['block']} warn={summary['warn']}")
        print(summary["note"])

    return 1 if summary["block"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

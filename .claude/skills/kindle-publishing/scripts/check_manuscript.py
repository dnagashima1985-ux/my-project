#!/usr/bin/env python3
"""Sweep a manuscript for the mistakes that survive a careful read.

Usage:  python3 check_manuscript.py [book.json]

These are the errors a human proofreader tends to miss because each one looks
fine in isolation — they only show up when you compare across chapters. Run it
before every build; it takes a second and has caught real problems.

Checks:
  1. placeholders that were never filled in (著者名, TODO, XXX, ここに…)
  2. mixed notation for the same term (見落とし/見落し, 引き継ぎ/引継ぎ …)
  3. full-width digits, which read badly on Kindle
  4. stray non-Japanese scripts (Cyrillic/Hangul) from a slip of the keyboard
  5. repeated key figures, so a number quoted in two chapters can be eyeballed
  6. chapters with no deep-dive section (warning only — a chapter that only
     restates the source reads thin, and that is invisible when proofreading
     one chapter at a time)
  7. per-chapter and total character counts against the target
"""

import collections
import json
import os
import re
import sys

# Deliberately unambiguous markers only. Loose ones like "ここに" match ordinary
# prose ("囁く才能はここにいる") and train you to ignore the report.
PLACEHOLDERS = ["著者名", "TODO", "TBD", "XXX", "FIXME", "仮題", "（未定）",
                "ここに挿入", "＿＿", "本文をここに"]

# Chapters carrying only borrowed facts read thin. Each main chapter should
# have one section that goes a step below the source: mechanism, worked
# calculation, or a named case. Front and back matter are exempt.
DEEPDIVE = re.compile(r"^#{2,3}\s*(もう一段深く|深掘り|コラム|なぜ)", re.M)
NO_DEEPDIVE_NEEDED = ("はじめに", "終章", "付録", "出典", "奥付")

VARIANTS = [
    ("見落とし", "見落し"), ("引き継ぎ", "引継ぎ"), ("問い合わせ", "問合せ"),
    ("組み合わせ", "組合せ"), ("取り組み", "取組み"), ("受け入れ", "受入れ"),
    ("行う", "行なう"), ("full-width ID", "ＩＤ"),
]


def main(cfg_path):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    root = os.path.dirname(os.path.abspath(cfg_path))
    src = os.path.join(root, cfg.get("src_dir", "src"))
    files = [f for f, _ in cfg["chapters"]]
    text = {f: open(os.path.join(src, f), encoding="utf-8").read() for f in files}
    allt = "\n".join(text.values())
    problems = 0

    print("== 未置換のプレースホルダ ==")
    for f in files:
        for i, line in enumerate(text[f].split("\n"), 1):
            for p in PLACEHOLDERS:
                if p in line:
                    print("  ! %s:%d  %s" % (f, i, line.strip()[:60]))
                    problems += 1
    print("  なし" if problems == 0 else "")

    print("== 表記ゆれ ==")
    found = 0
    for good, bad in VARIANTS:
        if bad in allt:
            print("  ! %r が %d 件（正: %s）" % (bad, allt.count(bad), good))
            found += 1
    problems += found
    if not found:
        print("  なし")

    print("== 全角数字 ==")
    fw = re.findall(r"[０-９]", allt)
    if fw:
        print("  ! %d 文字（半角に統一してください）" % len(fw))
        problems += 1
    else:
        print("  なし")

    print("== 他言語の文字混入 ==")
    stray = 0
    for f in files:
        for i, line in enumerate(text[f].split("\n"), 1):
            if re.search(r"[Ѐ-ӿ가-힯]", line):
                print("  ! %s:%d  %s" % (f, i, line.strip()[:60]))
                stray += 1
    problems += stray
    if not stray:
        print("  なし")

    print("== 複数章に出てくる数値（章をまたいで一致しているか目視） ==")
    nums = collections.Counter()
    for f in files:
        for m in set(re.findall(r"\d[\d,\.]*\s*(?:%|人|年|倍|km|字|件|割)", text[f])):
            # Small counts ("2回", "3人") are prose, not claims. Only figures
            # big enough to be a cited statistic are worth cross-checking.
            head = re.match(r"[\d,\.]+", m.strip())
            try:
                if float(head.group().replace(",", "")) < 10:
                    continue
            except (AttributeError, ValueError):
                continue
            nums[m.strip()] += 1
    for n, c in sorted(nums.items(), key=lambda kv: -kv[1]):
        if c >= 2:
            print("  %-12s %d章" % (n, c))

    print("== 深掘りのない章（注意） ==")
    thin = 0
    for f, nav in cfg["chapters"]:
        if any(k in nav for k in NO_DEEPDIVE_NEEDED):
            continue
        if not DEEPDIVE.search(text[f]):
            print("  - %s（%s）機序・計算・事例のどれかを1つ足す" % (f, nav))
            thin += 1
    if thin:
        print("  （この見出しの規約より前に書いた本では全章が並ぶ。無視してよい）")
    else:
        print("  なし")

    print("== 文字数 ==")
    total = 0
    for f, nav in cfg["chapters"]:
        n = len(re.sub(r"\s", "", text[f]))
        total += n
        print("  %-26s %6d 字  %s" % (f, n, nav))
    target = cfg.get("target_chars", 50000)
    print("  ---")
    print("  合計 %d 字（目標 %d 字, %+d）" % (total, target, total - target))

    print()
    print("問題: %d 件" % problems)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "book.json"))

#!/usr/bin/env python3
"""Scaffold a new book so writing can start immediately.

Usage:
  python3 new_book.py <slug> --title タイトル [--subtitle 副題] [--chapters 7]
                             [--dir .] [--framework 関門]

Creates book.json, notes/evidence.md and one stub per chapter in src/, each
stub already shaped like the standard chapter template (including the
"もう一段深く" slot). Stubs carry TODO markers on purpose: check_manuscript.py
fails while any of them survive, so a half-written book cannot be built by
accident.

Nothing here is guesswork you have to keep in your head — the parts that
differ per book (title split for the cover, chapter titles) are left as
TODO in book.json and fail loudly rather than shipping a wrong cover.
"""

import argparse
import io
import json
import os
import sys

CHAPTER_STUB = """# {heading}

## 漏れの正体

TODO 何が、どう失われているのか。読者の実感から入る。

## 証拠

TODO 研究と実践。誰の研究か、どこの協会かを名指しで引く。証拠カードから3枚以上。

## もう一段深く：TODO

TODO 機序・計算・事例のどれか1つ。資料の一段下を書く。
機序なら「A→B→C」を矢印でつないでから文章にする。
計算なら過程を見せて、読者が自分のクラブの数字で計算し直せる形にする。

## 日本の事情

TODO 制度・慣行・季節。ここが本の価値の半分。

## 塞ぎ方

TODO 具体策を番号つきで。すぐ実行できる粒度まで下ろす。

## 道具：TODO

TODO 名前のついた書式。列名と、1行の運用の掟まで書く。

## 測り方

TODO この章の状態を見る指標を3〜6個。

## 現場ワーク：TODO

TODO 30〜90分で終わる実作業。所要時間を書く。

---

**{heading}の要点**

- TODO 6〜9行
"""

HAJIMENI_STUB = """# はじめに

TODO 読者がいま困っていることから入る。1,500〜2,000字。

最後に、読者が自分の組織を測れる問いを4つ置く。

1. TODO
2. TODO
3. TODO
4. TODO
"""

JYOSHOU_STUB = """# 序章 TODO

## TODO 読者の実感

TODO

## 枠組みの提示

TODO ここで枠組みを完全に説明しきる。ここが弱いと以降の章がバラバラになる。
2,500〜3,000字。

## もう一段深く：TODO

TODO 枠組みから出る反直感な結論。計算で見せられるとなお良い。
"""

SHUSHOU_STUB = """# 終章 TODO

## この本の道具は、人を傷つけうる

TODO 分類する道具を扱う自覚。記録は本人の目に触れても構わない言葉で書く。
個人情報の扱い（誰が見るか・どこに置くか・いつ消すか・どう説明するか）。

## 結局のところ、三つ

TODO

## 最後に

TODO はじめにの問いに戻る。
"""

APPENDIX_STUB = """# 付録A TODO チェックリスト

TODO 本文の道具をまとめた、そのまま使える形。

# 付録B 道具一覧

TODO 章ごとの道具と、使う場面。

# 付録C 用語集

TODO 本文のカタカナ語と専門語。

# 出典

TODO 主要典拠と、参照した研究・実践を名前つきで列挙。

# 本書と原典の関係

TODO 原典に存在しない要素（枠組み、道具、実装手順）を具体的に列挙する1段落。
省略しない。読者への誠実さであり、権利上の防御でもある。

# 免責

TODO 本書は著者の提案であり、原典の団体の見解ではない旨。

# 奥付

**TODO 書名**

TODO 副題

著　{author}

**発行元　{publisher}**

本書の内容についてのお問い合わせ、および記載した書式・チェックリストの
自組織での利用については、発行元までご連絡ください。

© {publisher}
"""

EVIDENCE_HEADER = """# 証拠カード — {title}

資料を読みながら1事実＝1枚で足していく。目安40〜80枚。
見出しに載っている話だけを拾うと20枚で止まる。止まったら脚注・図表の注記・
事例の細部・用語の定義・「資料が触れていないこと」をもう一周する。

書き終えたらカードを章に配る。1章3枚未満の章は、枠組みのほうがずれている。

| # | 事実 | 数字 | 誰が | どこ | 章 |
|---|---|---|---|---|---|
| 1 |  |  |  | source.pdf p. |  |
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scaffold a new KDP book")
    ap.add_argument("slug", help="英字のファイル名（例: mitsu-no-tokei）")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--chapters", type=int, default=7,
                    help="本編の章数（枠組みの数。既定7）")
    ap.add_argument("--author", default="フットボールパラダイム")
    ap.add_argument("--publisher", default="フットボールパラダイム")
    ap.add_argument("--dir", default=".", help="出力先ディレクトリ")
    ap.add_argument("--force", action="store_true", help="既存ファイルを上書きする")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.dir)
    src = os.path.join(root, "src")
    notes = os.path.join(root, "notes")
    cfg_path = os.path.join(root, "book.json")
    if os.path.exists(cfg_path) and not args.force:
        raise SystemExit("book.json がすでにあります（--force で上書き）")
    os.makedirs(src, exist_ok=True)
    os.makedirs(notes, exist_ok=True)

    chapters = [("00-hajimeni.md", "はじめに", HAJIMENI_STUB),
                ("01-jyoshou.md", "序章 TODO", JYOSHOU_STUB)]
    for i in range(1, args.chapters + 1):
        fname = "%02d-ch%d.md" % (i + 1, i)
        heading = "第%d章 TODO" % i
        chapters.append((fname, heading, CHAPTER_STUB.format(heading=heading)))
    n = args.chapters + 2
    chapters.append(("%02d-shushou.md" % n, "終章 TODO", SHUSHOU_STUB))
    chapters.append(("%02d-appendix.md" % (n + 1), "付録・出典",
                     APPENDIX_STUB.format(author=args.author,
                                          publisher=args.publisher)))

    written = 0
    for fname, _nav, stub in chapters:
        path = os.path.join(src, fname)
        if os.path.exists(path) and not args.force:
            continue
        io.open(path, "w", encoding="utf-8").write(stub)
        written += 1

    cfg = {
        "slug": args.slug,
        "title": args.title,
        "subtitle": args.subtitle,
        "author": args.author,
        "publisher": args.publisher,
        "lang": "ja",
        "target_chars": 50000,
        "chapters": [[f, nav] for f, nav, _ in chapters],
        "cover": {
            "title_1": "TODO タイトル前半",
            "title_2": "TODO 後半（極太で大きく出る側）",
            "hook": "TODO 煽りの一行",
            "copy": ["TODO 補足コピー1行目", "TODO 2行目"],
            "badge": ["サッカー", "指導者に", "ひらめきを"],
            "badge_color": "#1B5FA8",
            "accent": "#F08A24",
            "diagram_labels": [],
            "diagram_numbers": [],
            "layouts": ["white", "navy", "diagram"],
        },
    }
    io.open(cfg_path, "w", encoding="utf-8").write(
        json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")

    ev = os.path.join(notes, "evidence.md")
    if not os.path.exists(ev) or args.force:
        io.open(ev, "w", encoding="utf-8").write(
            EVIDENCE_HEADER.format(title=args.title))

    print("scaffolded in %s" % root)
    print("  book.json          （cover.title_1 / title_2 は必ず埋める）")
    print("  notes/evidence.md  （まずここを40〜80枚にする）")
    print("  src/               %d ファイル" % written)
    print()
    print("次: 資料を読んで証拠カード → 枠組みを設計 → 章タイトルを book.json に")
    print("    書き戻す → 執筆 → check_manuscript.py（TODOが残っていると落ちる）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

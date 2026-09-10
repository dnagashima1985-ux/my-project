# 一週間を逆算する — 原稿一式

副題：試合の5日前から当日まで、練習をどう並べるか
著／発行元：フットボールパラダイム

日本の育成現場向けに書き下ろしたオリジナルの実務書です。骨格は独自の「四つの疲れ（筋・神経・頭・心）」と、
それを一週間に並べる「週の器」。
Barça Innovation Hub の記事「Training models in modern football」と、そこで
名前が挙がる研究（フラーデ／ブヒャイトら／UEFA傷害調査ほか）は、出典を明記
したうえで**証拠として引用**しています。

## 構成

```
books/gyakusan/
├── notes/evidence.md           証拠カード60枚（原稿の裏づけ）
├── src/                        章ごとのMarkdown（ここを編集する）
│   ├── 00-hajimeni.md          はじめに
│   ├── 01-jyoshou.md           序章 一週間という単位（四つの疲れ）
│   ├── 02-ch1.md               第1章 筋の疲れ
│   ├── 03-ch2.md               第2章 神経の疲れ
│   ├── 04-ch3.md               第3章 頭の疲れ
│   ├── 05-ch4.md               第4章 心の疲れ
│   ├── 06-ch5.md               第5章 週の器（型A〜D）
│   ├── 07-ch6.md               第6章 連戦の週（削る順番）
│   ├── 08-ch7.md               第7章 測る（sRPEとACWRの限界）
│   ├── 09-ch8.md               第8章 夏と学校
│   ├── 10-ch9.md               第9章 四週間で回す
│   ├── 11-shushou.md           終章 選手は機械ではない
│   └── 12-appendix.md          付録A-D・出典・免責・奥付
├── book.json                   全スクリプトが読む唯一の設定
├── cover_art.py                表紙3案の絵（タイトルから起こしたもの）
├── kdp-form.md                 KDP入力シート（画面の項目順）
├── kdp-listing.md              内容紹介・キーワード・価格
├── build/                      EPUB と結合Markdown（生成物）
└── cover/                      表紙3案（生成物）
```

本文47,151字／全13セクション。各章は共通の型——何が起きているか／証拠／
もう一段深く／日本の事情／どう組むか／道具／測り方／現場ワーク／要点。

## ビルド

```bash
S=~/.claude/skills/kindle-publishing/scripts
python3 $S/check_manuscript.py book.json   # 先に必ず
python3 $S/build_epub.py     book.json
python3 $S/build_cover.py    book.json
```

## 表紙

`cover/` に3案あります（1600×2560px・JPEG、KDPにそのまま入稿可）。
**タイトルから起こした描き下ろし**です。絵の定義は `cover_art.py`。

| ファイル | 案 |
|---|---|
| **`cover/gyakusan-row.jpg`** | **採用案。**ボールの一列。MD-3→MDの並びで、MD-2に輪 |
| `cover/gyakusan-cones.jpg` | 芝に立つコーン。MD-5からOFFまで、MD-2だけ高い |
| `cover/gyakusan-swap.jpg` | 上と下で同じ7個。2つ入れ替えただけで週が変わる |

文言・色は `book.json` の `cover`、絵は `cover_art.py` で変えられます。

## この本が原典に足したもの

四つの疲れという枠組み、心の疲れが倍率として効くという説明、約束事の在庫
（新品・定着中・自動）、連戦の削る順番と「体力×頭の余力」の掛け算、週の型
A〜D、日本の学校暦を三つの山として読む見方、道具9つ、四週間の実装順序。
いずれも原典には存在しません。詳細は `src/12-appendix.md` の「本書と原典の関係」。

原典の figure・表・写真・逐語訳は転載していません。

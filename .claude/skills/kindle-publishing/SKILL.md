---
name: kindle-publishing
description: |
  日本語のKindle実務書（KDP）を、参考資料から独自フレームワークで書き下ろし、
  EPUB・表紙3案・KDP入稿テキストまで一括で仕上げる制作パイプライン。
  発行元「フットボールパラダイム」のシリーズ体裁に合わせる。
  Use this skill whenever the user wants to write, produce, or publish a
  Kindle/KDP book in Japanese — including when they upload a PDF or report and
  ask "これで本が作れる?", ask for 原稿・EPUB・表紙・内容紹介・キーワード・
  KDPの入力値, want an existing manuscript rebuilt or retitled, or say things
  like 「Kindle本作りたい」「KDPに出したい」「電子書籍にして」「表紙作って」.
  Trigger it even when they only mention one piece (just the cover, just the
  blurb) — the pipeline's pieces share one config and stay consistent only if
  they run from here.
---

# KDP実務書の制作パイプライン

参考資料を渡されてから、KDPの入力欄が全部埋まるまでを一本の流れにしたもの。
出力は毎回同じ4つ——**原稿（EPUB＋Markdown）／表紙3案（JPEG）／KDP入力シート／
出品テキスト**。

## 最初に読む順番

1. このファイル（全体の流れと、外してはいけない原則）
2. `references/house-style.md` — シリーズの体裁。表紙・価格・命名・バッジ
3. `references/writing-playbook.md` — 独自フレームワークの作り方と章の型
4. `references/kdp-form.md` — KDP「本の詳細」画面の入力シート雛形

執筆に入る前に2と3は必ず読むこと。特に3は、この仕事で最も失敗しやすい部分
（下記「独自性の原則」）の具体的な手順が書いてある。

## 全体の流れ

```
資料を読む → 独自フレームを設計 → book.json → 章を書く
   → check_manuscript.py → build_epub.py → build_cover.py
   → KDP入力シート＋出品テキスト → 納品
```

### 1. 資料を読む

PDFなら `pdftotext` で全文を抜く。poppler が無ければ
`apt-get update && apt-get install -y poppler-utils`。

```bash
pdftotext source.pdf raw.txt
sed 's/[[:space:]]\+/ /g' raw.txt | grep -v '^$' > clean.txt
```

`-layout` は段組みが混ざるので、通し読みには素の抽出のほうが読みやすい。
**全部読む。** 要約で済ませると、後で「この数字はどの章の話か」が分からなくなり、
引用の精度が落ちる。1回の出力が大きすぎると切り捨てられるので、400〜600行ずつ
読み進める。

### 2. 独自フレームワークを設計する ← ここが勝負

**資料の目次を、そのまま本の骨格にしてはいけない。** それは解説書であって、
著書ではない。読者が「この人の本だ」と感じるのは、資料にはない切り口が
背骨になっているときだけ。

やること：資料から**事実・研究・事例**だけを取り出し、それを説明するための
**自分の枠組み**を新しく組む。枠組みには次を揃える。

- 覚えられる名前（「七つの関門」「三つの時計」など）
- 数を伴う構造（5つ／7つ。多すぎると覚えられない）
- 一段深い主張（なぜそれが起きるのか、という機序の説明）
- 名前のついた道具（読者が明日使えるもの。「割れ表」「月齢の鏡」など）

詳しい手順と、良い枠組みの見分け方は `references/writing-playbook.md`。

### 3. book.json を書く

全スクリプトがこの1ファイルを読む。ここが唯一の設定。

```json
{
  "slug": "eibun-no-file-mei",
  "title": "本のタイトル",
  "subtitle": "サブタイトル",
  "author": "フットボールパラダイム",
  "publisher": "フットボールパラダイム",
  "lang": "ja",
  "target_chars": 50000,
  "chapters": [
    ["00-hajimeni.md", "はじめに"],
    ["01-jyoshou.md", "序章 ..."]
  ],
  "cover": {
    "title_1": "タイトル前半",
    "title_2": "タイトル後半（大きく出る側）",
    "hook": "煽りの一行",
    "copy": ["補足コピー1行目", "2行目"],
    "badge": ["サッカー", "指導者に", "ひらめきを"],
    "badge_color": "#1B5FA8",
    "accent": "#F08A24",
    "diagram_labels": ["存在", "可視", "識別"],
    "diagram_numbers": ["100", "8"],
    "layouts": ["white", "navy", "diagram"]
  }
}
```

`title_1` / `title_2` はタイトルを2行に割ったもの。`title_2` が極太で大きく出る
ので、キーワードとして強い側を後半に置く。`diagram_*` は枠組みが段階モデルの
ときだけ使う（`diagram` レイアウトの図になる）。無ければドット図にフォールバック
するので省略してよい。

### 4. 章を書く

`src/` に1章1ファイル。**章の型を全章で揃えること**——揃っていると読者が
探し物をしやすく、書く側も迷わない。型は `references/writing-playbook.md`。

分量の目安は本文45,000〜55,000字。既刊より厚めで、¥450を正当化できる水準。

### 5. 検査してビルドする

```bash
python3 <skill>/scripts/check_manuscript.py book.json   # 先に必ず
python3 <skill>/scripts/build_epub.py     book.json
python3 <skill>/scripts/build_cover.py    book.json
```

- **check_manuscript.py** — 未置換のプレースホルダ、表記ゆれ、全角数字、
  他言語混入、章をまたぐ数値、章別文字数。人間の目が最も滑る種類の誤りを拾う
- **build_epub.py** — `build/<slug>.epub`（KDPに直接入稿可）と結合Markdown。
  タイトルページ・目次・`dc:publisher` 入り。標準ライブラリのみ
- **build_cover.py** — `cover/<slug>-<layout>.jpg` を1600×2560で。和文フォントは
  実際に使う文字だけをGoogle Fontsから取ってくるので、どんなタイトルでも化けない

いずれも `book.json` のあるディレクトリで実行する。

### 6. KDPの書類を作る

`references/kdp-form.md` を雛形に、実値を埋めた `kdp-form.md` と
`kdp-listing.md`（内容紹介・キーワード・カテゴリ・価格）を書く。
フリガナとローマ字は**毎回必要**で、忘れると入稿画面で止まる。

## 外してはいけない原則

### 独自性

骨格・道具・数値の解釈は自分で作る。資料からは事実と研究知見だけを借り、
**誰の研究か・どこの協会の実践かを名指しで**引く。「FIFAガイドによれば」で
段落を始める癖がついたら、それは解説書に戻っている合図。

### 著作権

参考資料の多くは複製を禁じている。逐語訳・図表の転載・章立てごとの要約はしない。
事実と数値そのものは著作権の対象ではないので、出典を示して引用してよい。
巻末に「本書と原典の関係」を1段落書き、**原典に存在しない要素**（枠組み、道具、
実装手順）を具体的に列挙する。これは読者への誠実さであり、自分の防御でもある。

### 日本の読者に向けて書く

海外の実践をそのまま紹介しても現場は動かない。各章に「日本の事情」の節を置き、
制度・慣行・季節の違いを踏まえて翻訳する。ここが本の価値の半分を作る。

### 人間が決めること

次は勝手に決めず、必ず本人に確認する。

- 表紙3案からどれを使うか
- 著者名を屋号にするか実名にするか
- 価格（推奨は出せる。決めるのは本人）
- KDPプレビューアでの実機確認（特に表が多い本）

## 出力の置き場所

```
<作業ディレクトリ>/
├── book.json
├── src/            章ごとのMarkdown
├── build/          EPUB と結合Markdown（生成物）
├── cover/          表紙JPEG（生成物）。.fonts/ はキャッシュ
├── kdp-form.md     KDP入力シート
└── kdp-listing.md  内容紹介・キーワード・価格
```

生成物（`build/` `cover/`）はgitに入れるかどうかを本人に聞く。原稿と
`book.json` は必ず残す——これがあれば全部作り直せる。

## つまずきやすいところ

**Markdownの改行** — 連続する行は1段落に連結される。奥付のように行を分けたい
ところは空行で区切る。

**表紙のタイトルが折り返す** — `title_1` が長すぎる。9文字を超えたら分割位置を
見直す。`.t1` は138px、`.t2` は214pxで、幅1392pxに収まる想定。

**フォントが落ちてこない** — ネットワークが無いと英数字だけ描画される。
`cover/.fonts/` にキャッシュが残っていれば再利用される。

**Chromiumが見つからない** — `CHROME=/path/to/chrome` を環境変数で渡す。

**EPUBのJPEG変換でPillowが無い** — `pip3 install Pillow`。

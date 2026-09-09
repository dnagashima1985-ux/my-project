# 才能を見落とさない七つの関門 — 原稿一式

副題：育成年代スカウティングの設計図
著／発行元：フットボールパラダイム

日本の育成現場向けに書き下ろしたオリジナルの実務書です。骨格は独自の
「七つの関門（存在・可視・識別・記録・合意・時間・回帰）」モデル。
FIFA『Talent Identification Guide』(© FIFA 2026) に収録された研究知見と
各国の実践は、出典を明記したうえで**証拠として引用**しています。

## 構成

```
book/
├── src/                        章ごとのMarkdown原稿（ここを編集する）
│   ├── 00-hajimeni.md          はじめに
│   ├── 01-jyoshou.md           序章 才能は、こぼれている（七関門モデル）
│   ├── 02-gate1-sonzai.md      第1関門 存在
│   ├── 03-gate2-kashi.md       第2関門 可視
│   ├── 04-gate3-shikibetsu.md  第3関門 識別
│   ├── 05-gate4-kiroku.md      第4関門 記録
│   ├── 06-gate5-goui.md        第5関門 合意
│   ├── 07-gate6-jikan.md       第6関門 時間
│   ├── 08-gate7-kaiki.md       第7関門 回帰
│   ├── 09-audit.md             第8章 監査（見落とし監査）
│   ├── 10-90days.md            第9章 90日の実装順序
│   ├── 11-shushou.md           終章
│   └── 12-appendix.md          付録A-C・出典・免責
├── kdp-form.md                 KDP入力シート（画面の項目順に貼る値）
├── kdp-listing.md              KDP出品用テキスト（内容紹介・キーワード・価格）
├── build_epub.py               EPUB3ビルドスクリプト（依存パッケージなし）
└── build/
    ├── nanatsu-no-kanmon.epub   KDPに直接アップロードできるEPUB
    └── nanatsu-no-kanmon.md     全章を結合した単一Markdown（Word取込用）
```

本文およそ51,500字（空白除く）／全13セクション（巻末に奥付あり）。

各章は共通の構成で書かれています——漏れの正体／証拠／日本の事情／塞ぎ方／
道具／測り方／現場ワーク。

## ビルド方法

```bash
python3 build_epub.py
```

`src/` のMarkdownを編集して再実行すれば、EPUBと結合Markdownが再生成されます。
Python標準ライブラリのみ使用。pandoc等は不要です。

## 表紙

`cover/` に3案あります（1600×2560px・JPEG、KDPにそのまま入稿可）。
**9つのレイアウトから、本ごとに違う3案**が自動で選ばれます（絵・図・文字から1つずつ）。別の3案が見たいときは `--seed 2` を付けて再実行します。

| ファイル | 案 |
|---|---|
| `cover/nanatsu-no-kanmon-stripe.jpg` | 絵：ユニフォームの縦縞 |
| `cover/nanatsu-no-kanmon-cycle.jpg` | 図：七つの関門を円環に、中央に100人 |
| `cover/nanatsu-no-kanmon-number.jpg` | 文字：巨大な「100」を薄く敷く |

```bash
python3 ~/.claude/skills/kindle-publishing/scripts/build_cover.py book.json
```

文言・色は `book.json` の `cover` で変えられます（title_1 / title_2 / hook /
copy / badge / diagram_labels / diagram_numbers / seed）。3案とも下部に帯を
敷き、発行元をタイトル上に小さく、シリーズバッジを置いています。

## KDPへの入稿

`kdp-form.md` が「Kindle 本の詳細」画面の項目順に並んだ入力シートです
（タイトル・フリガナ・ローマ字・レーベル・著者・カテゴリ・キーワードの
実値）。長文の内容紹介だけは `kdp-listing.md` にあります。

1. KDPで「電子書籍」を新規作成
2. `kdp-form.md` の値を上から順に転記（内容紹介は `kdp-listing.md` から）
3. 原稿ファイルに `build/nanatsu-no-kanmon.epub` をアップロード
4. 表紙 `cover/nanatsu-no-kanmon-*.jpg` から1案をアップロード
5. プレビューアで目次・表組み・奥付の表示を確認（表が多いので要チェック）
6. 価格 ¥450／70%ロイヤリティ／KDPセレクトを設定

Word原稿から進めたい場合は `build/nanatsu-no-kanmon.md` をWordに読み込み、
見出しスタイルを割り当ててから .docx として保存してください。

## 著作権についての注意

本原稿はFIFAガイドの翻訳・要約・再構成ではありません。七つの関門という枠組み、
残存率の掛け算という説明、各道具（三語の宣言／割れ表／月齢の鏡／戻り道リスト／
引き継ぎテスト／見落とし監査）、日本の育成構造への適用、90日の実装順序は、
いずれも同ガイドには存在せず、新たに構成したものです。

FIFAガイド本体は「出典明記とFIFAの許諾なしには部分的複製も禁止」と明記されて
いるため、原文の figure・表・写真・逐語訳は転載しないでください。
出典の記載は `src/12-appendix.md` にまとめてあります。

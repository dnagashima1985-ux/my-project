# 才能を見落とさない技術 — 原稿一式

FIFA『Talent Identification Guide』(© FIFA 2026) を土台に書き下ろした、
日本の育成現場向けオリジナル実務書の原稿です。

## 構成

```
book/
├── src/                     章ごとのMarkdown原稿（ここを編集する）
│   ├── 00-front.md          はじめに
│   ├── 01-intro.md          序章
│   ├── 02-ch1.md 〜 09-ch8.md  第1〜8章
│   ├── 10-outro.md          終章
│   └── 11-appendix.md       付録A-C・出典・免責
├── build_epub.py            EPUB3ビルドスクリプト（依存パッケージなし）
└── build/
    ├── talent-id-guide-ja.epub   KDPに直接アップロードできるEPUB
    └── talent-id-guide-ja.md     全章を結合した単一Markdown（Word取込用）
```

本文およそ55,000字（空白除く）／全12セクション。

## ビルド方法

```bash
python3 build_epub.py
```

`src/` のMarkdownを編集して再実行すれば、EPUBと結合Markdownが再生成されます。
Python標準ライブラリのみ使用。pandoc等は不要です。

## 出版前に決めること

`build_epub.py` の先頭にある定数を書き換えてください。

- `TITLE` / `SUBTITLE` — 書名（現在は仮題）
- `AUTHOR` — 著者名（現在 "著者名" のままです）

表紙画像はEPUBに含めていません。KDPの表紙クリエイターを使うか、
1600×2560px以上のJPG/TIFFを別途用意してアップロード時に指定してください。

## KDPへの入稿

1. KDPで「電子書籍」を新規作成
2. 原稿ファイルに `build/talent-id-guide-ja.epub` をアップロード
3. 表紙を設定し、プレビューアで目次と表組みの表示を確認
4. カテゴリは「スポーツ・アウトドア > サッカー」「ビジネス・経済 > マネジメント」あたり

Word原稿から進めたい場合は `build/talent-id-guide-ja.md` をWordに読み込み、
見出しスタイルを割り当ててから .docx として保存してください。

## 著作権についての注意

本原稿はFIFAガイドの翻訳・要約ではなく、その枠組みと公表された知見を
出典明記のうえ参照した独立の著作物です。FIFAガイド本体は
「出典明記とFIFAの許諾なしには部分的複製も禁止」と明記されているため、
原文の figure・表・写真・逐語訳を本書に転載しないでください。
出典の記載は `src/11-appendix.md` にまとめてあります。

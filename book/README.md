# 才能を見落とさない七つの関門 — 原稿一式

副題：育成年代スカウティングの設計図／著：フットボールパラダイム

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
├── build_epub.py               EPUB3ビルドスクリプト（依存パッケージなし）
└── build/
    ├── nanatsu-no-kanmon.epub   KDPに直接アップロードできるEPUB
    └── nanatsu-no-kanmon.md     全章を結合した単一Markdown（Word取込用）
```

本文およそ51,000字（空白除く）／全13セクション。

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
既刊シリーズの体裁——フラットな色面、極太ゴシックの2行タイトル、
タイトル脇に小さく著者名、下部に煽りコピー、右下にギザギザの
シリーズバッジ「サッカー指導者にひらめきを」——に合わせています。

| ファイル | 案 |
|---|---|
| `cover/cover-a-navy.jpg` | 紺地×オレンジ。整列したドットが崩れて落ちる |
| `cover/cover-b-white.jpg` | 生成り地×黒＋オレンジ。既刊に最も近い |
| `cover/cover-c-gates.jpg` | 生成り地×紺。七関門の図解（100→8） |

```bash
cd cover && python3 build_covers.py   # out/ に再生成
```

文言・色は `cover/build_covers.py` 冒頭の定数（TITLE_1 / TITLE_2 /
SUBTITLE / AUTHOR / HOOK / COPY_1 / COPY_2 / BADGE）で変更できます。
和文フォント（Noto Sans JP のサブセット）は `cover/fonts/` に同梱、
描画は同梱のChromium、書き出しはPillowで、外部サービスは不要です。

## KDPへの入稿

1. KDPで「電子書籍」を新規作成
2. 原稿ファイルに `build/nanatsu-no-kanmon.epub` をアップロード
3. 表紙を設定し、プレビューアで目次と表組みの表示を確認
4. カテゴリは「スポーツ・アウトドア > サッカー」「ビジネス・経済 > マネジメント」あたり

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

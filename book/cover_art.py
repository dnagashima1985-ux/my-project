# -*- coding: utf-8 -*-
"""『才能を見落とさない七つの関門』の表紙——タイトルから起こした3案。

サムネイルで「サッカーの本」と分かることを優先し、絵の主役は必ず
ゴール・ボール・ピッチのどれかにしてある。

- goals : 「七つの関門」を、奥へ小さくなる7つのゴールとボールの数で
- onepanel : 「見落とさない」を、1枚だけ色の違うパネルを持つ巨大なボールで
- sheet : 「見落とさない仕組み」を、ピッチ図つきの観察票そのもので
"""

CAPTION = "その一人は、いつも同じ場所にいる"


def goals(cfg, P, S):
    """ゴールを7つ。くぐるたびに枠が小さくなり、通るボールが減る。"""
    FB = S["fb"]
    ink, accent = P["ink"], P["accent"]
    labels = [l for l in (cfg.get("diagram_labels") or []) if l][:7]
    counts = [9, 8, 6, 5, 4, 3, 2]
    out = []
    # 枠の高さ＋ボール1列が step に収まるように。詰めるとボールが次の枠に乗る
    top, step = 108, 150
    for i in range(7):
        w = 1200 - i * 152
        h = 92 - i * 6
        y = top + i * step
        out.append(FB.goal(800, y, w, h, color=ink, lw=max(5, 11 - i),
                           net=max(14, 30 - i * 2),
                           net_opacity="%.2f" % (0.5 - i * 0.05)))
        if i < len(labels):
            out.append('<text x="%.0f" y="%d" fill="%s" font-size="32" '
                       'font-family="NSJP" font-weight="700" text-anchor="end" '
                       'opacity=".85">%s</text>'
                       % (800 - w / 2 - 20, y + h * 0.7, ink, labels[i]))
        n, last = counts[i], i == 6
        for k in range(n):
            cx = 800 + (k - (n - 1) / 2.0) * (w / (n + 0.6))
            r = 24 - i * 1.5
            out.append(FB.ball(cx, y + h + 32, r,
                               light="#FFFFFF" if not last else accent,
                               dark="#16161A"))
    nums = cfg.get("diagram_numbers") or ["", ""]
    out.append('<text x="1500" y="72" fill="%s" font-size="58" '
               'font-family="NSJP" font-weight="900" text-anchor="end">%s</text>'
               % (accent, nums[0]))
    out.append('<text x="800" y="1160" fill="%s" font-size="58" '
               'font-family="NSJP" font-weight="900" text-anchor="middle">%s'
               '</text>' % (accent, nums[1] if len(nums) > 1 else ""))
    return "".join(out)


def onepanel(cfg, P, S):
    """画面いっぱいのボール。黒い面がひとつだけ色違い——見落とされている一人。"""
    FB, W = S["fb"], S["W"]
    cx, cy, r = 800, 520, 486
    out = ['<circle cx="%d" cy="%d" r="%d" fill="%s" opacity=".4"/>'
           % (cx + 24, cy + 28, r, S["mix"](P["bg"], "#000000", .45))]
    out.append(FB.ball_detail(cx, cy, r, mark=3, mark_color=P["accent"]))
    out.append('<text x="%d" y="1120" fill="%s" font-size="44" '
               'font-family="NSJP" font-weight="900" text-anchor="middle" '
               'opacity=".92">%s</text>' % (W / 2, P["ink"], CAPTION))
    return "".join(out)


# 票の行。glyphs 宣言と本文で同じ文字列を使う（字形の取り寄せ漏れを防ぐ）
ROWS = ["いま何ができるか", "1年後はどうか", "体はどの段階か",
        "次に注目する点", "もう一度観るか"]


def sheet(cfg, P, S):
    """クリップボードの観察票。中にピッチ図があるので、一目でサッカー。"""
    FB, W, mix = S["fb"], S["W"], S["mix"]
    ink, accent = P["ink"], P["accent"]
    out = [FB.grass(W, 1180, P["bg"], mix(P["bg"], "#000000", .10), bands=9)]
    out.append(FB.clipboard(250, 70, 1100, 1020, board="#B9843F",
                            paper="#FFFFFF", ink="#2B2B2F"))
    out.append('<text x="800" y="252" fill="#16161A" font-size="52" '
               'font-family="NSJP" font-weight="900" text-anchor="middle">'
               '一枚の観察票</text>')
    out.append('<line x1="318" y1="286" x2="1282" y2="286" stroke="%s" '
               'stroke-width="4"/>' % accent)
    # 票の中のピッチ図
    out.append('<rect x="318" y="320" width="420" height="560" fill="none" '
               'stroke="#16161A" stroke-width="4"/>')
    out.append('<line x1="318" y1="600" x2="738" y2="600" stroke="#16161A" '
               'stroke-width="4"/>')
    out.append('<circle cx="528" cy="600" r="72" fill="none" stroke="#16161A" '
               'stroke-width="4"/>')
    for x, y in [(528, 360), (400, 460), (656, 460), (528, 520), (430, 700),
                 (626, 700), (528, 830)]:
        out.append('<circle cx="%d" cy="%d" r="17" fill="#16161A"/>' % (x, y))
    out.append('<circle cx="528" cy="520" r="26" fill="none" stroke="%s" '
               'stroke-width="6"/>' % accent)
    rows = ROWS
    for i, label in enumerate(rows):
        y = 380 + i * 118
        hot = i == len(rows) - 1
        if hot:
            out.append('<rect x="782" y="%d" width="500" height="92" fill="%s" '
                       'opacity=".14"/>' % (y - 56, accent))
        out.append('<text x="792" y="%d" fill="#16161A" font-size="34" '
                   'font-family="NSJP" font-weight="700">%s</text>'
                   % (y, label))
        for k in range(4):
            cx = 1090 + k * 52
            out.append('<rect x="%d" y="%d" width="34" height="34" fill="%s" '
                       'stroke="#16161A" stroke-width="3"/>'
                       % (cx, y - 28, accent if (hot and k == 2) else "#FFFFFF"))
        out.append('<line x1="792" y1="%d" x2="1282" y2="%d" stroke="#16161A" '
                   'stroke-width="2" opacity=".3"/>' % (y + 26, y + 26))
    out.append(FB.ball(1418, 1044, 74, light="#FFFFFF", dark="#16161A"))
    return "".join(out)


ARTS = [
    {"name": "goals", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#10233A", "#0A1626", "#FFFFFF", "#F08A24", "#FFFFFF",
                 "#0A1626", "#C0392B", None),
     "svg": goals},
    {"name": "onepanel", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "glyphs": CAPTION,
     "palette": ("#0E1116", "#0E1116", "#FFFFFF", "#F08A24", "#F08A24",
                 "#0E1116", "#C0392B", None),
     "svg": onepanel},
    {"name": "sheet", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "glyphs": "一枚の観察票" + "".join(ROWS),
     "palette": ("#1B6E4A", "#16161A", "#FFFFFF", "#1B5FA8", "#1B5FA8",
                 "#FFFFFF", "#C0392B", None),
     "svg": sheet},
]

# -*- coding: utf-8 -*-
"""『連戦で壊れない週の設計図』の表紙——タイトルから起こした3案。

モチーフを画面いっぱいに置き、色面で割る。図を小さく並べない。

- crackball : 「壊れない」の逆。ひびの入った巨大なボール
- netshot   : ネットに突き刺さる瞬間。ゴール裏からの視界
- splitweek : ふだんの週と大会の週を、斜めの色面で二分する
"""

TOP_ROW = "ふだんの週　中3日"
BOTTOM_ROW = "大会の週　中1日"


def crackball(cfg, P, S):
    """黒地に、画面をはみ出す大きさのボール。そこへ一本のひび。"""
    FB, W = S["fb"], S["W"]
    accent = P["accent"]
    cx, cy, r = 800, 520, 486
    out = ['<circle cx="%d" cy="%d" r="%d" fill="%s" opacity=".35"/>'
           % (cx + 26, cy + 30, r, S["mix"](P["bg"], "#000000", .5))]
    out.append(FB.ball_detail(cx, cy, r))
    out.append(FB.crack(cx, cy, r, color=accent, lw=18))
    out.append('<text x="%d" y="1122" fill="%s" font-size="44" '
               'font-family="NSJP" font-weight="900" text-anchor="middle" '
               'opacity=".9">%s</text>' % (W / 2, P["ink"], "壊れるのは、いつも連戦の終わり"))
    return "".join(out)


def netshot(cfg, P, S):
    """ゴール裏からの視界。ネット越しに、突き刺さったボールを見る。"""
    FB, W = S["fb"], S["W"]
    out = [FB.net_field(W, 1180, step=132, color=P["ink"], opacity=".40",
                        lw=5, skew=1180, horizontals=False)]  # 高さぶん振ると45度
    cx, cy, r = 800, 600, 268
    out.append('<circle cx="%d" cy="%d" r="%d" fill="%s" opacity=".45"/>'
               % (cx, cy, int(r * 1.5), S["mix"](P["bg"], "#000000", .35)))
    out.append(FB.impact(cx, cy, r, color=P["accent"], lw=11, rays=9,
                         arc=(20, 160)))   # 押し込まれた下側だけ
    out.append(FB.ball_detail(cx, cy, r))
    return "".join(out)


def splitweek(cfg, P, S):
    """斜めに割った色面。上はふだんの週、下は大会の週。ボールの間隔で語る。"""
    FB, W, mix = S["fb"], S["W"], S["mix"]
    top_bg, bottom_bg = "#F1EDE4", P["accent"]
    out = [FB.split_diagonal(W, 1180, top_bg, bottom_bg, 560, 760)]

    def y_at(x, y0):                                 # 斜めの色面と平行に並べる
        return y0 + (x - 210) * 0.125

    for m in [0, 4, 8, 12]:                          # ふだんの週：等間隔
        x = 210 + 1180 * m / 12.0
        out.append(FB.ball(x, y_at(x, 300), 52, light="#FFFFFF", dark="#16161A"))
    out.append('<text x="120" y="150" fill="#16161A" font-size="52" '
               'font-family="NSJP" font-weight="900">%s</text>' % TOP_ROW)

    for m in [0, 3.4, 6.2, 8.4, 10.1, 11.4]:         # 大会の週：詰まっていく
        x = 210 + 1180 * m / 12.0
        out.append(FB.ball(x, y_at(x, 880), 52, light="#FFFFFF", dark="#16161A"))
    out.append('<text x="1480" y="1112" fill="#FFFFFF" font-size="52" '
               'font-family="NSJP" font-weight="900" text-anchor="end">%s</text>'
               % BOTTOM_ROW)
    return "".join(out)


ARTS = [
    {"name": "crackball", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "glyphs": "壊れるのはいつも連戦の終わり",
     "palette": ("#0E1116", "#0E1116", "#FFFFFF", "#F2A33A", "#F2A33A",
                 "#0E1116", "#C0392B", None),
     "svg": crackball},
    {"name": "netshot", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#0F5A52", "#0A322D", "#FFFFFF", "#F2C230", "#F2C230",
                 "#0A322D", "#C0392B", None),
     "svg": netshot},
    {"name": "splitweek", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "glyphs": TOP_ROW + BOTTOM_ROW,
     "palette": ("#F1EDE4", "#16161A", "#FFFFFF", "#C0392B", "#C0392B",
                 "#FFFFFF", "#16161A", "#DCD6C8"),
     "svg": splitweek},
]

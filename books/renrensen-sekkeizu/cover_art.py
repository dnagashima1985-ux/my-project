# -*- coding: utf-8 -*-
"""『連戦で壊れない週の設計図』の表紙——タイトルから起こした3案。

サムネイルで「サッカーの本」と分かることを優先し、絵の主役は必ず
ピッチ・ゴール・ボール・ユニフォームのどれかにしてある。

- matchweek : 「週の設計図」を、ゴール前の芝に並べた7つのボールで
- congestion: 「連戦」を、詰まっていく試合＝ボールの並びで
- kits      : 「疲れは、一種類ではない」を、4枚のユニフォームの背番号で
"""


def matchweek(cfg, P, S):
    """ゴール前の芝に、月曜から日曜までのボールが7つ並ぶ。土曜が試合。"""
    FB, W = S["fb"], S["W"]
    ink, accent = P["ink"], P["accent"]
    out = [FB.grass(W, 1180, P["bg"], S["mix"](P["bg"], "#000000", .10), bands=10)]
    out.append(FB.goal(800, 96, 700, 250, color=ink, lw=14, net=30))
    out.append(FB.penalty_area(800, 346, w=1300, h=280, color=ink, lw=8,
                               spot=False))

    days = ["月", "火", "水", "木", "金", "土", "日"]
    md = ["MD-5", "MD-4", "MD-3", "MD-2", "MD-1", "MD", "OFF"]
    left, gap, y = 168, 212, 820
    for i, day in enumerate(days):
        cx = left + i * gap
        match = i == 5
        r = 62 if match else 44
        if match:
            out.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
                       'stroke-width="9"/>' % (cx, y, r + 26, accent))
        out.append(FB.ball(cx, y, r, light="#FFFFFF" if match else "#EFEFEA",
                           dark="#16161A"))
        out.append('<text x="%d" y="%d" fill="%s" font-size="46" '
                   'font-family="NSJP" font-weight="900" text-anchor="middle">'
                   '%s</text>' % (cx, y - 108, ink, day))
        out.append('<text x="%d" y="%d" fill="%s" font-size="28" '
                   'font-family="NSJP" font-weight="700" text-anchor="middle" '
                   'opacity=".8">%s</text>'
                   % (cx, y + 118, accent if match else ink, md[i]))
    x1, x2 = left + 3 * gap, left + 5 * gap
    out.append('<g stroke="%s" stroke-width="5">' % accent)
    out.append('<line x1="%d" y1="1046" x2="%d" y2="1046"/>' % (x1, x2))
    for x in (x1, x2):
        out.append('<line x1="%d" y1="1022" x2="%d" y2="1070"/>' % (x, x))
    out.append("</g>")
    out.append('<text x="%d" y="1122" fill="%s" font-size="44" '
               'font-family="NSJP" font-weight="900" text-anchor="middle">'
               '48時間</text>' % ((x1 + x2) / 2, accent))
    return "".join(out)


def congestion(cfg, P, S):
    """タッチラインを時間軸に。ふだんの週の上に、大会の週を重ねて見せる。"""
    FB, W = S["fb"], S["W"]
    ink, accent = P["ink"], P["accent"]
    out = [FB.grass(W, 1180, P["bg"], S["mix"](P["bg"], "#000000", .10), bands=10)]
    base, span = 190, 1230

    def row(y, matches, label, hot_from=None):
        o = ['<text x="%d" y="%d" fill="%s" font-size="46" font-family="NSJP" '
             'font-weight="900">%s</text>' % (base - 20, y - 150, ink, label)]
        o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
                 'stroke-width="7" opacity=".8"/>'
                 % (base, y, base + span, y, ink))
        xs = [base + span * m / 14.0 for m in matches]
        for i, x in enumerate(xs):
            hot = hot_from is not None and i >= hot_from
            if hot:
                o.append('<circle cx="%.0f" cy="%d" r="60" fill="none" '
                         'stroke="%s" stroke-width="8"/>' % (x, y, accent))
            o.append(FB.ball(x, y, 42, light="#FFFFFF", dark="#16161A"))
        for i in range(len(xs) - 1):
            gap = matches[i + 1] - matches[i] - 1
            hot = hot_from is not None and i + 1 >= hot_from
            col = accent if hot else ink
            o.append('<text x="%.0f" y="%d" fill="%s" font-size="40" '
                     'font-family="NSJP" font-weight="900" text-anchor="middle">'
                     '中%d日</text>' % ((xs[i] + xs[i + 1]) / 2, y - 74, col, gap))
        return "".join(o)

    out.append(row(400, [0, 4, 8, 12], "ふだんの週"))
    out.append(row(880, [0, 4, 7, 9, 11, 12], "大会の週", hot_from=3))
    out.append('<text x="%d" y="1030" fill="%s" font-size="46" '
               'font-family="NSJP" font-weight="900" text-anchor="end">'
               'ここで壊れる</text>' % (base + span + 30, accent))
    return "".join(out)


def kits(cfg, P, S):
    """4枚のユニフォーム。背番号は、その疲れが戻るまでの時間。"""
    FB, W = S["fb"], S["W"]
    ink, accent = P["ink"], P["accent"]
    out = [FB.grass(W, 1180, P["bg"], S["mix"](P["bg"], "#000000", .09), bands=10)]
    out.append(FB.touchline(1104, color=ink, lw=7, W=W, corner=88, side="up"))
    rows = [("筋", "72", "48〜72時間"), ("神経", "48", "24〜48時間"),
            ("頭", "12", "半日〜1日"), ("心", "∞", "数日〜数週")]
    cxs = [292, 646, 1000, 1354]   # 袖が触れない間隔
    for (name, num, when), cx in zip(rows, cxs):
        hot = name == "心"
        out.append(FB.shirt(cx, 300, 192, 320,
                            fill=accent if hot else "#F5F2EC",
                            stroke="#16161A", lw=7,
                            number=num, number_color="#16161A", font=118))
        out.append('<text x="%d" y="%d" fill="%s" font-size="52" '
                   'font-family="NSJP" font-weight="900" text-anchor="middle">'
                   '%s</text>' % (cx, 726, ink, name))
        out.append('<text x="%d" y="%d" fill="%s" font-size="30" '
                   'font-family="NSJP" font-weight="700" text-anchor="middle" '
                   'opacity=".82">%s</text>' % (cx, 776, ink, when))
    out.append('<text x="%d" y="%d" fill="%s" font-size="40" font-family="NSJP" '
               'font-weight="700" text-anchor="middle" opacity=".9">'
               '背番号は、戻るまでの時間</text>' % (W / 2, 900, ink))
    return "".join(out)


ARTS = [
    {"name": "matchweek", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#146B45", "#0B3A26", "#FFFFFF", "#F2A33A", "#FFFFFF",
                 "#0B3A26", "#C0392B", None),
     "svg": matchweek},
    {"name": "congestion", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#0F5233", "#101418", "#FFFFFF", "#F2C230", "#F2C230",
                 "#101418", "#C0392B", None),
     "svg": congestion},
    {"name": "kits", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#12603E", "#123B6D", "#FFFFFF", "#F08A24", "#FFFFFF",
                 "#123B6D", "#C0392B", None),
     "glyphs": "∞背号戻時間", "svg": kits},
]

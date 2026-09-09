# -*- coding: utf-8 -*-
"""『連戦で壊れない週の設計図』の表紙——タイトルから起こした3案。

- blueprint : 「週の設計図」を、そのまま青焼きの図面にする
- congestion: 「連戦」を、間隔が詰まっていく試合の並びで見せる
- curves    : 「疲れは、一種類ではない」を、戻り方の違う4本の線で見せる

build_cover.py が ARTS を読んで、この3案を表紙にする。
"""


def blueprint(cfg, P, S):
    W, mix = S["W"], S["mix"]
    ink, accent = P["ink"], P["accent"]
    out = []
    for x in range(0, W, 80):                       # 方眼
        out.append('<line x1="%d" y1="0" x2="%d" y2="1180" stroke="%s" '
                   'stroke-width="2" opacity=".10"/>' % (x, x, ink))
    for y in range(0, 1180, 80):
        out.append('<line x1="0" y1="%d" x2="%d" y2="%d" stroke="%s" '
                   'stroke-width="2" opacity=".10"/>' % (y, W, y, ink))

    days = ["月", "火", "水", "木", "金", "土", "日"]
    md = ["MD-5", "MD-4", "MD-3", "MD-2", "MD-1", "MD", "OFF"]
    # 練習日は白の面、試合日だけアクセント。オレンジを薄く敷くと濁る
    load = [0, .16, 0, .16, .07, "match", 0]        # 土曜が試合
    left, colw, gap = 150, 172, 15
    for i, day in enumerate(days):
        x = left + i * (colw + gap)
        if load[i] == "match":
            fill = 'fill="%s"' % accent
        elif load[i]:
            fill = 'fill="%s" fill-opacity="%.2f"' % (ink, load[i])
        else:
            fill = 'fill="none"'
        out.append('<rect x="%d" y="360" width="%d" height="360" %s '
                   'stroke="%s" stroke-width="3"/>' % (x, colw, fill, ink))
        out.append('<text x="%d" y="322" fill="%s" font-size="46" '
                   'font-family="NSJP" font-weight="700" text-anchor="middle">'
                   '%s</text>' % (x + colw / 2, ink, day))
        out.append('<text x="%d" y="768" fill="%s" font-size="26" '
                   'font-family="NSJP" font-weight="400" text-anchor="middle" '
                   'opacity=".72">%s</text>' % (x + colw / 2, ink, md[i]))

    # 寸法線：木（MD-2）から土（MD）まで48時間
    x1 = left + 3 * (colw + gap) + colw / 2
    x2 = left + 5 * (colw + gap) + colw / 2
    out.append('<g stroke="%s" stroke-width="3">' % accent)
    out.append('<line x1="%.0f" y1="856" x2="%.0f" y2="856"/>' % (x1, x2))
    for x in (x1, x2):
        out.append('<line x1="%.0f" y1="828" x2="%.0f" y2="884"/>' % (x, x))
    out.append("</g>")
    out.append('<text x="%.0f" y="838" fill="%s" font-size="40" '
               'font-family="NSJP" font-weight="900" text-anchor="middle">'
               '48時間</text>' % ((x1 + x2) / 2, accent))

    # 図面の表題欄
    out.append('<rect x="1096" y="112" width="364" height="132" fill="none" '
               'stroke="%s" stroke-width="3" opacity=".8"/>' % ink)
    out.append('<line x1="1096" y1="180" x2="1460" y2="180" stroke="%s" '
               'stroke-width="2" opacity=".8"/>' % ink)
    out.append('<text x="1116" y="162" fill="%s" font-size="30" '
               'font-family="NSJP" font-weight="700">WEEK PLAN</text>' % ink)
    out.append('<text x="1116" y="222" fill="%s" font-size="26" '
               'font-family="NSJP" opacity=".72">SCALE 1 WEEK</text>' % ink)
    return "".join(out)


def congestion(cfg, P, S):
    """ふだんの週と、連戦の週を上下に並べる。間隔が詰まっていくのが主役。"""
    art = S["art"]
    ink, accent = art(P, .9), P["accent"]
    faint = art(P, .35)
    base, span = 210, 1230

    def row(y, matches, label, hot_from=None):
        # 行の名前は、間隔ラベル（y-96）よりさらに上に置く。同じ高さだと重なる
        out = ['<text x="%d" y="%d" fill="%s" font-size="46" font-family="NSJP" '
               'font-weight="900">%s</text>' % (base - 30, y - 178, ink, label)]
        out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
                   'stroke-width="8"/>' % (base, y, base + span, y, faint))
        for i in range(15):
            x = base + span * i / 14.0
            out.append('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d" stroke="%s" '
                       'stroke-width="4"/>' % (x, y - 18, x, y + 18, faint))
        xs = [base + span * m / 14.0 for m in matches]
        for i, x in enumerate(xs):
            hot = hot_from is not None and i >= hot_from
            out.append('<circle cx="%.0f" cy="%d" r="44" fill="%s"/>'
                       % (x, y, accent if hot else ink))
        for i in range(len(xs) - 1):
            gap = matches[i + 1] - matches[i] - 1
            hot = hot_from is not None and i + 1 >= hot_from
            col = accent if hot else ink
            mx = (xs[i] + xs[i + 1]) / 2
            out.append('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d" stroke="%s" '
                       'stroke-width="4"/>'
                       % (xs[i] + 54, y - 74, xs[i + 1] - 54, y - 74, col))
            out.append('<text x="%.0f" y="%d" fill="%s" font-size="42" '
                       'font-family="NSJP" font-weight="900" '
                       'text-anchor="middle">中%d日</text>' % (mx, y - 96, col, gap))
        return "".join(out)

    out = [row(430, [0, 4, 8, 12], "ふだんの週")]
    out.append(row(900, [0, 4, 7, 9, 11, 12], "大会の週", hot_from=3))
    out.append('<text x="%d" y="%d" fill="%s" font-size="44" font-family="NSJP" '
               'font-weight="900" text-anchor="end">ここで壊れる</text>'
               % (base + span, 1030, accent))
    return "".join(out)


def curves(cfg, P, S):
    W, art = S["W"], S["art"]
    ink, accent = art(P, .92), P["accent"]
    faint = art(P, .3)
    top, base, x0 = 300, 940, 240
    out = ['<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
           'stroke-width="3" stroke-dasharray="14 12"/>'
           % (120, base, 1500, base, faint)]
    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
               'stroke-width="5"/>' % (x0, top - 40, x0, base + 40, faint))
    out.append('<text x="%d" y="%d" fill="%s" font-size="38" font-family="NSJP" '
               'font-weight="700" text-anchor="middle">試合</text>'
               % (x0, top - 66, ink))

    rows = [("頭", "半日〜1日", 560, .55), ("神経", "24〜48時間", 800, .70),
            ("筋", "48〜72時間", 1080, .85), ("心", "数日〜数週", 1420, 1.0)]
    for name, when, end, weight in rows:
        col = accent if name == "心" else ink
        w = 9 if name == "心" else 7
        op = 1.0 if name == "心" else .45 + weight * .35
        out.append('<path d="M%d %d C%.0f %d %.0f %d %d %d" fill="none" '
                   'stroke="%s" stroke-width="%d" opacity="%.2f"/>'
                   % (x0, top, x0 + (end - x0) * .55, top,
                      x0 + (end - x0) * .55, base, end, base, col, w, op))
        out.append('<circle cx="%d" cy="%d" r="12" fill="%s" opacity="%.2f"/>'
                   % (end, base, col, op))
        out.append('<text x="%d" y="%d" fill="%s" font-size="42" '
                   'font-family="NSJP" font-weight="900" text-anchor="middle" '
                   'opacity="%.2f">%s</text>' % (end, base + 66, col, op, name))
        out.append('<text x="%d" y="%d" fill="%s" font-size="28" '
                   'font-family="NSJP" font-weight="400" text-anchor="middle" '
                   'opacity="%.2f">%s</text>'
                   % (end, base + 112, col, op * .8, when))
    out.append('<text x="%d" y="%d" fill="%s" font-size="34" font-family="NSJP" '
               'font-weight="700" opacity=".75">戻るまでの速さ</text>'
               % (1180, top + 30, ink))
    return "".join(out)


ARTS = [
    {"name": "blueprint", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#0E2E5A", "#0A2145", "#FFFFFF", "#F2A33A", "#FFFFFF",
                 "#0A2145", "#C0392B", None),
     "svg": blueprint},
    {"name": "congestion", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#F5F2EC", "#16161A", "#FFFFFF", "#C0392B", "#C0392B",
                 "#FFFFFF", "#16161A", "#DCD6C8"),
     "svg": congestion},
    {"name": "curves", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#101820", "#0A1017", "#FFFFFF", "#F2A33A", "#F2A33A",
                 "#0A1017", "#1B5FA8", None),
     "svg": curves},
]

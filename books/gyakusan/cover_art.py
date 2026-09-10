# -*- coding: utf-8 -*-
"""『一週間を逆算する』の表紙——タイトルから起こした3案。

タイトルが試合から逆算した日の呼び名なので、絵は「並び」と「逆算」で作る。
看板は「週」。MD表記は絵の中に置いて、逆算のカウントダウンを見せる。

- row   : ボールが横一列。MD-2に輪、MDは色が違う
- cones : 芝に立つコーン。MD-2だけ高くてオレンジ
- swap  : 上と下で同じ7個。2つ入れ替えただけで週が変わる
"""

DAYS = ["MD-5", "MD-4", "MD-3", "MD-2", "MD-1", "MD", "OFF"]
SWAP_CAPTION = "入れ替えただけ。中身は同じ"
CONE_CAPTION = "置く日を変えると、強くなる"


def row(cfg, P, S):
    """ボール5個の一列。両端は断ち落とす。試合の日だけがオレンジの輪。

    7個並べるとサムネイルでは粒になる。5個まで減らして大きくした。
    """
    FB, W = S["fb"], S["W"]
    ink, accent = P["ink"], P["accent"]
    # 左端の1個だけ断ち落として、週が続いていることを見せる。右端は輪ごと収める
    y, r, step = 520, 168, 366
    labels = ["", "MD-3", "MD-2", "MD-1", "MD"]
    out = []
    for i in range(5):
        cx = -100 + i * step
        if i == 2:                                   # 表紙の主役、MD-2
            out.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
                       'stroke-width="18"/>' % (cx, y, r + 46, accent))
        out.append(FB.ball(cx, y, r,
                           light=accent if i == 4 else "#FFFFFF"))
        if labels[i]:
            out.append('<text x="%d" y="%d" fill="%s" font-size="54" '
                       'font-family="NSJP" font-weight="900" text-anchor="middle" '
                       'opacity="%s">%s</text>'
                       % (cx, y + r + 140, accent if i == 2 else ink,
                          "1" if i == 2 else ".8", labels[i]))
    out.append(FB.touchline(1010, color=ink, lw=8, W=W, corner=104))
    return "".join(out)


def cones(cfg, P, S):
    """練習の記号はコーン。7本のうち2本だけが強度の日。"""
    FB, W, mix = S["fb"], S["W"], S["mix"]
    ink, accent = P["ink"], P["accent"]
    out = [FB.grass(W, 1180, P["bg"], mix(P["bg"], "#000000", .10), bands=9)]
    line_y = 860                                     # コーンはこの線の上に立つ
    out.append(FB.touchline(line_y, color=ink, lw=8, W=W, corner=104))
    out.append(FB.ball(1336, 300, 112))
    base, step = 200, 200
    for i in range(7):
        cx = base + i * step
        hot = i == 3            # MD-2
        out.append(FB.cone(cx, line_y, h=290 if hot else 200,
                           color=accent if hot else "#F5F2EC",
                           dark=mix(P["bg"], "#000000", .35)))
        out.append('<text x="%d" y="%d" fill="%s" font-size="50" '
                   'font-family="NSJP" font-weight="900" text-anchor="middle" '
                   'opacity="%s">%s</text>'
                   % (cx, line_y + 90, accent if hot else ink,
                      "1" if hot else ".72", DAYS[i]))
    out.append('<text x="120" y="1104" fill="%s" font-size="48" '
               'font-family="NSJP" font-weight="900" opacity=".92">%s</text>'
               % (ink, CONE_CAPTION))
    return "".join(out)


def swap(cfg, P, S):
    """同じ7個を、2つだけ入れ替える。それだけで週の意味が変わる。"""
    FB, W = S["fb"], S["W"]
    ink, accent = "#16161A", P["accent"]
    base, step, r = 220, 194, 74
    top_y, bottom_y = 330, 880
    out = []
    for i in range(7):
        cx = base + i * step
        out.append('<g opacity=".38">%s</g>' % FB.ball(cx, top_y, r))
    out.append('<text x="%d" y="%d" fill="%s" font-size="40" '
               'font-family="NSJP" font-weight="900" opacity=".55">'
               'いつもの並び</text>' % (base - 40, top_y - 118, ink))

    swapped = {2: accent, 4: accent}
    for i in range(7):
        cx = base + i * step
        if i in swapped:
            out.append('<circle cx="%d" cy="%d" r="%d" fill="%s"/>'
                       % (cx, bottom_y, r + 22, swapped[i]))
        out.append(FB.ball(cx, bottom_y, r))
    x2, x4 = base + 2 * step, base + 4 * step
    out.append(FB.arrow_curve(x2, top_y + r + 34, x4, bottom_y - r - 40,
                              color=accent, lw=10, bow=0.16))
    out.append(FB.arrow_curve(x4, top_y + r + 34, x2, bottom_y - r - 40,
                              color=accent, lw=10, bow=0.16))
    out.append('<text x="%d" y="%d" fill="%s" font-size="46" '
               'font-family="NSJP" font-weight="900">%s</text>'
               % (base - 40, bottom_y + r + 96, ink, SWAP_CAPTION))
    return "".join(out)


ARTS = [
    {"name": "row", "text": "big", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "glyphs": "".join(DAYS) + "MD-012345",
     "palette": ("#0E1116", "#0E1116", "#FFFFFF", "#F2A33A", "#F2A33A",
                 "#0E1116", "#C0392B", None),
     "svg": row},
    {"name": "cones", "text": "big", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "glyphs": "".join(DAYS) + CONE_CAPTION + "MD-012345",
     "palette": ("#12603E", "#0B3A26", "#FFFFFF", "#F08A24", "#FFFFFF",
                 "#0B3A26", "#C0392B", None),
     "svg": cones},
    {"name": "swap", "text": "big", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "glyphs": SWAP_CAPTION + "いつもの並び",
     "palette": ("#F1EDE4", "#16161A", "#FFFFFF", "#C0392B", "#C0392B",
                 "#FFFFFF", "#16161A", "#DCD6C8"),
     "svg": swap},
]

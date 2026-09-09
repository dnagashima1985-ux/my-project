# -*- coding: utf-8 -*-
"""SVGでサッカーの部品を描く小さな道具箱。表紙の絵はここから組み立てる。

表紙は180pxのサムネイルで「サッカーの本だ」と分かる必要がある。抽象的な図表を
描くと、内容は正確でもジャンルが伝わらない。ボール・ゴール・ネット・白線・芝は
その距離で効く数少ない記号なので、毎回どれかを絵の主役に置く。

すべて SVG の断片（文字列）を返す。cover_art.py から FB.ball(...) のように呼ぶ。
"""

import math


def ball(cx, cy, r, light="#FFFFFF", dark="#16161A", lw=None):
    """サッカーボール。小さいときは記号として、大きいときは球として描く。"""
    # 小さいうちは記号のほうが読める。細かく描くと車輪に見える境目がここ
    if r >= 110:
        return ball_detail(cx, cy, r, light=light, dark=dark)
    lw = lw if lw is not None else max(2.0, r * 0.09)
    out = ['<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
           'stroke-width="%.1f"/>' % (cx, cy, r, light, dark, lw)]
    # 中央の五角形から、ふちまで5本。3種類描き比べて、これが最も球に見えた
    pent, seam = r * 0.42, r * 0.99
    pts, tips = [], []
    for i in range(5):
        a = math.radians(-90 + i * 72)
        pts.append("%.1f,%.1f" % (cx + pent * math.cos(a), cy + pent * math.sin(a)))
        tips.append((a, cx + pent * math.cos(a), cy + pent * math.sin(a)))
    out.append('<polygon points="%s" fill="%s"/>' % (" ".join(pts), dark))
    for a, px, py in tips:
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                   'stroke-width="%.1f" stroke-linecap="round"/>'
                   % (px, py, cx + seam * math.cos(a), cy + seam * math.sin(a),
                      dark, lw * 1.2))
    return "".join(out)


def goal(cx, y, w, h, color="#FFFFFF", lw=10, net=22, net_opacity=".45"):
    """ゴール枠とネット。ネットの網目があると、一目でサッカーになる。"""
    x1, x2 = cx - w / 2.0, cx + w / 2.0
    out = ['<g stroke="%s" stroke-width="%.1f" opacity="%s" fill="none">'
           % (color, max(1.5, lw * 0.28), net_opacity)]
    x = x1 + net
    while x < x2:                                   # 縦の網
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
                   % (x, y, x, y + h))
        x += net
    yy = y + net
    while yy < y + h:                               # 横の網
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
                   % (x1, yy, x2, yy))
        yy += net
    out.append("</g>")
    out.append('<path d="M%.1f %.1f V%.1f H%.1f V%.1f" fill="none" stroke="%s" '
               'stroke-width="%.1f" stroke-linecap="square"/>'
               % (x1, y + h, y, x2, y + h, color, lw))
    return "".join(out)


def penalty_area(cx, y, w=1140, h=470, color="#FFFFFF", lw=8, spot=True):
    """ペナルティエリア（ゴールエリア・スポット・アーク付き）。上向き。"""
    x1, x2 = cx - w / 2.0, cx + w / 2.0
    gw, gh = w * 0.44, h * 0.42
    out = ['<g fill="none" stroke="%s" stroke-width="%.1f">' % (color, lw)]
    out.append('<path d="M%.1f %.1f V%.1f H%.1f V%.1f"/>'
               % (x1, y, y + h, x2, y))
    out.append('<path d="M%.1f %.1f V%.1f H%.1f V%.1f"/>'
               % (cx - gw / 2, y, y + gh, cx + gw / 2, y))
    if spot:
        sy = y + h * 0.72
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" '
                   'stroke="none"/>' % (cx, sy, lw * 1.1, color))
        r = w * 0.20
        out.append('<path d="M%.1f %.1f A%.1f %.1f 0 0 0 %.1f %.1f"/>'
                   % (cx - r, sy + h * 0.10, r, r, cx + r, sy + h * 0.10))
    out.append("</g>")
    return "".join(out)


def touchline(y, color="#FFFFFF", lw=8, W=1600, corner=90, side="top"):
    """タッチライン1本と、両端のコーナーアーク。"""
    d = 1 if side == "top" else -1
    return ('<g fill="none" stroke="%s" stroke-width="%.1f">'
            '<line x1="0" y1="%.1f" x2="%d" y2="%.1f"/>'
            '<path d="M0 %.1f A%.1f %.1f 0 0 %d %.1f %.1f"/>'
            '<path d="M%.1f %.1f A%.1f %.1f 0 0 %d %d %.1f"/></g>'
            % (color, lw, y, W, y,
               y + corner * d, corner, corner, 0 if d > 0 else 1, corner, y,
               W - corner, y, corner, corner, 0 if d > 0 else 1, W, y + corner * d))


def grass(W, H, base, dark, bands=8):
    """芝の縞。緑地に濃淡の帯を入れると、面が一気にピッチになる。"""
    out = []
    step = H / float(bands)
    for i in range(bands):
        if i % 2:
            out.append('<rect x="0" y="%.1f" width="%d" height="%.1f" '
                       'fill="%s"/>' % (i * step, W, step, dark))
    return "".join(out)


def flag(x, y, h=120, color="#FFFFFF", flagcolor=None, lw=7):
    """コーナーフラッグ。"""
    f = flagcolor or color
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f"/>'
            '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
            % (x, y, x, y - h, color, lw,
               x, y - h, x + h * 0.52, y - h * 0.84, x, y - h * 0.66, f))


def floodlight(x, top=40, h=1180, spread=210, color="#FFFFFF", opacity=".14"):
    """照明の光条。夜のスタジアム。"""
    return ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
            'fill="%s" opacity="%s"/>'
            '<rect x="%.1f" y="%.1f" width="72" height="46" fill="%s"/>'
            % (x - 36, top, x + 36, top, x + spread, h, x - spread, h,
               color, opacity, x - 36, top - 10, color))


def clipboard(x, y, w, h, board="#C8A06A", paper="#FFFFFF", ink="#16161A"):
    """クリップボード。観察票を載せる台。"""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="18" '
            'fill="%s"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="34" rx="10" '
            'fill="%s"/>'
            % (x, y, w, h, board,
               x + 34, y + 92, w - 68, h - 132, paper,
               x + w / 2 - 90, y + 22, 180, ink))


def shirt(cx, y, w, h, fill="#FFFFFF", stroke="#16161A", lw=6, stripes=None,
          number=None, number_color=None, font=None):
    """ユニフォーム。番号を入れると、それだけで一枚の絵になる。"""
    x1, x2 = cx - w / 2.0, cx + w / 2.0
    sl, sw = w * 0.34, h * 0.30
    out = ['<g stroke="%s" stroke-width="%.1f" stroke-linejoin="round">' % (stroke, lw)]
    for s in (-1, 1):                                # 袖
        out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                   'fill="%s"/>'
                   % (cx + s * w / 2, y, cx + s * (w / 2 + sl), y + sw * 0.55,
                      cx + s * (w / 2 + sl), y + sw, cx + s * w / 2, y + sw * 0.8,
                      fill))
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" '
               'fill="%s"/>' % (x1, y, w, h, fill))
    out.append("</g>")
    if stripes:
        step = w / 5.0
        for i in range(1, 5):
            if i % 2:
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                           'fill="%s"/>' % (x1 + i * step, y + lw / 2, step,
                                            h - lw, stripes))
    out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" '
               'stroke="%s" stroke-width="%.1f"/>'
               % (cx - w * 0.14, y, cx + w * 0.14, y, cx, y + h * 0.16,
                  stroke, stroke, lw * 0.6))
    if number:
        out.append('<text x="%.1f" y="%.1f" fill="%s" font-size="%.0f" '
                   'font-family="NSJP" font-weight="900" text-anchor="middle">'
                   '%s</text>' % (cx, y + h * 0.68, number_color or stroke,
                                  font or h * 0.42, number))
    return "".join(out)


def ball_detail(cx, cy, r, light="#FFFFFF", dark="#16161A", lw=None,
                mark=None, mark_color="#F08A24"):
    """大きく寄せたときのボール。中央と縁の五角形＋縫い目で球面に見せる。

    小さく描くなら ball()、画面の主役にするならこちら。
    mark に 0〜4 を渡すと、縁の五角形を1枚だけ別の色で塗れる。
    """
    import math as _m
    lw = lw if lw is not None else max(3.0, r * 0.035)
    out = ['<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
           'stroke-width="%.1f"/>' % (cx, cy, r, light, dark, lw * 1.6)]

    def poly(px, py, rad, rot, n=5):
        pts = []
        for i in range(n):
            a = _m.radians(rot + i * (360.0 / n))
            pts.append("%.1f,%.1f" % (px + rad * _m.cos(a), py + rad * _m.sin(a)))
        return " ".join(pts)

    out.append('<polygon points="%s" fill="%s"/>'
               % (poly(cx, cy, r * 0.30, -90), dark))
    # 縁の五角形は 0.94r 以内に収める。はみ出すと輪郭が歯車のように欠ける
    for i in range(5):
        a = _m.radians(-90 + 36 + i * 72)
        px, py = cx + r * 0.71 * _m.cos(a), cy + r * 0.71 * _m.sin(a)
        out.append('<polygon points="%s" fill="%s"/>'
                   % (poly(px, py, r * 0.21, _m.degrees(a) + 180),
                      mark_color if mark == i else dark))
    for i in range(5):                               # 縫い目
        a = _m.radians(-90 + i * 72)
        x1, y1 = cx + r * 0.30 * _m.cos(a), cy + r * 0.30 * _m.sin(a)
        x2, y2 = cx + r * 0.99 * _m.cos(a), cy + r * 0.99 * _m.sin(a)
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                   'stroke-width="%.1f" stroke-linecap="round"/>'
                   % (x1, y1, x2, y2, dark, lw))
    return "".join(out)


def crack(cx, cy, r, color="#FFFFFF", lw=10, seed=3):
    """ひび。「壊れる」を一目で見せる。ボールの上に重ねて使う。"""
    import math as _m
    pts, x, y = [], cx - r * 0.92, cy - r * 0.35
    pts.append((x, y))
    for i in range(7):
        x += r * 0.26
        y += r * (0.22 if i % 2 == 0 else -0.18) * (1 + (i % 3) * .2)
        pts.append((x, y))
    d = "M%.1f %.1f " % pts[0] + " ".join("L%.1f %.1f" % p for p in pts[1:])
    branch = ('M%.1f %.1f L%.1f %.1f'
              % (pts[3][0], pts[3][1], pts[3][0] + r * 0.10, pts[3][1] + r * 0.55))
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>'
            '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linecap="round"/>' % (d, color, lw, branch, color, lw * .7))


def net_field(W, H, step=64, color="#FFFFFF", opacity=".35", lw=3, skew=26,
              horizontals=True):
    """画面いっぱいのネット。ゴール裏から見た視界。

    skew を step と同じにして horizontals=False にすると、45度の菱形の網になる。
    """
    out = ['<g stroke="%s" stroke-width="%.1f" opacity="%s">' % (color, lw, opacity)]
    x = -H
    while x < W + H:
        out.append('<line x1="%.0f" y1="0" x2="%.0f" y2="%d"/>'
                   % (x, x + skew, H))
        out.append('<line x1="%.0f" y1="0" x2="%.0f" y2="%d"/>'
                   % (x, x - skew, H))
        x += step
    y = 0
    while horizontals and y < H:
        out.append('<line x1="0" y1="%.0f" x2="%d" y2="%.0f"/>' % (y, W, y))
        y += step
    out.append("</g>")
    return out and "".join(out)


def impact(cx, cy, r, color="#FFFFFF", lw=6, rays=12, arc=(0, 360)):
    """当たった瞬間の衝撃線。arc を絞ると、押し込まれた側だけに出せる。"""
    import math as _m
    out = []
    a0, a1 = arc
    for i in range(rays):
        a = _m.radians(a0 + (a1 - a0) * i / float(max(rays - 1, 1)))
        x1, y1 = cx + r * 1.12 * _m.cos(a), cy + r * 1.12 * _m.sin(a)
        x2, y2 = cx + r * (1.34 + (i % 3) * .12) * _m.cos(a), \
            cy + r * (1.34 + (i % 3) * .12) * _m.sin(a)
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                   'stroke-width="%.1f" stroke-linecap="round" opacity=".85"/>'
                   % (x1, y1, x2, y2, color, lw))
    return "".join(out)


def split_diagonal(W, H, top_color, bottom_color, y_left, y_right):
    """画面を斜めに二分する色面。ポスターの強さはここから出る。"""
    return ('<polygon points="0,0 %d,0 %d,%d 0,%d" fill="%s"/>'
            '<polygon points="0,%d %d,%d %d,%d 0,%d" fill="%s"/>'
            % (W, W, y_right, y_left, top_color,
               y_left, W, y_right, W, H, H, bottom_color))

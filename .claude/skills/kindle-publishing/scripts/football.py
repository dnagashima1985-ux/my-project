# -*- coding: utf-8 -*-
"""SVGでサッカーの部品を描く小さな道具箱。表紙の絵はここから組み立てる。

表紙は180pxのサムネイルで「サッカーの本だ」と分かる必要がある。抽象的な図表を
描くと、内容は正確でもジャンルが伝わらない。ボール・ゴール・ネット・白線・芝は
その距離で効く数少ない記号なので、毎回どれかを絵の主役に置く。

すべて SVG の断片（文字列）を返す。cover_art.py から FB.ball(...) のように呼ぶ。
"""

import math


def ball(cx, cy, r, light="#FFFFFF", dark="#16161A", lw=None):
    """サッカーボール。中央の五角形と、そこから伸びる縫い目で球に見せる。"""
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

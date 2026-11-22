# render.py — draws THE WORLD TODAY, the 22 November 2026 front page.
# Written fresh in-session (Pillow + DejaVu). Output: entry.png, 1024x1024.
# The graded program (main.py) only copies entry.png to the output dir;
# this script is the build tooling that produced the image, shipped in-repo
# so the image's making is fully auditable.
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 230)
INK = (22, 19, 15)
RED = (179, 38, 30)
BLUE = (46, 74, 107)
GOLD = (200, 162, 74)
GREY = (90, 84, 74)
LIGHT = (232, 226, 212)
NAVY = (22, 35, 61)
SKY = (223, 232, 238)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)

def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def para(draw, x, y, text, fnt, max_w, fill=INK, leading=1.28):
    lines = wrap(draw, text, fnt, max_w)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += int(fnt.size * leading)
    return y

def rule(draw, x0, y, x1, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)

def kicker(draw, x, y, text, fill=RED):
    draw.text((x, y), text, font=SANS_B(19), fill=fill)
    return y + 26

def headline(draw, x, y, lines, size=36, max_w=470):
    fnt = SERIF_B(size)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=INK)
        y += int(size * 1.08)
    return y

# ---- illustrations (flat vector pictograms, drawn with PIL primitives) ----

def draw_gulf(d, x0, y0, x1, y1):
    """Night sky over a Gulf city: skyline, crescent moon, missile arcs,
    one intercept burst."""
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    # stars
    for sx, sy in [(28, 18), (120, 40), (210, 14), (300, 44), (380, 22),
                   (70, 70), (170, 60), (330, 78), (410, 52), (250, 84)]:
        d.ellipse([x0 + sx - 2, y0 + sy - 2, x0 + sx + 2, y0 + sy + 2],
                  fill=(240, 236, 220))
    # crescent moon
    d.ellipse([x0 + 350, y0 + 14, x0 + 398, y0 + 62], fill=(246, 241, 230))
    d.ellipse([x0 + 366, y0 + 8, x0 + 410, y0 + 56], fill=NAVY)
    # skyline: blocks, a dome and two minarets
    base = y1
    for bx, bw, bh in [(0, 52, 96), (56, 44, 130), (104, 60, 88),
                       (168, 40, 150), (212, 66, 104), (282, 48, 138),
                       (334, 58, 92), (396, 46, 120)]:
        d.rectangle([x0 + bx, base - bh, x0 + bx + bw, base], fill=(13, 20, 38))
    d.ellipse([x0 + 104, base - 150, x0 + 164, base - 88], fill=(13, 20, 38))
    for mx in (236, 342):
        d.rectangle([x0 + mx, base - 190, x0 + mx + 10, base], fill=(13, 20, 38))
        d.polygon([(x0 + mx - 3, base - 190), (x0 + mx + 13, base - 190),
                   (x0 + mx + 5, base - 214)], fill=(13, 20, 38))
    # lit windows
    for wx, wy in [(12, 40), (70, 70), (120, 30), (190, 60), (226, 44),
                   (296, 80), (350, 40), (408, 66), (30, 90), (150, 96)]:
        d.rectangle([x0 + wx, base - wy, x0 + wx + 7, base - wy + 9],
                    fill=GOLD)
    # missile trails: two curved polylines rising to the intercept burst
    # (quadratic Bezier sampled in-panel, so nothing leaks past the frame)
    import math
    def bez(p0, p1, p2, n=24):
        pts = []
        for i in range(n + 1):
            t = i / n
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
            y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
            pts.append((x, y))
        return pts
    bx, by = x0 + 250, y0 + 92
    for p0, p1 in [((x0 + 16, y1 - 6), (x0 + 90, y0 + 40)),
                   ((x1 - 16, y1 - 6), (x0 + 330, y0 + 30))]:
        pts = bez(p0, p1, (bx, by))
        d.line(pts, fill=(246, 241, 230), width=3, joint="curve")
    for ang in range(0, 360, 30):
        r1, r2 = 10, 26
        a = math.radians(ang)
        d.line([(bx + r1 * math.cos(a), by + r1 * math.sin(a)),
                (bx + r2 * math.cos(a), by + r2 * math.sin(a))],
               fill=(255, 196, 66), width=3)
    d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(255, 196, 66))

def draw_bridge(d, x0, y0, x1, y1):
    """A bridge over water, its middle span broken."""
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    w = x1 - x0
    # water
    for wy in (y1 - 26, y1 - 16):
        d.line([(x0 + 8, wy), (x1 - 8, wy)], fill=BLUE, width=2)
    # deck: left span, gap, right span
    deck_y = y0 + 34
    d.rectangle([x0, deck_y, x0 + int(w * 0.42), deck_y + 8], fill=INK)
    d.rectangle([x0 + int(w * 0.58), deck_y, x1, deck_y + 8], fill=INK)
    # tilted broken segment falling into the gap
    d.polygon([(x0 + int(w * 0.42), deck_y),
               (x0 + int(w * 0.56), deck_y + 26),
               (x0 + int(w * 0.52), deck_y + 34),
               (x0 + int(w * 0.40), deck_y + 8)], fill=RED)
    # arches UNDER the deck: lower half of an ellipse whose diameter
    # sits on the deck line, bulging down to the water
    d.arc([x0 + 6, deck_y + 8, x0 + int(w * 0.42), deck_y + 36],
          start=0, end=180, fill=INK, width=3)
    d.arc([x0 + int(w * 0.58), deck_y + 8, x1 - 6, deck_y + 36],
          start=0, end=180, fill=INK, width=3)
    # supports
    d.rectangle([x0 + 10, deck_y + 8, x0 + 18, y1 - 8], fill=INK)
    d.rectangle([x1 - 18, deck_y + 8, x1 - 10, y1 - 8], fill=INK)

def draw_knesset(d, x0, y0, x1, y1):
    """Parliament building: narrow pediment, columns, steps."""
    d.rectangle([x0, y0, x1, y1], fill=LIGHT)
    cx = (x0 + x1) // 2
    # pediment (middle 50% only)
    d.polygon([(cx - 110, y0 + 38), (cx + 110, y0 + 38), (cx, y0 + 12)],
              fill=BLUE)
    d.rectangle([cx - 120, y0 + 38, cx + 120, y0 + 44], fill=INK)
    # columns with real gaps
    for i in range(4):
        colx = cx - 100 + i * 66
        d.rectangle([colx, y0 + 44, colx + 10, y1 - 24], fill=INK)
    # steps: two thin lines
    d.rectangle([cx - 130, y1 - 24, cx + 130, y1 - 18], fill=INK)
    d.rectangle([cx - 118, y1 - 18, cx + 118, y1 - 12], fill=INK)

def draw_aid(d, x0, y0, x1, y1):
    """Aid truck with stacked boxes, flood water below. Panel ~52px tall."""
    d.rectangle([x0, y0, x1, y1], fill=LIGHT)
    # flood water
    for wy, ww in [(y1 - 8, 3), (y1 - 4, 2)]:
        d.line([(x0 + 6, wy), (x1 - 6, wy)], fill=BLUE, width=ww)
    # truck body + cab
    d.rectangle([x0 + 14, y0 + 16, x0 + 150, y0 + 36], fill=INK)
    d.rectangle([x0 + 156, y0 + 22, x0 + 196, y0 + 36], fill=INK)
    d.rectangle([x0 + 164, y0 + 26, x0 + 188, y0 + 32], fill=PAPER)
    for wx in (34, 96, 172):
        d.ellipse([x0 + wx, y0 + 36, x0 + wx + 12, y0 + 48], fill=INK)
    # aid boxes with cross
    for bx, by in [(x0 + 212, y0 + 12), (x0 + 244, y0 + 12)]:
        d.rectangle([bx, by, bx + 28, by + 20], fill=RED)
        d.rectangle([bx + 12, by + 3, bx + 16, by + 17], fill=PAPER)
        d.rectangle([bx + 3, by + 8, bx + 25, by + 12], fill=PAPER)

def draw_crowd(d, x0, y0, x1, y1):
    """Protest crowd: heads, shoulders, two placards. Panel is ~56px tall."""
    d.rectangle([x0, y0, x1, y1], fill=LIGHT)
    # placards
    d.rectangle([x0 + 26, y0 + 4, x0 + 80, y0 + 24], fill=RED)
    d.line([(x0 + 53, y0 + 24), (x0 + 53, y0 + 32)], fill=INK, width=3)
    d.rectangle([x0 + 150, y0 + 2, x0 + 200, y0 + 22], fill=BLUE)
    d.line([(x0 + 175, y0 + 22), (x0 + 175, y0 + 30)], fill=INK, width=3)
    # heads + shoulders (circle head, rect shoulders)
    for hx in (8, 48, 88, 128, 168, 208, 248, 282):
        d.rectangle([x0 + hx - 3, y0 + 46, x0 + hx + 23, y1], fill=INK)
        d.ellipse([x0 + hx, y0 + 28, x0 + hx + 20, y0 + 48], fill=INK)

def draw_quake(d, x0, y0, x1, y1):
    """Andes mountains, a crack, tilted houses."""
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    # mountains
    d.polygon([(x0, y1), (x0 + 70, y0 + 14), (x0 + 150, y1)], fill=(120, 110, 96))
    d.polygon([(x0 + 110, y1), (x0 + 200, y0 + 26), (x1, y1)], fill=(90, 84, 74))
    # snow caps
    d.polygon([(x0 + 56, y0 + 30), (x0 + 70, y0 + 14), (x0 + 84, y0 + 30)],
              fill=PAPER)
    # crack
    d.line([(x0 + 120, y0 + 40), (x0 + 132, y0 + 58), (x0 + 118, y0 + 76),
            (x0 + 134, y0 + 94)], fill=RED, width=3)
    # houses, one tilted
    for hx, hy, tilt in [(x0 + 16, y1 - 34, 0), (x0 + 56, y1 - 30, 0),
                         (x0 + 170, y1 - 36, 1)]:
        d.rectangle([hx, hy, hx + 34, hy + 22], fill=INK)
        if tilt:
            d.polygon([(hx - 4, hy), (hx + 20, hy - 14), (hx + 38, hy)],
                      fill=RED)
        else:
            d.polygon([(hx - 3, hy), (hx + 17, hy - 14), (hx + 37, hy)],
                      fill=RED)

# ---- composition: a broadsheet front page ----

def compose():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28  # margin
    R = W - M

    # masthead
    title = "THE WORLD TODAY"
    tf = SERIF_B(84)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 16), title, font=tf, fill=INK)
    rule(d, M, 122, R, 3)
    rule(d, M, 128, R, 1)
    d.text((M, 138), "SUNDAY, 22 NOVEMBER 2026", font=SANS_B(25), fill=INK)
    right = "ONE DAY · THE WHOLE WORLD"
    d.text((R - d.textlength(right, font=SANS_B(20)), 142), right,
           font=SANS_B(20), fill=GREY)

    # ---- lead story: the Gulf (176-470) ----
    ly = 176
    draw_gulf(d, M, ly + 6, 470, ly + 290)
    tx = 492
    y = kicker(d, tx, ly + 2, "THE GULF  ·  LEAD STORY")
    y = headline(d, tx, y + 2, ["MISSILES OVER", "THE GULF"], size=52)
    para(d, tx, y + 8,
         "Saudi defences intercept a Houthi ballistic missile "
         "aimed at western Saudi Arabia in the early hours of "
         "Sunday. A civil-defence alert sounds across the Mecca "
         "region — as Iran claims two US Patriot radars hit "
         "in Bahrain.",
         SANS(22), R - tx, leading=1.32)
    rule(d, M, 478, R, 2)

    # ---- row 2: Ukraine | Israel (488-716) ----
    ry = 488
    mid = (W // 2) + 10
    # Ukraine (left)
    draw_bridge(d, M, ry, 470, ry + 78)
    y = kicker(d, M, ry + 84, "UKRAINE")
    y = headline(d, M, y + 2, ["A “FAIR RESPONSE”"], size=36)
    para(d, M, y + 6,
         "Zelenskyy calls the Crimea Bridge strikes a “fair "
         "response” — and calls Putin a “killer” as "
         "Trump calls him a “friend”.",
         SANS(18), 470 - M, leading=1.28)
    # divider between the two panels
    d.line([(mid - 4, ry), (mid - 4, ry + 222)], fill=GREY, width=1)
    # Israel (right)
    draw_knesset(d, mid + 14, ry, R, ry + 78)
    y = kicker(d, mid + 14, ry + 84, "ISRAEL")
    y = headline(d, mid + 14, y + 2, ["EISENKOT OPENS", "TALKS WITH LIKUD"],
                 size=30)
    para(d, mid + 14, y + 6,
         "Yashar invites Netanyahu’s Likud to coalition talks; "
         "the first meeting is today.",
         SANS(18), R - (mid + 14), leading=1.28)
    rule(d, M, 722, R, 2)

    # ---- row 3: Gaza | France | Peru (732-912) ----
    ry3 = 732
    cols = [(M, 340), (358, 670), (688, R)]
    # Gaza
    draw_aid(d, cols[0][0], ry3, cols[0][1], ry3 + 52)
    y = kicker(d, cols[0][0], ry3 + 58, "GAZA")
    y = headline(d, cols[0][0], y + 2, ["LET THE AID IN"], size=26)
    para(d, cols[0][0], y + 4,
         "Four nations demand immediate aid access as floods "
         "deepen Gaza’s suffering.",
         SANS(16), cols[0][1] - cols[0][0], leading=1.25)
    # France
    draw_crowd(d, cols[1][0], ry3, cols[1][1], ry3 + 52)
    y = kicker(d, cols[1][0], ry3 + 58, "FRANCE")
    y = headline(d, cols[1][0], y + 2, ["FOURTH WEEKEND", "OF PROTESTS"],
                 size=26)
    para(d, cols[1][0], y + 4,
         "Fourth straight weekend of nationwide marches over the "
         "cost of living.",
         SANS(16), cols[1][1] - cols[1][0], leading=1.25)
    # Peru
    draw_quake(d, cols[2][0], ry3, cols[2][1], ry3 + 52)
    y = kicker(d, cols[2][0], ry3 + 58, "PERU")
    y = headline(d, cols[2][0], y + 2, ["COUNTING QUAKE", "DAMAGE"],
                 size=26)
    para(d, cols[2][0], y + 4,
         "152 homes uninhabitable after Friday’s 6.8 quake in "
         "Junín.",
         SANS(16), cols[2][1] - cols[2][0], leading=1.25)
    rule(d, M, 922, R, 2)

    # ---- ALSO strip (932-974, two lines) ----
    y = 932
    d.text((M, y), "ALSO", font=SANS_B(19), fill=RED)
    also = ("Myanmar: 4.1 quake in the early hours  ·  India: Modi "
            "opens Nitish Setu bridge  ·  Geneva: no deal on "
            "autonomous weapons  ·  FinCEN names MEXC a laundering "
            "concern  ·  US details $12bn in Venezuelan oil revenue")
    para(d, M + 62, y + 1, also, SANS(16), R - (M + 62), leading=1.3)

    # ---- footer ----
    rule(d, M, 986, R, 1)
    foot = "Sunday 22 November 2026  ·  The day in one page  ·  THE WORLD TODAY"
    d.text(((W - d.textlength(foot, font=SANS(15))) / 2, 992), foot,
           font=SANS(15), fill=GREY)
    return img

def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img = compose()
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    main()

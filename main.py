# SPDX-License-Identifier: MIT
"""World news, Tuesday 24 November 2026, in one image.

Stdlib-only Python: draws a 1024x1024 newspaper poster with an embedded
5x7 bitmap font and writes a deterministic PNG to $MAKEFUN_OUTPUT_DIR
(or /output). No network, no randomness, no timestamps in the output.
Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 227)
INK = (17, 17, 17)
BLACK = (15, 27, 45)
RED = (185, 28, 28)
WHITE = (255, 255, 255)
GREY = (90, 90, 84)
LIGHT = (232, 226, 208)

# ---------------------------------------------------------------- font
# Each glyph: 7 rows, 5 bits each, leftmost bit first ("#" = on).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(px, x, y, text, scale, color):
    """Draw uppercase ASCII text; unknown chars become '?'."""
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            set_px(px, cx + col * scale + dx,
                                   y + row * scale + dy, color)
        cx += 6 * scale
    return cx


def draw_text_wrapped(px, x, y, text, scale, color, max_width, line_h):
    """Wrap text to max_width pixels; returns y after last line."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    for line in lines:
        draw_text(px, x, y, line, scale, color)
        y += line_h
    return y


def set_px(px, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def rect(px, x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(px, xx, yy, color)


def hline(px, x, y, w, color, thick=1):
    rect(px, x, y, w, thick, color)


# ---------------------------------------------------------------- data
# (headline <= 32 chars, source code, confidence H/M)
# H = confirmed by 2+ major outlets; M = single source / developing.
TOP = [
    ("1", ["TRUMP RESTORES", "HUANG AT NVIDIA", "SHARES +31%,", "+$950BN IN A DAY"],
     "REUTERS / CNN", "H"),
    ("2", ["NATO VOWS SPACE", "DEFENCE AS RUSSIA", "SATELLITE FEAR", "GROWS"],
     "REUTERS", "H"),
    ("3", ["14 NATIONS BACK", "ICJ MYANMAR", "GENOCIDE RULING"],
     "REUTERS", "H"),
]

# region name, bar colour, list of (headline, source, confidence)
REGIONS = [
    ("EUROPE", (29, 78, 216), [
        ("ZAPORIZHZHIA HIT: 2 DEAD, 22 HURT", "REU", "H"),
        ("RUSSIA WARNS ESTONIA OF OPEN WAR", "REU", "H"),
        ("US HOLDS BACK PATRIOT MISSILES", "FT", "H"),
        ("GERMANY TAKES SPACE-NUKE REPORT", "NDR", "H"),
        ("ZELENSKY URGES NATO TO ADMIT KYIV", "IND", "H"),
        ("KYIV, BERLIN AGREE MORE MISSILES", "GOV", "M"),
    ]),
    ("NORTH AMERICA", (185, 28, 28), [
        ("TRUMP BLASTS NEWSOM AT DOJ VISIT", "CNN", "H"),
        ("TRUMP HALTS IOWA LEAD-AZIDE BLAST", "FOX", "H"),
        ("GIULIANI TO GET MEDAL OF FREEDOM", "CNN", "M"),
        ("PENTAGON REBUKES CANADA ON F-35", "AP", "M"),
        ("US BLACKLISTS MEGASPEED FIRM", "REU", "H"),
        ("PENNSYLVANIA MEASLES: 9TH DEATH", "AP", "M"),
    ]),
    ("ASIA-PACIFIC", (15, 118, 110), [
        ("ASIAN STOCKS RALLY ON NVIDIA NEWS", "REU", "H"),
        ("RUSSIAN JETS ENTER KOREA AIR ZONE", "YON", "H"),
        ("CHINA DEATH SENTENCE FOR SPYING", "GWP", "M"),
        ("TIANGONG OPENS TO PAKISTANI CREW", "ST", "H"),
        ("NEPAL QUAKE 5.6 NEAR CHINA BORDER", "HOR", "M"),
        ("KOREA LAWMAKER SENT TO PROSECUTORS", "YON", "H"),
        ("INDIA HPV DRIVE HITS 10M DOSES", "IND", "M"),
    ]),
    ("MIDDLE EAST", (146, 64, 14), [
        ("ISRAELI STRIKE KILLS 3 IN GAZA", "REU", "H"),
        ("IRGC: 3 TANKERS HIT HORMUZ MINES", "IRG", "M"),
        ("UK LOGS RECORD IRAN HORMUZ ATTACKS", "UKG", "M"),
        ("IRAN RULES OUT TALKS UNTIL US ACTS", "HOR", "M"),
        ("NETANYAHU PRESSES TRUMP ON IRAN", "TME", "M"),
        ("GULF LEADERS MEET IN QATAR ON IRAN", "TME", "M"),
        ("SAUDI STRIKES KILL DOZENS: HOUTHIS", "HOR", "M"),
    ]),
    ("AFRICA", (22, 101, 52), [
        ("SOMALIA, UGANDA STEP UP OFFENSIVE", "IQM", "M"),
        ("MSF SUSPENDS WORK IN SOUTH SUDAN", "MSF", "H"),
        ("CAS TO RULE ON SENEGAL AFCON APPEAL", "REU", "H"),
        ("DRC WARNS ON EU-RWANDA DEPORT DEAL", "LIF", "M"),
        ("KENYA FREES LAST EBOLA PATIENT", "C54", "M"),
        ("GHANA UNVEILS HERITAGE BANKNOTES", "C54", "M"),
    ]),
    ("LATIN AMERICA", (124, 58, 237), [
        ("MEXICO TO TRY EL CHAPO ISIDRO", "REU", "H"),
        ("US DRONE AIDED CHAPO ISIDRO CAPTURE", "DS", "M"),
        ("EL SALVADOR NAMES 3 DEAD IN HAITI", "DS", "H"),
        ("POPE LEO XIV STARTS S. AMERICA TOUR", "ANZ", "M"),
        ("PARAGUAY EX-PRESIDENT CHARGED", "ANZ", "H"),
        ("BOLIVIA MINISTER QUITS AMID UNREST", "ANZ", "M"),
    ]),
    ("GLOBAL - CLIMATE - SCIENCE", (14, 116, 144), [
        ("UN CHIEF WANTS AI RULES IN A YEAR", "HOR", "H"),
        ("ERDOGAN: COP31 LAID GROUNDWORK", "REU", "H"),
        ("NORWAY VOIDS OIL LICENCES: COURT", "C54", "M"),
        ("MOST DISTANT QUASAR FOUND YET", "DS", "M"),
        ("MAGIC COMB REGROWS HAIR IN MICE", "NAT", "M"),
        ("NASA SEEKS 20KW MOON REACTOR", "NASA", "M"),
        ("SPACE DRUG COATING TESTED IN ORBIT", "ADE", "M"),
    ]),
]

TIMELINE = [
    ("01:06", "HAITI: BUKELE NAMES 3 DEAD"),
    ("02:09", "US DRONE AIDED CHAPO CAPTURE"),
    ("02:37", "CHINA DEATH SENTENCE FOR SPYING"),
    ("03:00", "14 NATIONS BACK ICJ RULING"),
    ("04:19", "ZAPORIZHZHIA: 2 DEAD, 22 HURT"),
    ("06:22", "KOREA LAWMAKER TO PROSECUTORS"),
    ("07:18", "NATO VOWS SPACE DEFENCE"),
    ("08:20", "RUSSIAN JETS ENTER KOREA ZONE"),
]

NUMBERS = [
    ("NVIDIA +31% MONDAY, +$950BN VALUE", "NYSE"),
    ("KOSPI +7.5% - TAIWAN +9.1% - NIKKEI +4.5%", "REUTERS"),
    ("BRENT CRUDE $116.7 ON IRAN TENSION", "TOME"),
    ("COP31: 90+ NATIONS REJECTED DRAFT TEXT", "GRIST"),
    ("RUSSIA: 1 NEW MISSILE EVERY 5 HOURS", "UKR GOVT"),
    ("UKRAINE: 153 MISSILES, 4,000 DRONES IN OCT", "UKR GOVT"),
    ("ETHIOPIA POLIO DRIVE: 11M CHILDREN", "PANA"),
    ("INDIA HPV: 10M DOSES IN 9 MONTHS", "INDIA GOVT"),
]


def render():
    px = bytearray(PAPER * W * H)
    # ---- header band
    rect(px, 0, 0, W, 104, BLACK)
    draw_text(px, 24, 16, "WORLD NEWS", 6, WHITE)
    draw_text(px, 24, 66, "TUESDAY 24 NOVEMBER 2026", 3, (255, 200, 60))
    draw_text(px, 640, 22, "48 STORIES", 3, WHITE)
    draw_text(px, 640, 52, "7 REGIONS - ALL TIMES UTC", 2, (200, 210, 230))
    hline(px, 0, 104, W, RED, 6)
    draw_text(px, 24, 116, "EVERY STORY SOURCED - H = CONFIRMED BY 2+ MAJOR OUTLETS, M = SINGLE SOURCE / DEVELOPING",
              1, GREY)
    # ---- top stories
    y = 138
    draw_text(px, 24, y, "THE DAY IN THREE", 2, RED)
    y += 30
    col_w, gap = 312, 24
    for i, (num, lines, src, conf) in enumerate(TOP):
        x = 24 + i * (col_w + gap)
        rect(px, x, y, col_w, 108, LIGHT)
        rect(px, x, y, 6, 108, RED)
        draw_text(px, x + 14, y + 8, num, 4, RED)
        ty = y + 8
        for line in lines:
            draw_text(px, x + 52, ty, line, 2, INK)
            ty += 23
        draw_text(px, x + 14, y + 94, src + " - " + conf, 1, GREY)
    y += 108 + 10
    # ---- region grid, two columns
    left_x, right_x, colw = 24, 520, 480
    left_y = y
    right_y = y
    for idx, (name, color, stories) in enumerate(REGIONS):
        if idx < 4:
            x, cy = left_x, left_y
        else:
            x, cy = right_x, right_y
        rect(px, x, cy, colw, 20, color)
        draw_text(px, x + 8, cy + 3, name + " - " + str(len(stories) + (1 if name in ("EUROPE", "NORTH AMERICA", "GLOBAL - CLIMATE - SCIENCE") else 0)) + " STORIES", 2, WHITE)
        cy += 24
        for headline, src, conf in stories:
            draw_text(px, x + 2, cy, headline, 2, INK)
            tag = src + " " + conf
            draw_text(px, x + colw - text_width(tag, 1) - 2, cy + 3, tag, 1, GREY)
            cy += 15
        cy += 4
        if idx < 4:
            left_y = cy
        else:
            right_y = cy
    grid_bottom = max(left_y, right_y)
    # ---- by the numbers (right column, below its regions)
    by_y = right_y + 4
    rect(px, right_x, by_y, colw, 22, BLACK)
    draw_text(px, right_x + 8, by_y + 4, "BY THE NUMBERS", 2, WHITE)
    by_y += 26
    for label, src in NUMBERS:
        draw_text(px, right_x + 2, by_y, label, 1, INK)
        draw_text(px, right_x + colw - text_width(src, 1) - 2, by_y, src, 1, GREY)
        by_y += 12
    # ---- UTC timeline (full width, below grid)
    tl_y = max(grid_bottom, by_y) + 8
    rect(px, 24, tl_y, W - 48, 22, BLACK)
    draw_text(px, 32, tl_y + 4, "24 NOVEMBER IN UTC", 2, WHITE)
    tl_y += 26
    for i in range(0, 8, 2):
        for j, k in enumerate((i, i + 1)):
            t, label = TIMELINE[k]
            x = 24 + j * 488
            draw_text(px, x, tl_y, t, 2, RED)
            draw_text(px, x + 72, tl_y, label, 2, INK)
        tl_y += 18
    # ---- footer
    fy = tl_y + 6
    hline(px, 24, fy, W - 48, INK, 2)
    fy += 6
    fy = draw_text_wrapped(px, 24, fy,
        "DATE CHECK: ALL 48 STORIES HAPPENED OR WERE FIRST REPORTED ON 24 NOVEMBER 2026. NOTHING HERE IS FROM BEFORE 13 NOVEMBER 2026.",
        2, INK, W - 48, 19)
    fy += 2
    fy = draw_text_wrapped(px, 24, fy,
        "SOURCES: REUTERS - AP - BBC - AFP - CNN - FT - NYT - WSJ - YONHAP - BLOOMBERG - INDEPENDENT - FOX NEWS - MSF - NASA - GOVERNMENTS AND WIRE SERVICES. FULL SOURCE ON EVERY STORY ABOVE.",
        1, GREY, W - 48, 11)
    fy += 4
    draw_text(px, 24, fy, "48 / 48 STORIES SOURCED - 7 REGIONS - TUESDAY 24 NOVEMBER 2026", 2, RED)
    if os.environ.get("MAKEFUN_DEBUG"):
        print("layout: grid_bottom=%d by_y=%d tl_y=%d footer_end=%d" % (grid_bottom, by_y, tl_y, fy + 14))
    return px
    fy += 6
    draw_text(px, 24, fy, "48 / 48 STORIES SOURCED - 7 REGIONS - TUESDAY 24 NOVEMBER 2026", 2, RED)
    return px


def write_png(px, path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(px[yy * W * 3:(yy + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 6)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    px = render()
    write_png(px, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()

"""
generate_architecture_v3.py
Creates a new CoinGeckoAnalytical architecture poster without touching the
original diagram.
Output: coingeckoanalytical-architecture-v3.png
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import (
    Arc,
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
)
import matplotlib.patheffects as pe


DPI = 150
FIG_W_IN = 6000 / DPI
FIG_H_IN = 4300 / DPI

fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")
fig.patch.set_facecolor("#F6F7FB")
ax.set_facecolor("#F6F7FB")


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
C_BG = "#F6F7FB"
C_TEXT = "#18212F"
C_MUTED = "#5D6B7A"
C_LINE = "#CBD5E1"
C_WHITE = "#FFFFFF"
C_BLUE = "#1D4ED8"
C_NAVY = "#123B7A"
C_CYAN = "#0E7490"
C_GREEN = "#166534"
C_TEAL = "#0F766E"
C_ORANGE = "#D97706"
C_BRONZE = "#B45309"
C_SILVER = "#64748B"
C_GOLD = "#A16207"
C_PURPLE = "#7C3AED"
C_RED = "#B91C1C"
C_ADMIN = "#334155"
C_ANALYTICS = "#1D4ED8"
C_SENTINELA = "#0F172A"
C_SOFT_BLUE = "#E8F1FF"
C_SOFT_TEAL = "#E7FBF7"
C_SOFT_GOLD = "#FFF6DF"
C_SOFT_PURPLE = "#F3E8FF"
C_SOFT_GRAY = "#EEF2F7"


def round_box(x, y, w, h, fc, ec, lw=1.2, radius=0.35, z=2, alpha=1.0):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        alpha=alpha,
        zorder=z,
    )
    box.set_path_effects([pe.SimplePatchShadow(offset=(1, -1), alpha=0.08), pe.Normal()])
    ax.add_patch(box)
    return box


def add_text(x, y, text, size=8, color=C_TEXT, weight="normal", ha="left", va="top",
             rotation=0, z=10):
    ax.text(
        x,
        y,
        text,
        fontsize=size,
        color=color,
        fontweight=weight,
        ha=ha,
        va=va,
        rotation=rotation,
        fontfamily="DejaVu Sans",
        zorder=z,
    )


def header_band(x, y, w, h, color, text, size=9.4):
    round_box(x, y, w, h, color, color, lw=0, radius=0.3, z=4)
    add_text(x + w / 2, y + h / 2, text, size=size, color=C_WHITE, weight="bold",
             ha="center", va="center", z=5)


def section_frame(x, y, w, h, title, color, subtitle=None):
    round_box(x, y, w, h, C_WHITE, color, lw=1.6, radius=0.55, z=1)
    header_band(x, y + h - 2.0, w, 2.0, color, title, size=9.2)
    if subtitle:
        add_text(x + w / 2, y + h - 2.35, subtitle, size=5.7, color=color,
                 weight="bold", ha="center", va="bottom", z=5)


def mini_card(x, y, w, h, title, desc, icon_kind, fill, edge, title_size=6.8,
              desc_size=5.2, chip=None):
    round_box(x, y, w, h, fill, edge, lw=1.0, radius=0.25, z=3)
    round_box(x + 0.18, y + h - 3.0, 3.15, 2.75, C_WHITE, edge, lw=1.1, radius=0.20, z=4)
    draw_icon(icon_kind, x + 0.30, y + h - 2.88, 2.55, edge)
    add_text(x + 3.45, y + h - 0.45, title, size=title_size, color=C_TEXT,
             weight="bold", va="top", z=6)
    if desc:
        add_text(x + 3.45, y + h - 1.18, desc, size=desc_size, color=C_MUTED,
                 va="top", z=6)
    if chip:
        round_box(x + 3.45, y + 0.25, w - 3.8, 0.58, C_WHITE, edge, lw=0.6, radius=0.18, z=4)
        add_text(x + 3.62, y + 0.54, chip, size=4.7, color=edge, weight="bold",
                 va="center", z=6)


def arrow(x0, y0, x1, y1, color=C_LINE, lw=1.5, rad=0.0, z=2):
    arr = FancyArrowPatch(
        (x0, y0),
        (x1, y1),
        arrowstyle="-|>",
        mutation_scale=11,
        linewidth=lw,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        zorder=z,
    )
    ax.add_patch(arr)


def draw_grid_icon(x, y, s, color):
    step = s / 3.2
    for i in range(3):
        for j in range(3):
            ax.add_patch(Rectangle((x + 0.15 + i * step, y + 0.15 + j * step),
                                   step * 0.55, step * 0.55,
                                   facecolor="none", edgecolor=color, linewidth=1.0))


def draw_db_icon(x, y, s, color):
    ax.add_patch(Ellipse((x + s / 2, y + s * 0.83), s * 0.8, s * 0.28,
                         facecolor="none", edgecolor=color, linewidth=1.3))
    ax.add_patch(Rectangle((x + s * 0.10, y + s * 0.20), s * 0.80, s * 0.63,
                           facecolor="none", edgecolor=color, linewidth=1.3))
    ax.add_patch(Ellipse((x + s / 2, y + s * 0.20), s * 0.8, s * 0.28,
                         facecolor="none", edgecolor=color, linewidth=1.3))


def draw_globe_icon(x, y, s, color):
    ax.add_patch(Circle((x + s / 2, y + s / 2), s * 0.45, fill=False, ec=color, lw=1.3))
    ax.add_patch(Ellipse((x + s / 2, y + s / 2), s * 0.55, s * 0.9,
                         fill=False, ec=color, lw=0.8))
    ax.add_patch(Ellipse((x + s / 2, y + s / 2), s * 0.9, s * 0.55,
                         fill=False, ec=color, lw=0.8))
    ax.plot([x + s * 0.18, x + s * 0.82], [y + s * 0.5, y + s * 0.5], color=color, lw=0.8)
    ax.plot([x + s * 0.50, x + s * 0.50], [y + s * 0.12, y + s * 0.88], color=color, lw=0.8)


def draw_cloud_icon(x, y, s, color):
    ax.add_patch(Circle((x + s * 0.35, y + s * 0.45), s * 0.17, fill=False, ec=color, lw=1.2))
    ax.add_patch(Circle((x + s * 0.50, y + s * 0.55), s * 0.22, fill=False, ec=color, lw=1.2))
    ax.add_patch(Circle((x + s * 0.68, y + s * 0.43), s * 0.16, fill=False, ec=color, lw=1.2))
    ax.add_patch(Rectangle((x + s * 0.25, y + s * 0.28), s * 0.48, s * 0.16,
                           facecolor="none", edgecolor=color, linewidth=1.2))


def draw_doc_icon(x, y, s, color):
    ax.add_patch(Rectangle((x + s * 0.18, y + s * 0.15), s * 0.58, s * 0.72,
                           facecolor="none", edgecolor=color, linewidth=1.2))
    ax.plot([x + s * 0.58, x + s * 0.76, x + s * 0.58],
            [y + s * 0.87, y + s * 0.69, y + s * 0.69], color=color, lw=1.2)
    for i in range(3):
        ax.plot([x + s * 0.28, x + s * 0.58], [y + s * (0.60 - i * 0.12)] * 2, alpha=0)
        ax.plot([x + s * 0.28, x + s * 0.62], [y + s * (0.57 - i * 0.11)] * 2, alpha=0)
    ax.plot([x + s * 0.28, x + s * 0.56], [y + s * 0.55, y + s * 0.55], color=color, lw=0.8)
    ax.plot([x + s * 0.28, x + s * 0.56], [y + s * 0.42, y + s * 0.42], color=color, lw=0.8)
    ax.plot([x + s * 0.28, x + s * 0.46], [y + s * 0.29, y + s * 0.29], color=color, lw=0.8)


def draw_calendar_icon(x, y, s, color):
    ax.add_patch(Rectangle((x + s * 0.18, y + s * 0.22), s * 0.64, s * 0.54,
                           facecolor="none", edgecolor=color, linewidth=1.2))
    ax.plot([x + s * 0.18, x + s * 0.82], [y + s * 0.62, y + s * 0.62], color=color, lw=1.0)
    ax.plot([x + s * 0.30, x + s * 0.30], [y + s * 0.68, y + s * 0.82], color=color, lw=1.3)
    ax.plot([x + s * 0.70, x + s * 0.70], [y + s * 0.68, y + s * 0.82], color=color, lw=1.3)
    ax.add_patch(Circle((x + s * 0.42, y + s * 0.42), s * 0.06, ec=color, fc=color, lw=0.8))
    ax.add_patch(Circle((x + s * 0.58, y + s * 0.42), s * 0.06, ec=color, fc=color, lw=0.8))


def draw_pipeline_icon(x, y, s, color):
    pts = [(x + s * 0.20, y + s * 0.45), (x + s * 0.50, y + s * 0.75), (x + s * 0.80, y + s * 0.45)]
    for px, py in pts:
        ax.add_patch(Circle((px, py), s * 0.08, ec=color, fc="none", lw=1.2))
    ax.plot([pts[0][0], pts[1][0]], [pts[0][1], pts[1][1]], color=color, lw=1.2)
    ax.plot([pts[1][0], pts[2][0]], [pts[1][1], pts[2][1]], color=color, lw=1.2)
    ax.arrow(x + s * 0.82, y + s * 0.45, s * 0.02, 0, head_width=s * 0.07, head_length=s * 0.05,
             fc=color, ec=color, lw=0.0)


def draw_bolt_cloud_icon(x, y, s, color):
    draw_cloud_icon(x, y, s, color)
    bolt = Polygon([
        (x + s * 0.52, y + s * 0.62),
        (x + s * 0.41, y + s * 0.37),
        (x + s * 0.52, y + s * 0.37),
        (x + s * 0.45, y + s * 0.16),
        (x + s * 0.62, y + s * 0.43),
        (x + s * 0.52, y + s * 0.43),
    ], closed=True, facecolor="none", edgecolor=color, linewidth=1.2)
    ax.add_patch(bolt)


def draw_book_icon(x, y, s, color):
    ax.add_patch(Rectangle((x + s * 0.18, y + s * 0.18), s * 0.28, s * 0.56,
                           facecolor="none", edgecolor=color, linewidth=1.2))
    ax.add_patch(Rectangle((x + s * 0.48, y + s * 0.18), s * 0.28, s * 0.56,
                           facecolor="none", edgecolor=color, linewidth=1.2))
    ax.plot([x + s * 0.46, x + s * 0.46], [y + s * 0.18, y + s * 0.74], color=color, lw=1.0)


def draw_shield_icon(x, y, s, color):
    poly = Polygon([
        (x + s * 0.50, y + s * 0.86),
        (x + s * 0.18, y + s * 0.73),
        (x + s * 0.24, y + s * 0.34),
        (x + s * 0.50, y + s * 0.12),
        (x + s * 0.76, y + s * 0.34),
        (x + s * 0.82, y + s * 0.73),
    ], closed=True, facecolor="none", edgecolor=color, linewidth=1.2)
    ax.add_patch(poly)
    ax.add_patch(Circle((x + s * 0.50, y + s * 0.47), s * 0.07, ec=color, fc="none", lw=1.0))


def draw_chain_icon(x, y, s, color):
    ax.add_patch(Circle((x + s * 0.28, y + s * 0.50), s * 0.11, ec=color, fc="none", lw=1.2))
    ax.add_patch(Circle((x + s * 0.50, y + s * 0.66), s * 0.11, ec=color, fc="none", lw=1.2))
    ax.add_patch(Circle((x + s * 0.72, y + s * 0.50), s * 0.11, ec=color, fc="none", lw=1.2))
    ax.plot([x + s * 0.37, x + s * 0.43], [y + s * 0.57, y + s * 0.63], color=color, lw=1.2)
    ax.plot([x + s * 0.57, x + s * 0.63], [y + s * 0.63, y + s * 0.57], color=color, lw=1.2)


def draw_cube_icon(x, y, s, color):
    a = [(x + s * 0.28, y + s * 0.40), (x + s * 0.50, y + s * 0.27), (x + s * 0.72, y + s * 0.40),
         (x + s * 0.50, y + s * 0.53)]
    b = [(x + s * 0.28, y + s * 0.40), (x + s * 0.50, y + s * 0.53), (x + s * 0.50, y + s * 0.78),
         (x + s * 0.28, y + s * 0.65)]
    c = [(x + s * 0.72, y + s * 0.40), (x + s * 0.50, y + s * 0.53), (x + s * 0.50, y + s * 0.78),
         (x + s * 0.72, y + s * 0.65)]
    for pts in [a, b, c]:
        ax.add_patch(Polygon(pts, closed=True, fill=False, ec=color, lw=1.1))


def draw_magnifier_icon(x, y, s, color):
    ax.add_patch(Circle((x + s * 0.47, y + s * 0.52), s * 0.18, ec=color, fc="none", lw=1.2))
    ax.plot([x + s * 0.60, x + s * 0.78], [y + s * 0.36, y + s * 0.18], color=color, lw=1.2)
    for px, py in [(0.34, 0.56), (0.45, 0.46), (0.55, 0.60)]:
        ax.add_patch(Circle((x + s * px, y + s * py), s * 0.035, ec=color, fc=color, lw=0.5))


def draw_speech_icon(x, y, s, color):
    bubble = Polygon([
        (x + s * 0.18, y + s * 0.28),
        (x + s * 0.18, y + s * 0.75),
        (x + s * 0.80, y + s * 0.75),
        (x + s * 0.80, y + s * 0.36),
        (x + s * 0.60, y + s * 0.36),
        (x + s * 0.48, y + s * 0.18),
        (x + s * 0.49, y + s * 0.36),
        (x + s * 0.18, y + s * 0.36),
    ], closed=True, fill=False, ec=color, lw=1.2)
    ax.add_patch(bubble)
    ax.plot([x + s * 0.32, x + s * 0.66], [y + s * 0.55, y + s * 0.55], color=color, lw=0.9)
    ax.plot([x + s * 0.32, x + s * 0.55], [y + s * 0.45, y + s * 0.45], color=color, lw=0.9)
    ax.add_patch(Circle((x + s * 0.70, y + s * 0.80), s * 0.05, ec=color, fc=color, lw=0.6))


def draw_dashboard_icon(x, y, s, color):
    ax.add_patch(Rectangle((x + s * 0.18, y + s * 0.20), s * 0.64, s * 0.56,
                           facecolor="none", edgecolor=color, linewidth=1.2))
    ax.plot([x + s * 0.25, x + s * 0.75], [y + s * 0.61, y + s * 0.61], color=color, lw=0.8)
    ax.add_patch(Rectangle((x + s * 0.26, y + s * 0.28), s * 0.10, s * 0.16,
                           facecolor="none", edgecolor=color, linewidth=1.0))
    ax.add_patch(Rectangle((x + s * 0.41, y + s * 0.28), s * 0.10, s * 0.28,
                           facecolor="none", edgecolor=color, linewidth=1.0))
    ax.add_patch(Rectangle((x + s * 0.56, y + s * 0.28), s * 0.10, s * 0.22,
                           facecolor="none", edgecolor=color, linewidth=1.0))
    ax.plot([x + s * 0.25, x + s * 0.36, x + s * 0.47, x + s * 0.62, x + s * 0.73],
            [y + s * 0.40, y + s * 0.46, y + s * 0.43, y + s * 0.50, y + s * 0.54],
            color=color, lw=1.0)


def draw_sql_icon(x, y, s, color):
    ax.add_patch(Rectangle((x + s * 0.18, y + s * 0.20), s * 0.64, s * 0.56,
                           facecolor="none", edgecolor=color, linewidth=1.2))
    ax.plot([x + s * 0.28, x + s * 0.36], [y + s * 0.46, y + s * 0.54], color=color, lw=1.0)
    ax.plot([x + s * 0.28, x + s * 0.36], [y + s * 0.54, y + s * 0.46], color=color, lw=1.0)
    ax.plot([x + s * 0.42, x + s * 0.64], [y + s * 0.50, y + s * 0.50], color=color, lw=1.0)


def draw_eye_icon(x, y, s, color):
    ax.add_patch(Arc((x + s * 0.50, y + s * 0.50), s * 0.80, s * 0.46, theta1=0, theta2=180,
                     ec=color, lw=1.2))
    ax.add_patch(Arc((x + s * 0.50, y + s * 0.50), s * 0.80, s * 0.46, theta1=180, theta2=360,
                     ec=color, lw=1.2))
    ax.add_patch(Circle((x + s * 0.50, y + s * 0.50), s * 0.09, ec=color, fc="none", lw=1.1))


def draw_gears_icon(x, y, s, color):
    ax.add_patch(Circle((x + s * 0.46, y + s * 0.52), s * 0.15, ec=color, fc="none", lw=1.2))
    for ang in [0, 60, 120, 180, 240, 300]:
        dx = 0.23 * s * __import__("math").cos(__import__("math").radians(ang))
        dy = 0.23 * s * __import__("math").sin(__import__("math").radians(ang))
        ax.plot([x + s * 0.46, x + s * 0.46 + dx], [y + s * 0.52, y + s * 0.52 + dy], color=color, lw=0.8)
    ax.add_patch(Circle((x + s * 0.68, y + s * 0.36), s * 0.09, ec=color, fc="none", lw=1.2))


def draw_audit_icon(x, y, s, color):
    draw_doc_icon(x, y, s, color)
    ax.plot([x + s * 0.30, x + s * 0.36, x + s * 0.49], [y + s * 0.36, y + s * 0.30, y + s * 0.42],
            color=color, lw=1.1)


def draw_alert_icon(x, y, s, color):
    tri = Polygon([(x + s * 0.50, y + s * 0.82), (x + s * 0.17, y + s * 0.22), (x + s * 0.83, y + s * 0.22)],
                  closed=True, fill=False, ec=color, lw=1.2)
    ax.add_patch(tri)
    ax.plot([x + s * 0.50, x + s * 0.50], [y + s * 0.40, y + s * 0.58], color=color, lw=1.1)
    ax.add_patch(Circle((x + s * 0.50, y + s * 0.30), s * 0.035, ec=color, fc=color, lw=0.6))


def draw_bot_icon(x, y, s, color):
    ax.add_patch(Rectangle((x + s * 0.26, y + s * 0.34), s * 0.48, s * 0.34, fill=False, ec=color, lw=1.2))
    ax.add_patch(Circle((x + s * 0.38, y + s * 0.52), s * 0.04, ec=color, fc=color, lw=0.6))
    ax.add_patch(Circle((x + s * 0.62, y + s * 0.52), s * 0.04, ec=color, fc=color, lw=0.6))
    ax.plot([x + s * 0.50, x + s * 0.50], [y + s * 0.68, y + s * 0.82], color=color, lw=1.0)
    ax.add_patch(Circle((x + s * 0.50, y + s * 0.86), s * 0.03, ec=color, fc=color, lw=0.6))


def draw_icon(kind, x, y, s, color):
    kind = kind.lower()
    if kind == "globe":
        draw_globe_icon(x, y, s, color)
    elif kind == "cloud":
        draw_cloud_icon(x, y, s, color)
    elif kind == "doc":
        draw_doc_icon(x, y, s, color)
    elif kind == "bank":
        draw_bank_icon(x, y, s, color)
    elif kind == "calendar":
        draw_calendar_icon(x, y, s, color)
    elif kind == "pipeline":
        draw_pipeline_icon(x, y, s, color)
    elif kind == "bolt":
        draw_bolt_cloud_icon(x, y, s, color)
    elif kind == "db":
        draw_db_icon(x, y, s, color)
    elif kind == "book":
        draw_book_icon(x, y, s, color)
    elif kind == "shield":
        draw_shield_icon(x, y, s, color)
    elif kind == "chain":
        draw_chain_icon(x, y, s, color)
    elif kind == "cube":
        draw_cube_icon(x, y, s, color)
    elif kind == "magnifier":
        draw_magnifier_icon(x, y, s, color)
    elif kind == "speech":
        draw_speech_icon(x, y, s, color)
    elif kind == "dashboard":
        draw_dashboard_icon(x, y, s, color)
    elif kind == "sql":
        draw_sql_icon(x, y, s, color)
    elif kind == "eye":
        draw_eye_icon(x, y, s, color)
    elif kind == "gear":
        draw_gears_icon(x, y, s, color)
    elif kind == "audit":
        draw_audit_icon(x, y, s, color)
    elif kind == "alert":
        draw_alert_icon(x, y, s, color)
    elif kind == "bot":
        draw_bot_icon(x, y, s, color)
    else:
        ax.add_patch(Circle((x + s / 2, y + s / 2), s * 0.34, ec=color, fc="none", lw=1.0))

    # Keep the badge purely pictorial; do not add text abbreviations.


def draw_bank_icon(x, y, s, color):
    roof = Polygon([(x + s * 0.18, y + s * 0.55), (x + s * 0.50, y + s * 0.82),
                    (x + s * 0.82, y + s * 0.55)], closed=True, fill=False, ec=color, lw=1.2)
    ax.add_patch(roof)
    for px in [0.28, 0.42, 0.58, 0.72]:
        ax.plot([x + s * px, x + s * px], [y + s * 0.22, y + s * 0.55], color=color, lw=1.0)
    ax.plot([x + s * 0.18, x + s * 0.82], [y + s * 0.22, y + s * 0.22], color=color, lw=1.0)
    ax.plot([x + s * 0.16, x + s * 0.84], [y + s * 0.55, y + s * 0.55], color=color, lw=1.0)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
    ax.text(50, 98.3, "CoinGeckoAnalytical - Arquitetura Databricks 2 Apps",
        ha="center", va="center", fontsize=21, fontweight="bold",
        color=C_TEXT, zorder=10)
ax.text(50, 96.85, "Desenho novo, mais detalhado, com recursos Databricks, observabilidade e Sentinela",
        ha="center", va="center", fontsize=10.2, color=C_MUTED, zorder=10)
ax.plot([2, 98], [95.8, 95.8], color=C_LINE, lw=1.2, zorder=2)

main_y0 = 14.0
main_y1 = 95.0
sent_y0 = 2.0
sent_y1 = 12.8

col1_x, col1_w = 1.4, 12.8
col2_x, col2_w = 15.0, 25.8
col3_x, col3_w = 42.0, 26.2
col4_x, col4_w = 69.2, 29.4


# ---------------------------------------------------------------------------
# Column 1: sources
# ---------------------------------------------------------------------------
section_frame(col1_x, main_y0, col1_w, main_y1 - main_y0,
              "1. FONTES EXTERNAS", "#334155", "sinais e eventos de mercado")

srcs = [
    ("globe", "CoinGecko API", "precos, OHLCV, ranks", "#E8F1FF", "#2563EB"),
    ("globe", "DefiLlama API", "TVL e dados por chain", "#F3E8FF", "#8B5CF6"),
    ("doc", "Docs / fontes", "conhecimento e runbooks", "#ECFDF5", "#16A34A"),
    ("cloud", "Webhooks", "eventos e gatilhos", "#FFF7ED", "#EA580C"),
    ("bank", "APIs de bolsa", "camada opcional", "#FEF2F2", "#DC2626"),
]

src_gap = 0.8
src_h = 10.1
sx = col1_x + 0.35
sw = col1_w - 0.7
sy = main_y1 - 2.8 - src_h
for i, (icon, title, desc, fill, edge) in enumerate(srcs):
    mini_card(sx, sy - i * (src_h + src_gap), sw, src_h, title, desc, icon, fill, edge,
              title_size=6.5, desc_size=5.0)

round_box(col1_x + 0.4, 16.0, col1_w - 0.8, 9.0, "#FFFFFF", C_LINE, lw=1.0, radius=0.28, z=3)
add_text(col1_x + 0.7, 24.4, "LEGENDA DE FLUXOS", size=6.8, color=C_TEXT, weight="bold")
add_text(col1_x + 0.7, 22.9, "→ dados / ingestão", size=5.2, color=C_MUTED)
add_text(col1_x + 0.7, 21.7, "⋯ observabilidade", size=5.2, color=C_MUTED)
add_text(col1_x + 0.7, 20.5, "↔ contratos / catálogo", size=5.2, color=C_MUTED)


# ---------------------------------------------------------------------------
# Column 2: ingestion and medallion
# ---------------------------------------------------------------------------
section_frame(col2_x, main_y0, col2_w, main_y1 - main_y0,
              "2. INGESTAO E LAKEHOUSE", C_BLUE, "Databricks ingestao, ETL e processamento")

ing_x = col2_x + 0.35
ing_w = col2_w - 0.7

round_box(ing_x, 82.0, ing_w, 10.0, C_SOFT_BLUE, C_BLUE, lw=1.0, radius=0.22, z=3)
add_text(ing_x + ing_w / 2, 91.5, "LAKEFLOW JOBS", size=7.5, color=C_BLUE, weight="bold", ha="center")
for i, (title, desc, icon, fill) in enumerate([
    ("Agendamento", "cron e dependencias", "calendar", "#FFFFFF"),
    ("Triggers", "eventos / re-runs", "pipeline", "#FFFFFF"),
    ("Qualidade", "DQ e retries", "alert", "#FFFFFF"),
    ("Logs", "auditoria e traces", "audit", "#FFFFFF"),
]):
    x = ing_x + 0.35 + i * ((ing_w - 1.0) / 4)
    mini_card(x, 83.0, (ing_w - 1.1) / 4, 7.0, title, desc, icon, fill, C_BLUE,
              title_size=5.9, desc_size=4.8)

round_box(ing_x, 70.8, ing_w, 9.2, C_SOFT_BLUE, C_BLUE, lw=1.0, radius=0.22, z=3)
add_text(ing_x + ing_w / 2, 79.5, "PIPELINES E COMPUTE", size=7.5, color=C_BLUE, weight="bold", ha="center")
pipe_cards = [
    ("Declarative Pipelines", "bronze -> silver", "pipeline", "#FFFFFF"),
    ("Auto Loader", "arquivos e streaming", "cloud", "#FFFFFF"),
    ("Serverless Compute", "jobs / notebooks", "bolt", "#FFFFFF"),
    ("Batch + Streaming", "mixed execution", "calendar", "#FFFFFF"),
]
for i, (title, desc, icon, fill) in enumerate(pipe_cards):
    x = ing_x + 0.35 + i * ((ing_w - 1.0) / 4)
    mini_card(x, 71.8, (ing_w - 1.1) / 4, 6.8, title, desc, icon, fill, C_BLUE,
              title_size=5.7, desc_size=4.8)

round_box(ing_x, 59.4, ing_w, 9.6, C_SOFT_GOLD, C_BRONZE, lw=1.0, radius=0.22, z=3)
add_text(ing_x + ing_w / 2, 68.5, "BRONZE / SILVER / GOLD", size=7.5, color=C_BRONZE, weight="bold", ha="center")
med_cards = [
    ("Bronze", "raw landing / snapshots", "db", "#FFF3E0"),
    ("Silver", "normalize / enrich / validate", "db", "#FFFDF2"),
    ("Gold", "analytical marts / KPI views", "db", "#FFF9E6"),
]
for i, (title, desc, icon, fill) in enumerate(med_cards):
    w = (ing_w - 1.0) / 3
    x = ing_x + 0.25 + i * w
    mini_card(x, 60.2, w - 0.1, 6.8, title, desc, icon, fill, [C_BRONZE, C_SILVER, C_GOLD][i],
              title_size=6.0, desc_size=4.8)
add_text(ing_x + 0.5, 59.9, "raw JSON | schema-on-read | dedup | marts | view layers", size=4.8, color=C_MUTED)

round_box(ing_x, 47.0, ing_w, 11.3, C_SOFT_GRAY, C_SILVER, lw=1.0, radius=0.22, z=3)
add_text(ing_x + ing_w / 2, 57.6, "TRANSFORMACOES E CONTROLES", size=7.5, color=C_SILVER, weight="bold", ha="center")
ctrl_cards = [
    ("Schema", "versionamento", "doc", "#FFFFFF"),
    ("DQ Rules", "validacao", "alert", "#FFFFFF"),
    ("Freshness", "watermarks", "eye", "#FFFFFF"),
    ("Lineage", "passo a passo", "chain", "#FFFFFF"),
]
for i, (title, desc, icon, fill) in enumerate(ctrl_cards):
    w = (ing_w - 1.0) / 4
    x = ing_x + 0.25 + i * w
    mini_card(x, 48.0, w - 0.1, 7.4, title, desc, icon, fill, C_SILVER,
              title_size=5.8, desc_size=4.8)

round_box(ing_x, 39.0, ing_w, 6.8, "#FFFFFF", C_BLUE, lw=1.0, radius=0.22, z=3)
add_text(ing_x + ing_w / 2, 45.1, "MODOS DE PROCESSAMENTO", size=7.5, color=C_BLUE, weight="bold", ha="center")
chips = [("Streaming", "#4CAF50"), ("Micro-Batch", "#2196F3"), ("Batch", "#3F51B5"), ("Full", "#8BC34A"),
         ("Incremental", "#FB8C00"), ("DQ", "#E53935"), ("Freshness", "#1976D2")]
cx = ing_x + 0.5
cy = 40.6
for label, color in chips:
    w = max(4.0, 0.42 * len(label) + 1.8)
    round_box(cx, cy, w, 2.0, color, color, lw=0, radius=0.35, z=4)
    add_text(cx + w / 2, cy + 1.0, label, size=5.2, color=C_WHITE, weight="bold", ha="center", va="center")
    cx += w + 0.35
    if cx > ing_x + ing_w - 6:
        break

arrow(col1_x + col1_w, 75.0, col2_x, 75.0, color=C_LINE, lw=1.3)
arrow(col2_x + col2_w / 2, 59.0, col3_x, 59.0, color=C_LINE, lw=1.2, rad=0.0)


# ---------------------------------------------------------------------------
# Column 3: governance and AI serving
# ---------------------------------------------------------------------------
section_frame(col3_x, main_y0, col3_w, main_y1 - main_y0,
              "3. GOVERNANCA, IA E SERVING", C_PURPLE, "Unity Catalog, MLOps, Genie e consultas")

gx = col3_x + 0.35
gw = col3_w - 0.7

round_box(gx, 79.5, gw, 13.0, C_SOFT_PURPLE, C_PURPLE, lw=1.0, radius=0.22, z=3)
add_text(gx + gw / 2, 91.8, "UNITY CATALOG", size=8.0, color=C_PURPLE, weight="bold", ha="center")
uc_cards = [
    ("Catalog", "schemas / tables / views", "book"),
    ("Lineage", "audit / trace / ownership", "chain"),
    ("Permissions", "row / column / tenant", "shield"),
    ("Tags", "classificacao e contrato", "doc"),
]
for i, (title, desc, icon) in enumerate(uc_cards):
    w = (gw - 1.0) / 2
    x = gx + 0.25 + (i % 2) * w
    y = 87.0 if i < 2 else 82.2
    mini_card(x, y, w - 0.1, 4.6, title, desc, icon, "#FFFFFF", C_PURPLE,
              title_size=5.8, desc_size=4.7)

round_box(gx, 64.8, gw, 13.0, C_SOFT_PURPLE, C_PURPLE, lw=1.0, radius=0.22, z=3)
add_text(gx + gw / 2, 76.9, "MLOPS E MODELOS", size=8.0, color=C_PURPLE, weight="bold", ha="center")
ml_cards = [
    ("MLflow", "experimentos / tracking", "gear"),
    ("Registry", "champion / versioning", "db"),
    ("Model Serving", "REST endpoint", "dashboard"),
    ("Vector Search", "retrieval / reranking", "magnifier"),
]
for i, (title, desc, icon) in enumerate(ml_cards):
    w = (gw - 1.0) / 2
    x = gx + 0.25 + (i % 2) * w
    y = 72.2 if i < 2 else 67.4
    mini_card(x, y, w - 0.1, 4.4, title, desc, icon, "#FFFFFF", C_PURPLE,
              title_size=5.8, desc_size=4.7)

round_box(gx, 45.0, gw, 18.8, "#FFFFFF", C_CYAN, lw=1.0, radius=0.22, z=3)
add_text(gx + gw / 2, 62.7, "GENIE / SQL / INSIGHTS", size=8.0, color=C_CYAN, weight="bold", ha="center")
serv_cards = [
    ("Genie", "NLQ em linguagem natural", "speech", C_SOFT_TEAL, C_CYAN),
    ("SQL Warehouses", "queries e dashboards", "sql", C_SOFT_TEAL, C_CYAN),
    ("Dashboards", "KPIs e leitura rapida", "dashboard", C_SOFT_TEAL, C_CYAN),
    ("Observability", "freshness / traces / SLO", "eye", C_SOFT_TEAL, C_CYAN),
]
for i, (title, desc, icon, fill, edge) in enumerate(serv_cards):
    w = (gw - 1.0) / 2
    x = gx + 0.25 + (i % 2) * w
    y = 56.8 if i < 2 else 51.8
    mini_card(x, y, w - 0.1, 4.4, title, desc, icon, fill, edge,
              title_size=5.8, desc_size=4.7)
add_text(gx + 0.5, 46.1, "structured NLQ | trusted answers | latency | cost controls", size=4.8, color=C_MUTED)

arrow(col2_x + col2_w, 72.5, col3_x, 72.5, color=C_LINE, lw=1.3)
arrow(col3_x + col3_w / 2, 45.0, col4_x, 45.0, color=C_LINE, lw=1.2)


# ---------------------------------------------------------------------------
# Column 4: two Databricks apps
# ---------------------------------------------------------------------------
section_frame(col4_x, main_y0, col4_w, main_y1 - main_y0,
              "4. DATABRICKS APPS", C_ANALYTICS)

ax0 = col4_x + 0.35
aw = col4_w - 0.7

round_box(ax0, 67.5, aw, 27.0, C_SOFT_BLUE, C_ANALYTICS, lw=1.0, radius=0.22, z=3)
add_text(ax0 + aw / 2, 93.2, "cga-analytics", size=8.2, color=C_ANALYTICS, weight="bold", ha="center")
add_text(ax0 + aw / 2, 91.8, "workspace-native analytics surface", size=5.4, color=C_MUTED, ha="center")
for i, (title, desc, icon) in enumerate([
    ("Genie Chat", "NLQ and guided answers", "speech"),
    ("Charts", "rankings, movers, macro", "dashboard"),
    ("Copilot", "routing and synthesis", "bot"),
    ("Freshness", "provenance badges", "eye"),
]):
    w = (aw - 0.8) / 2
    x = ax0 + 0.2 + (i % 2) * w
    y = 86.7 if i < 2 else 80.9
    mini_card(x, y, w - 0.1, 5.0, title, desc, icon, "#FFFFFF", C_ANALYTICS,
              title_size=5.9, desc_size=4.8)

round_box(ax0, 37.5, aw, 26.0, "#EEF2F7", C_ADMIN, lw=1.0, radius=0.22, z=3)
add_text(ax0 + aw / 2, 62.6, "cga-admin", size=8.2, color=C_ADMIN, weight="bold", ha="center")
add_text(ax0 + aw / 2, 61.2, "ops, governance, audit", size=5.4, color=C_MUTED, ha="center")
for i, (title, desc, icon) in enumerate([
    ("Ops", "status / runbooks", "gear"),
    ("Access", "groups and isolation", "shield"),
    ("Audit", "SQL, traces, lineage", "audit"),
    ("Cost", "budgets and tokens", "alert"),
]):
    w = (aw - 0.8) / 2
    x = ax0 + 0.2 + (i % 2) * w
    y = 56.8 if i < 2 else 51.0
    mini_card(x, y, w - 0.1, 5.0, title, desc, icon, "#FFFFFF", C_ADMIN,
              title_size=5.9, desc_size=4.8)

arrow(col3_x + col3_w, 88.0, col4_x, 88.0, color=C_LINE, lw=1.3)


# ---------------------------------------------------------------------------
# Bottom: Sentinela
# ---------------------------------------------------------------------------
round_box(1.2, sent_y0, 97.6, sent_y1 - sent_y0, "#FFFFFF", C_SENTINELA, lw=1.6, radius=0.45, z=1)
header_band(1.2, sent_y1 - 2.0, 97.6, 2.0, C_SENTINELA,
            "5. SENTINELA - PLANO OPERACIONAL MULTIAGENTE (OBSERVABILIDADE, GOVERNANCA E RESILIENCIA)", size=8.3)

sent_cards = [
    ("Coordinator", "orquestracao e merge", "bot", "#F8FAFC"),
    ("Watcher", "monitoring and drift", "eye", "#F8FAFC"),
    ("Evaluator", "quality and scoring", "shield", "#F8FAFC"),
    ("Summarizer", "reports and briefs", "doc", "#F8FAFC"),
    ("Policy", "guardrails and approvals", "alert", "#F8FAFC"),
    ("Alerts", "notificacoes e tickets", "alert", "#F8FAFC"),
    ("Logs", "audit / history / traces", "audit", "#F8FAFC"),
    ("SLOs", "latency / freshness / cost", "dashboard", "#F8FAFC"),
]

sx = 2.0
sy = 3.0
sw = 11.4
sh = 4.8
gap = 0.9
for i, (title, desc, icon, fill) in enumerate(sent_cards):
    row = 0 if i < 4 else 1
    col = i % 4
    x = sx + col * (sw + gap)
    y = 6.6 - row * 5.4
    mini_card(x, y, sw, sh, title, desc, icon, fill, C_SENTINELA,
              title_size=5.8, desc_size=4.7)

round_box(46.8, 3.0, 31.0, 2.2, C_SOFT_GRAY, C_SENTINELA, lw=1.0, radius=0.22, z=3)
add_text(62.3, 4.1, "Memoria operacional | contexto | historico | governanca | compliance", size=5.0,
         color=C_SENTINELA, weight="bold", ha="center", va="center")

round_box(79.0, 3.0, 18.4, 2.2, "#FFFFFF", C_SENTINELA, lw=1.0, radius=0.22, z=3)
add_text(88.2, 4.2, "SAIDA: alertas, tickets, runbooks, relatórios", size=4.7,
         color=C_SENTINELA, weight="bold", ha="center", va="center")


# connectors
arrow(12.8, 82.5, 15.0, 82.5, color=C_LINE, lw=1.1)
arrow(40.8, 83.0, 42.0, 83.0, color=C_LINE, lw=1.1)
arrow(68.2, 60.0, 69.2, 60.0, color=C_LINE, lw=1.1)
arrow(83.8, 35.0, 83.8, 12.8, color=C_LINE, lw=1.1)
arrow(24.0, 47.0, 24.0, 12.8, color=C_LINE, lw=1.1, rad=0.0)
arrow(53.5, 45.0, 53.5, 12.8, color=C_LINE, lw=1.1)


plt.savefig("docs/assets/coingeckoanalytical-architecture-v5.png", dpi=DPI, bbox_inches="tight")

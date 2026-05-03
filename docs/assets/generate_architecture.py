"""
generate_architecture.py
Generates the CoinGeckoAnalytical platform architecture diagram.
Output: coingeckoanalytical-architecture.png (6000x3800 px @ 150 dpi)
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

# ---------------------------------------------------------------------------
# Canvas setup
# ---------------------------------------------------------------------------
DPI = 150
FIG_W_IN = 6000 / DPI   # 40.0 inches
FIG_H_IN = 3800 / DPI   # 25.333 inches

fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")
fig.patch.set_facecolor("#F5F5F5")
ax.set_facecolor("#F5F5F5")

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
C_BRONZE       = "#CD7F32"
C_SILVER       = "#708090"
C_GOLD         = "#DAA520"
C_UNITY        = "#1565C0"
C_GENIE        = "#6A0DAD"
C_ORCH         = "#1B5E20"
C_GATEWAY      = "#00695C"
C_APP_ANAL     = "#0D47A1"
C_APP_ADMIN    = "#263238"
C_SENTINELA    = "#B71C1C"
C_SOURCES      = "#37474F"
C_ARROW        = "#455A64"
C_WHITE        = "#FFFFFF"
C_LIGHT_GREY   = "#ECEFF1"
C_DARK_TEXT    = "#212121"
C_HEADER_TEXT  = "#FFFFFF"

# ---------------------------------------------------------------------------
# Helper primitives
# ---------------------------------------------------------------------------

def fancy_box(ax, x, y, w, h, facecolor, edgecolor="#CCCCCC",
              linewidth=1.2, radius=0.5, alpha=1.0, zorder=2):
    """Draw a rounded rectangle."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        alpha=alpha,
        zorder=zorder,
    )
    ax.add_patch(box)
    return box


def header_band(ax, x, y, w, h, color, text, fontsize=9, zorder=3):
    """Colored header band with white text."""
    fancy_box(ax, x, y, w, h, facecolor=color, edgecolor=color,
              linewidth=0, radius=0.4, zorder=zorder)
    ax.text(
        x + w / 2, y + h / 2, text,
        ha="center", va="center",
        fontsize=fontsize, fontweight="bold",
        color=C_WHITE, zorder=zorder + 1,
        fontfamily="DejaVu Sans",
    )


def component_box(ax, x, y, w, h, icon, name, desc,
                  bg_color=C_LIGHT_GREY, border_color="#AAAAAA",
                  name_size=7.5, desc_size=6.0, zorder=4):
    """Individual component card with icon, bold name, and description."""
    fancy_box(ax, x, y, w, h, facecolor=bg_color, edgecolor=border_color,
              linewidth=1.0, radius=0.35, zorder=zorder)
    # Icon + name on same line at top
    ax.text(
        x + 0.35, y + h - 0.30, f"{icon}  {name}",
        ha="left", va="top",
        fontsize=name_size, fontweight="bold",
        color=C_DARK_TEXT, zorder=zorder + 1,
        fontfamily="DejaVu Sans",
        clip_on=True,
    )
    # Description wrapped in smaller text
    if desc:
        ax.text(
            x + 0.35, y + h - 0.78, desc,
            ha="left", va="top",
            fontsize=desc_size,
            color="#546E7A", zorder=zorder + 1,
            fontfamily="DejaVu Sans",
            wrap=True,
            clip_on=True,
        )


def section_container(ax, x, y, w, h, label, color, label_size=9.5,
                       edge_lw=2.0, zorder=1):
    """Large section container with colored left border stripe."""
    fancy_box(ax, x, y, w, h, facecolor="#FAFAFA", edgecolor=color,
              linewidth=edge_lw, radius=0.6, zorder=zorder)
    # Vertical label on left side
    ax.text(
        x + 0.35, y + h / 2, label,
        ha="center", va="center",
        fontsize=label_size, fontweight="bold",
        color=color, zorder=zorder + 1,
        fontfamily="DejaVu Sans",
        rotation=90,
    )


def arrow(ax, x0, y0, x1, y1, color=C_ARROW, lw=1.8,
          label="", label_size=6.2, connectionstyle="arc3,rad=0.0", zorder=5):
    """Draw a fancy arrow with optional label."""
    arr = FancyArrowPatch(
        (x0, y0), (x1, y1),
        arrowstyle="-|>",
        color=color,
        linewidth=lw,
        connectionstyle=connectionstyle,
        mutation_scale=12,
        zorder=zorder,
    )
    ax.add_patch(arr)
    if label:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(
            mx, my, label,
            ha="center", va="center",
            fontsize=label_size, color=color,
            fontfamily="DejaVu Sans",
            zorder=zorder + 1,
            bbox=dict(boxstyle="round,pad=0.2", fc="#F5F5F5", ec=color,
                      lw=0.6, alpha=0.9),
        )


# ---------------------------------------------------------------------------
# TITLE
# ---------------------------------------------------------------------------
ax.text(
    50, 98.2,
    "CoinGeckoAnalytical — Arquitetura Completa v2",
    ha="center", va="center",
    fontsize=20, fontweight="bold",
    color=C_DARK_TEXT, fontfamily="DejaVu Sans",
    zorder=10,
)
ax.text(
    50, 96.8,
    "Databricks-native  ·  Duas Apps  ·  Genie como controlador de gráficos  ·  Orquestrador multi-agente",
    ha="center", va="center",
    fontsize=10.5, color="#546E7A",
    fontfamily="DejaVu Sans",
    zorder=10,
)

# Horizontal divider under title
ax.axhline(y=95.8, xmin=0.01, xmax=0.99, color="#CFD8DC", linewidth=1.2, zorder=3)

# ---------------------------------------------------------------------------
# LAYOUT CONSTANTS  (coordinate system 0-100 x 0-100)
# Columns: Sources | Databricks Platform | AI & Serving | Apps
# Row bands: top=title, main content 8..95, bottom=sentinela 2..8
# ---------------------------------------------------------------------------
MAIN_Y_BOT  = 10.5
MAIN_Y_TOP  = 95.0
MAIN_H      = MAIN_Y_TOP - MAIN_Y_BOT

SENT_Y_BOT  = 1.5
SENT_Y_TOP  = 9.8

# Column X boundaries
COL1_X  = 1.5     # Sources
COL1_W  = 11.5

COL2_X  = 14.5    # Databricks Platform
COL2_W  = 27.0

COL3_X  = 43.5    # AI & Serving
COL3_W  = 26.0

COL4_X  = 71.5    # Apps
COL4_W  = 26.5

# ---------------------------------------------------------------------------
# COLUMN 1 — External Data Sources
# ---------------------------------------------------------------------------
section_container(ax, COL1_X, MAIN_Y_BOT, COL1_W, MAIN_H,
                  "External\nSources", C_SOURCES, label_size=8.5, zorder=1)

src_header_h = 1.0
src_box_h    = 5.8
src_gap      = 1.8
src_x        = COL1_X + 1.2
src_w        = COL1_W - 2.0

sources = [
    ("CG",  "CoinGecko API",   "Market data\nnear-realtime\nprices, OHLCV, ranks",  "#FFF8E1", "#F9A825"),
    ("DL",  "DefiLlama API",   "TVL per protocol\nchain breakdown\nDeFi metrics",    "#F3E5F5", "#7B1FA2"),
    ("GH",  "GitHub API",      "Dev activity\ncommit frequency\ncontributor count",  "#E8F5E9", "#2E7D32"),
    ("FR",  "FRED API",        "Macro indicators\nrates, M2, CPI\nDXY, yield curve", "#E3F2FD", "#1565C0"),
]

src_y_start = MAIN_Y_TOP - 1.5
for i, (icon, name, desc, bg, border) in enumerate(sources):
    by = src_y_start - i * (src_box_h + src_gap)
    # colored badge icon
    fancy_box(ax, src_x, by - src_box_h, src_w, src_box_h,
              facecolor=bg, edgecolor=border, linewidth=1.5, radius=0.5, zorder=4)
    ax.text(src_x + src_w / 2, by - 0.6, icon,
            ha="center", va="top", fontsize=10, fontweight="bold",
            color=border, fontfamily="DejaVu Sans", zorder=5)
    ax.text(src_x + src_w / 2, by - 1.5, name,
            ha="center", va="top", fontsize=7.5, fontweight="bold",
            color=C_DARK_TEXT, fontfamily="DejaVu Sans", zorder=5)
    ax.text(src_x + src_w / 2, by - 2.4, desc,
            ha="center", va="top", fontsize=6.0,
            color="#546E7A", fontfamily="DejaVu Sans", zorder=5,
            multialignment="center")

# ---------------------------------------------------------------------------
# COLUMN 2 — Databricks Data Platform
# ---------------------------------------------------------------------------
section_container(ax, COL2_X, MAIN_Y_BOT, COL2_W, MAIN_H,
                  "Databricks  Data  Platform", C_BRONZE, label_size=8.5, zorder=1)

db_inner_x  = COL2_X + 1.5
db_inner_w  = COL2_W - 2.5

# ---- Vertical split for layers ----
# Bronze: 4 tables
# Silver: 3 tables
# Gold:   6 tables
# Unity Catalog: governance footer

layer_gap   = 0.8
unity_h     = 6.5
gold_h      = 20.0
silver_h    = 14.5
bronze_h    = 22.0

unity_y  = MAIN_Y_BOT + 0.8
gold_y   = unity_y  + unity_h  + layer_gap
silver_y = gold_y   + gold_h   + layer_gap
bronze_y = silver_y + silver_h + layer_gap

# ---- Bronze Layer ----
header_band(ax, db_inner_x, bronze_y + bronze_h - 1.4, db_inner_w, 1.4,
            C_BRONZE, "BRONZE LAYER  —  Raw Landing · Delta Lake · Source Snapshots",
            fontsize=8, zorder=5)
fancy_box(ax, db_inner_x, bronze_y, db_inner_w, bronze_h,
          facecolor="#FFF3E0", edgecolor=C_BRONZE, linewidth=1.5, radius=0.4, zorder=3)

bronze_tables = [
    ("bronze_market_data",         "CoinGecko snapshots · OHLCV · raw JSON preserved"),
    ("bronze_defillama_protocols", "TVL snapshots · protocol registry · chain data"),
    ("bronze_github_activity",     "Commit events · contributor stats · repo metadata"),
    ("bronze_fred_macro",          "Rate series · M2 · CPI · DXY · yield curve data"),
]
bt_h  = 3.5
bt_gap = 0.55
bt_x  = db_inner_x + 0.5
bt_w  = db_inner_w - 1.0
for i, (tname, tdesc) in enumerate(bronze_tables):
    ty = bronze_y + bronze_h - 1.8 - i * (bt_h + bt_gap) - bt_h
    component_box(ax, bt_x, ty, bt_w, bt_h,
                  icon="db", name=tname, desc=tdesc,
                  bg_color="#FFE0B2", border_color=C_BRONZE,
                  name_size=7.0, desc_size=5.8, zorder=6)

# ---- Silver Layer ----
header_band(ax, db_inner_x, silver_y + silver_h - 1.4, db_inner_w, 1.4,
            C_SILVER, "SILVER LAYER  —  Normalization · Enrichment · Validation",
            fontsize=8, zorder=5)
fancy_box(ax, db_inner_x, silver_y, db_inner_w, silver_h,
          facecolor="#ECEFF1", edgecolor=C_SILVER, linewidth=1.5, radius=0.4, zorder=3)

silver_tables = [
    ("silver_market_normalized", "Cleaned prices · volume · market cap · dedup"),
    ("silver_asset_enriched",    "Asset metadata join · sector tags · category"),
    ("silver_macro_regime",      "Regime classification · rate + M2 signal blend"),
]
st_h  = 3.2
st_gap = 0.45
st_x  = db_inner_x + 0.5
st_w  = db_inner_w - 1.0
for i, (tname, tdesc) in enumerate(silver_tables):
    ty = silver_y + silver_h - 1.8 - i * (st_h + st_gap) - st_h
    component_box(ax, st_x, ty, st_w, st_h,
                  icon=">>", name=tname, desc=tdesc,
                  bg_color="#CFD8DC", border_color=C_SILVER,
                  name_size=7.0, desc_size=5.8, zorder=6)

# ---- Gold Layer ----
header_band(ax, db_inner_x, gold_y + gold_h - 1.4, db_inner_w, 1.4,
            C_GOLD, "GOLD LAYER  —  Analytical Mart Views  ·  Unity Catalog Governed",
            fontsize=8, zorder=5)
fancy_box(ax, db_inner_x, gold_y, db_inner_w, gold_h,
          facecolor="#FFFDE7", edgecolor=C_GOLD, linewidth=1.5, radius=0.4, zorder=3)

gold_tables = [
    ("gold_market_rankings",    "Ranked assets by mcap · vol · 24h change"),
    ("gold_top_movers",         "Biggest gainers & losers · momentum signals"),
    ("gold_market_dominance",   "BTC/ETH dominance · sector weight breakdown"),
    ("gold_defi_protocols",     "TVL leaderboard · chain dist · protocol health"),
    ("gold_macro_regime",       "Current regime label · rate trend · M2 signal"),
    ("gold_enriched_rankings",  "Joined gold mart · sector + macro overlay"),
]
gt_h  = 2.4
gt_gap = 0.38
gt_x  = db_inner_x + 0.5
gt_w  = db_inner_w - 1.0
for i, (tname, tdesc) in enumerate(gold_tables):
    ty = gold_y + gold_h - 1.8 - i * (gt_h + gt_gap) - gt_h
    component_box(ax, gt_x, ty, gt_w, gt_h,
                  icon="*", name=tname, desc=tdesc,
                  bg_color="#FFF9C4", border_color=C_GOLD,
                  name_size=6.8, desc_size=5.6, zorder=6)

# ---- Unity Catalog ----
header_band(ax, db_inner_x, unity_y + unity_h - 1.4, db_inner_w, 1.4,
            C_UNITY, "UNITY CATALOG  —  Governance · Lineage · Permissions · Model Lifecycle",
            fontsize=8, zorder=5)
fancy_box(ax, db_inner_x, unity_y, db_inner_w, unity_h,
          facecolor="#E3F2FD", edgecolor=C_UNITY, linewidth=1.5, radius=0.4, zorder=3)

uc_items = [
    ("UC", "Data Lineage & Audit",     "Column-level lineage · access audit trail"),
    ("UC", "Access Policies",          "Row/column filters · tenant isolation"),
    ("UC", "Model Registry",           "MLflow model versions · champion tracking"),
]
uci_h   = 1.5
uci_gap = 0.3
uci_x   = db_inner_x + 0.5
uci_w   = (db_inner_w - 1.5) / 3 - 0.2
for i, (icon, name, desc) in enumerate(uc_items):
    xi = uci_x + i * (uci_w + 0.25)
    component_box(ax, xi, unity_y + 0.3, uci_w, uci_h + 0.8,
                  icon=icon, name=name, desc=desc,
                  bg_color="#BBDEFB", border_color=C_UNITY,
                  name_size=6.5, desc_size=5.4, zorder=6)

# ---------------------------------------------------------------------------
# COLUMN 3 — AI & Serving
# ---------------------------------------------------------------------------
section_container(ax, COL3_X, MAIN_Y_BOT, COL3_W, MAIN_H,
                  "AI  &  Serving", C_GENIE, label_size=8.5, zorder=1)

ai_inner_x = COL3_X + 1.5
ai_inner_w = COL3_W - 2.5

# Heights for sub-sections
gateway_h   = 13.5
orch_h      = 28.0
genie_h     = 18.0
ai_gap      = 1.0

gateway_y   = MAIN_Y_BOT + 0.8
orch_y      = gateway_y  + gateway_h + ai_gap
genie_y     = orch_y     + orch_h    + ai_gap

# ---- Genie ----
header_band(ax, ai_inner_x, genie_y + genie_h - 1.4, ai_inner_w, 1.4,
            C_GENIE, "AI/BI GENIE  —  Structured NLQ over Gold Views",
            fontsize=8, zorder=5)
fancy_box(ax, ai_inner_x, genie_y, ai_inner_w, genie_h,
          facecolor="#F3E5F5", edgecolor=C_GENIE, linewidth=1.5, radius=0.4, zorder=3)

genie_comps = [
    ("G", "NLQ Interface",        "Natural language → SQL plan\nstructured intent extraction"),
    ("G", "SQL Generator",        "Generates executable SQL\nagainst gold mart views"),
    ("G", "Answer Renderer",      "answer_text + generated_query\nfreshness badge · confidence"),
    ("G", "Gold View Connector",  "Read-only access to gold layer\nUnity Catalog governed"),
]
gc_h   = 3.2
gc_gap = 0.5
gc_x   = ai_inner_x + 0.4
gc_w   = ai_inner_w - 0.8
for i, (icon, name, desc) in enumerate(genie_comps):
    gy = genie_y + genie_h - 1.8 - i * (gc_h + gc_gap) - gc_h
    component_box(ax, gc_x, gy, gc_w, gc_h,
                  icon=icon, name=name, desc=desc,
                  bg_color="#E1BEE7", border_color=C_GENIE,
                  name_size=7.0, desc_size=5.8, zorder=6)

# ---- Multi-Agent Orchestrator ----
header_band(ax, ai_inner_x, orch_y + orch_h - 1.4, ai_inner_w, 1.4,
            C_ORCH, "MULTI-AGENT ORCHESTRATOR  —  3 Domain Agents + Synthesis",
            fontsize=8, zorder=5)
fancy_box(ax, ai_inner_x, orch_y, ai_inner_w, orch_h,
          facecolor="#E8F5E9", edgecolor=C_ORCH, linewidth=1.5, radius=0.4, zorder=3)

orch_comps = [
    ("MA", "MarketAgent",   "gpt-oss-120b / standard\nPrice action · rankings · momentum\nRetrieves gold_market_rankings"),
    ("MA", "MacroAgent",    "gpt-oss-120b / standard\nRate regime · M2 · CPI · DXY\nRetrieves gold_macro_regime"),
    ("DA", "DefiAgent",     "gpt-oss-120b / standard\nTVL · protocol health · chains\nRetrieves gold_defi_protocols"),
    ("SA", "SynthAgent",    "qwen3-80b / complex tier\nCross-domain synthesis\nFinal answer + provenance"),
    ("OC", "Orchestrator",  "orchestrate() entry point\nParallel fan-out · merge\nToken + cost telemetry"),
]
oc_h   = 4.2
oc_gap = 0.6
oc_x   = ai_inner_x + 0.4
oc_w   = ai_inner_w - 0.8
for i, (icon, name, desc) in enumerate(orch_comps):
    oy = orch_y + orch_h - 1.8 - i * (oc_h + oc_gap) - oc_h
    component_box(ax, oc_x, oy, oc_w, oc_h,
                  icon=icon, name=name, desc=desc,
                  bg_color="#C8E6C9", border_color=C_ORCH,
                  name_size=7.0, desc_size=5.8, zorder=6)

# ---- Unity AI Gateway ----
header_band(ax, ai_inner_x, gateway_y + gateway_h - 1.4, ai_inner_w, 1.4,
            C_GATEWAY, "UNITY AI GATEWAY  —  3 Model Tiers",
            fontsize=8, zorder=5)
fancy_box(ax, ai_inner_x, gateway_y, ai_inner_w, gateway_h,
          facecolor="#E0F2F1", edgecolor=C_GATEWAY, linewidth=1.5, radius=0.4, zorder=3)

gw_comps = [
    ("LT", "Light Tier",    "gemma-3-12b\nFast classification\nlow-cost routing"),
    ("ST", "Standard Tier", "gpt-oss-120b\nDomain agents\nbalanced quality+cost"),
    ("CT", "Complex Tier",  "qwen3-next-80b-a3b\nSynthesis + reasoning\nmax quality"),
]
gw_h   = 3.2
gw_gap = 0.45
gw_x   = ai_inner_x + 0.4
gw_w   = ai_inner_w - 0.8
for i, (icon, name, desc) in enumerate(gw_comps):
    gy = gateway_y + gateway_h - 1.8 - i * (gw_h + gw_gap) - gw_h
    component_box(ax, gw_x, gy, gw_w, gw_h,
                  icon=icon, name=name, desc=desc,
                  bg_color="#B2DFDB", border_color=C_GATEWAY,
                  name_size=7.0, desc_size=5.8, zorder=6)

# ---------------------------------------------------------------------------
# COLUMN 4 — Databricks Apps
# ---------------------------------------------------------------------------
section_container(ax, COL4_X, MAIN_Y_BOT, COL4_W, MAIN_H,
                  "Databricks  Apps", C_APP_ANAL, label_size=8.5, zorder=1)

app_inner_x = COL4_X + 1.5
app_inner_w = COL4_W - 2.5

# Two apps stacked
app_gap       = 1.2
admin_h       = 30.0
analytics_h   = MAIN_H - admin_h - app_gap - 2.0

admin_y       = MAIN_Y_BOT + 0.8
analytics_y   = admin_y + admin_h + app_gap

# ---- cga-admin App ----
header_band(ax, app_inner_x, admin_y + admin_h - 1.6, app_inner_w, 1.6,
            C_APP_ADMIN, "cga-admin  —  Internal Ops & Administration",
            fontsize=8, zorder=5)
fancy_box(ax, app_inner_x, admin_y, app_inner_w, admin_h,
          facecolor="#ECEFF1", edgecolor=C_APP_ADMIN, linewidth=2.0, radius=0.5, zorder=3)

admin_comps = [
    ("SD", "Sentinela Dashboard",  "Pipeline alerts · freshness SLA\nquality signal heatmap"),
    ("PH", "Pipeline Health",      "Ingestion status per source\nlast run · row counts · lag"),
    ("CT", "Cost & Token Monitor", "Spend by tier + tenant\nLLMOps budget controls"),
    ("AM", "Access Management",    "Unity Catalog groups\ntenant isolation rules"),
    ("AT", "Audit Trail",          "Request traces · generated SQL\nfull provenance log"),
]
ac_h   = 4.2
ac_gap = 0.55
ac_x   = app_inner_x + 0.4
ac_w   = app_inner_w - 0.8
for i, (icon, name, desc) in enumerate(admin_comps):
    ay = admin_y + admin_h - 2.0 - i * (ac_h + ac_gap) - ac_h
    component_box(ax, ac_x, ay, ac_w, ac_h,
                  icon=icon, name=name, desc=desc,
                  bg_color="#CFD8DC", border_color=C_APP_ADMIN,
                  name_size=7.0, desc_size=5.8, zorder=6)

# ---- cga-analytics App ----
header_band(ax, app_inner_x, analytics_y + analytics_h - 1.6, app_inner_w, 1.6,
            C_APP_ANAL, "cga-analytics  —  Public Market Intelligence Surface",
            fontsize=8, zorder=5)
fancy_box(ax, app_inner_x, analytics_y, app_inner_w, analytics_h,
          facecolor="#E3F2FD", edgecolor=C_APP_ANAL, linewidth=2.0, radius=0.5, zorder=3)

anal_comps = [
    ("GC", "Genie Chat Panel",   "NLQ input → Genie API\nSQL result → chart state update"),
    ("CD", "Chart Dashboard",    "Rankings / DeFi TVL / Macro\nMovers · reactive chart state"),
    ("CP", "Copilot Panel",      "Tier classification → orchestrator\norchestrate() call path"),
    ("FP", "Freshness & Prov.",  "Freshness badges per data source\nprovenance + confidence tags"),
]
nc_h   = 4.8
nc_gap = 0.7
nc_x   = app_inner_x + 0.4
nc_w   = app_inner_w - 0.8
for i, (icon, name, desc) in enumerate(anal_comps):
    ny = analytics_y + analytics_h - 2.0 - i * (nc_h + nc_gap) - nc_h
    component_box(ax, nc_x, ny, nc_w, nc_h,
                  icon=icon, name=name, desc=desc,
                  bg_color="#BBDEFB", border_color=C_APP_ANAL,
                  name_size=7.0, desc_size=5.8, zorder=6)

# ---------------------------------------------------------------------------
# BOTTOM ROW — Sentinela Ops Plane
# ---------------------------------------------------------------------------
sent_x = 1.5
sent_w = 96.0
sent_h = SENT_Y_TOP - SENT_Y_BOT

header_band(ax, sent_x, SENT_Y_TOP - 1.3, sent_w, 1.3,
            C_SENTINELA, "SENTINELA OPS PLANE  —  Observability · DataOps · LLMOps · CI/CD",
            fontsize=9, zorder=5)
fancy_box(ax, sent_x, SENT_Y_BOT, sent_w, sent_h,
          facecolor="#FFEBEE", edgecolor=C_SENTINELA, linewidth=2.0, radius=0.5, zorder=3)

sent_items = [
    ("SM", "Ingestion Monitoring",  "Freshness alerting\nquality signals"),
    ("TK", "Token Cost Telemetry",  "Spend by tier+tenant\nLLMOps observability"),
    ("RG", "Release Gates",         "Runbooks · ops readiness\napproval workflows"),
    ("CI", "CI/CD Pipeline",        "Asset Bundles · OAuth M2M\nGitHub Actions"),
    ("QA", "Data Quality",          "Schema validation · DQ rules\ndrift detection"),
    ("AL", "Alerting & Runbooks",   "PagerDuty / Slack\nincident playbooks"),
]
si_w   = (sent_w - 1.0) / len(sent_items) - 0.5
si_h   = sent_h - 1.8
si_y   = SENT_Y_BOT + 0.3
for i, (icon, name, desc) in enumerate(sent_items):
    si_x = sent_x + 0.5 + i * (si_w + 0.5)
    component_box(ax, si_x, si_y, si_w, si_h,
                  icon=icon, name=name, desc=desc,
                  bg_color="#FFCDD2", border_color=C_SENTINELA,
                  name_size=7.0, desc_size=5.8, zorder=6)

# ---------------------------------------------------------------------------
# DATA FLOW ARROWS
# ---------------------------------------------------------------------------

# Sources → Bronze  (one arrow per source, right edge of col1 to left edge of col2)
src_arrow_xs = [
    (COL1_X + COL1_W,  MAIN_Y_TOP - 5.0),   # CoinGecko
    (COL1_X + COL1_W,  MAIN_Y_TOP - 13.0),  # DefiLlama
    (COL1_X + COL1_W,  MAIN_Y_TOP - 21.0),  # GitHub
    (COL1_X + COL1_W,  MAIN_Y_TOP - 29.0),  # FRED
]
bronze_target_ys = [
    bronze_y + bronze_h - 3.5,
    bronze_y + bronze_h - 7.5,
    bronze_y + bronze_h - 11.5,
    bronze_y + bronze_h - 15.5,
]
for (x0, y0), y1 in zip(src_arrow_xs, bronze_target_ys):
    arrow(ax, x0, y0, COL2_X, y1,
          color="#795548", lw=1.5,
          connectionstyle="arc3,rad=0.1", zorder=5)

# Bronze → Silver
arrow(ax,
      db_inner_x + db_inner_w / 2, silver_y + silver_h,
      db_inner_x + db_inner_w / 2, silver_y + silver_h + layer_gap * 0.1 + bronze_y - (silver_y + silver_h + layer_gap),
      color=C_BRONZE, lw=2.0,
      connectionstyle="arc3,rad=0.0", zorder=5)
# Simpler: just draw from bottom of bronze box to top of silver box
bx_mid = db_inner_x + db_inner_w / 2
arrow(ax,
      bx_mid, bronze_y,
      bx_mid, silver_y + silver_h,
      color=C_BRONZE, lw=2.2, label="Bronze\n→ Silver",
      connectionstyle="arc3,rad=0.0", zorder=5)

# Silver → Gold
arrow(ax,
      bx_mid, silver_y,
      bx_mid, gold_y + gold_h,
      color=C_SILVER, lw=2.2, label="Silver\n→ Gold",
      connectionstyle="arc3,rad=0.0", zorder=5)

# Gold → Genie (right edge of Databricks to left edge of AI column)
gold_mid_y = gold_y + gold_h / 2
genie_mid_y = genie_y + genie_h / 2
arrow(ax,
      COL2_X + COL2_W, gold_mid_y,
      COL3_X,          genie_mid_y,
      color=C_GOLD, lw=2.2,
      connectionstyle="arc3,rad=0.0", zorder=5)

# Gold → Orchestrator
orch_mid_y = orch_y + orch_h / 2
arrow(ax,
      COL2_X + COL2_W, gold_mid_y - 2,
      COL3_X,           orch_mid_y,
      color=C_GOLD, lw=2.0,
      connectionstyle="arc3,rad=-0.15", zorder=5)

# Genie → cga-analytics (prominent, labeled)
genie_chart_y = analytics_y + analytics_h * 0.7
arrow(ax,
      COL3_X + COL3_W, genie_y + genie_h / 2,
      COL4_X,           genie_chart_y,
      color=C_GENIE, lw=2.8,
      label="generated_query SQL\n→ chart state controller",
      connectionstyle="arc3,rad=-0.1", zorder=6)

# Orchestrator → cga-analytics (prominent, labeled)
orch_app_y = analytics_y + analytics_h * 0.35
arrow(ax,
      COL3_X + COL3_W, orch_y + orch_h / 2,
      COL4_X,           orch_app_y,
      color=C_ORCH, lw=2.8,
      label="orchestrate()\n→ answer + provenance",
      connectionstyle="arc3,rad=0.1", zorder=6)

# Unity AI Gateway ↔ Orchestrator (internal, bidirectional style)
gw_mid_y   = gateway_y + gateway_h / 2
orch_bot_y = orch_y + 2.0
arrow(ax,
      ai_inner_x + ai_inner_w / 2, gateway_y + gateway_h,
      ai_inner_x + ai_inner_w / 2, orch_y,
      color=C_GATEWAY, lw=1.8, label="model\nrouting",
      connectionstyle="arc3,rad=0.0", zorder=5)

# Gold → Unity Catalog (downward within col2)
arrow(ax,
      bx_mid, gold_y,
      bx_mid, unity_y + unity_h,
      color=C_UNITY, lw=2.0, label="governed\nassets",
      connectionstyle="arc3,rad=0.0", zorder=5)

# Sentinela ↑ monitors everything (small upward arrows from sentinela to each column)
for col_mid_x in [COL1_X + COL1_W / 2,
                  COL2_X + COL2_W / 2,
                  COL3_X + COL3_W / 2,
                  COL4_X + COL4_W / 2]:
    arrow(ax,
          col_mid_x, SENT_Y_TOP,
          col_mid_x, MAIN_Y_BOT,
          color=C_SENTINELA, lw=1.2,
          connectionstyle="arc3,rad=0.0", zorder=4)

# ---------------------------------------------------------------------------
# LEGEND  (bottom right)
# ---------------------------------------------------------------------------
leg_x = 88.0
leg_y = 11.0
leg_w = 10.0
leg_h = 22.5

fancy_box(ax, leg_x, leg_y, leg_w, leg_h,
          facecolor="#FAFAFA", edgecolor="#607D8B", linewidth=1.2, radius=0.4, zorder=8)
ax.text(leg_x + leg_w / 2, leg_y + leg_h - 0.7, "LEGEND",
        ha="center", va="center", fontsize=7.5, fontweight="bold",
        color=C_DARK_TEXT, fontfamily="DejaVu Sans", zorder=9)

legend_items = [
    (C_SOURCES,    "External Sources"),
    (C_BRONZE,     "Bronze Layer"),
    (C_SILVER,     "Silver Layer"),
    (C_GOLD,       "Gold Layer"),
    (C_UNITY,      "Unity Catalog"),
    (C_GENIE,      "AI/BI Genie"),
    (C_ORCH,       "Multi-Agent Orch."),
    (C_GATEWAY,    "Unity AI Gateway"),
    (C_APP_ANAL,   "cga-analytics App"),
    (C_APP_ADMIN,  "cga-admin App"),
    (C_SENTINELA,  "Sentinela Ops"),
]
item_h  = (leg_h - 2.2) / len(legend_items)
for i, (color, label) in enumerate(legend_items):
    iy = leg_y + leg_h - 2.0 - i * item_h - item_h / 2
    fancy_box(ax, leg_x + 0.5, iy - 0.35, 1.1, 0.7,
              facecolor=color, edgecolor=color, linewidth=0, radius=0.15, zorder=9)
    ax.text(leg_x + 1.9, iy, label,
            ha="left", va="center",
            fontsize=6.0, color=C_DARK_TEXT,
            fontfamily="DejaVu Sans", zorder=9)

# ---------------------------------------------------------------------------
# VERSION TAG
# ---------------------------------------------------------------------------
ax.text(98.5, 0.4, "v2.0 · 2026-05-02",
        ha="right", va="bottom",
        fontsize=7.0, color="#90A4AE",
        fontfamily="DejaVu Sans", zorder=10)

# ---------------------------------------------------------------------------
# Column header labels (top)
# ---------------------------------------------------------------------------
col_labels = [
    (COL1_X + COL1_W / 2,  "External\nData Sources"),
    (COL2_X + COL2_W / 2,  "Databricks\nData Platform"),
    (COL3_X + COL3_W / 2,  "AI & Serving"),
    (COL4_X + COL4_W / 2,  "Databricks\nApps"),
]
for cx, lbl in col_labels:
    ax.text(cx, MAIN_Y_TOP + 0.4, lbl,
            ha="center", va="bottom",
            fontsize=8.5, fontweight="bold",
            color=C_DARK_TEXT, fontfamily="DejaVu Sans", zorder=10,
            multialignment="center")

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "coingeckoanalytical-architecture.png")
fig.savefig(
    output_path,
    dpi=DPI,
    bbox_inches="tight",
    facecolor=fig.get_facecolor(),
    format="png",
)
plt.close(fig)
print(f"Saved: {output_path}")

#!/usr/bin/env python3
"""Generate DataOps / MLOps / LLMOps maturity map PNG."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# ── palette ──────────────────────────────────────────────────────────────────
BG        = "#0f172a"
GRID      = "#1e293b"
TEXT_MAIN = "#f1f5f9"
TEXT_DIM  = "#64748b"

COLORS = {
    "DataOps":  "#06b6d4",   # cyan
    "MLOps":    "#a78bfa",   # violet
    "LLMOps":   "#f59e0b",   # amber
}

LEVELS = ["L1\nAd-hoc", "L2\nRepeatable", "L3\nDefined", "L4\nManaged", "L5\nOptimised"]

CAPABILITIES = {
    "DataOps": [
        ("Ingestion",        5),
        ("Schema contracts", 5),
        ("Medallion layers", 5),
        ("Observability",    5),
        ("CI / CD deploy",   5),
        ("Unity Catalog",    5),
        ("Data quality",     5),
        ("Cost governance",  5),
    ],
    "MLOps": [
        ("Feature store",    5),
        ("Training pipeline",5),
        ("Model registry",   5),
        ("Batch scoring",    5),
        ("Drift monitoring", 5),
        ("Experiment track.",5),
        ("Model aliases",    5),
        ("Serverless compat",5),
    ],
    "LLMOps": [
        ("Tier routing",     5),
        ("Prompt templates", 5),
        ("Multi-agent orch.",5),
        ("Provenance traces",5),
        ("Token telemetry",  5),
        ("Cost per query",   4),
        ("Input sanitise",   5),
        ("Narrative synth.", 5),
    ],
}

# ── figure layout ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(20, 9))
fig.patch.set_facecolor(BG)

for ax, (domain, caps) in zip(axes, CAPABILITIES.items()):
    ax.set_facecolor(GRID)
    color = COLORS[domain]

    n_caps = len(caps)
    y_positions = np.arange(n_caps)

    # Background level bands
    for lvl in range(1, 6):
        ax.axvline(lvl, color="#334155", linewidth=0.5, zorder=0)
        ax.fill_betweenx([-0.5, n_caps - 0.5], lvl - 1, lvl,
                         color=BG if lvl % 2 == 0 else GRID, alpha=0.3, zorder=0)

    # Bars
    for i, (cap_name, score) in enumerate(caps):
        # Full-length ghost bar
        ax.barh(i, 5, left=0, height=0.6,
                color="#1e293b", edgecolor="#334155", linewidth=0.5, zorder=1)
        # Actual score bar
        ax.barh(i, score, left=0, height=0.6,
                color=color, alpha=0.85, zorder=2)
        # Score label
        ax.text(score + 0.06, i, f"L{score}", va="center", ha="left",
                fontsize=9, color=color, fontweight="bold")

    # Capability labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels([c[0] for c in caps], fontsize=10, color=TEXT_MAIN)
    ax.tick_params(axis="y", length=0)

    # X axis — level labels
    ax.set_xlim(0, 5.6)
    ax.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5])
    ax.set_xticklabels(LEVELS, fontsize=8, color=TEXT_DIM)
    ax.tick_params(axis="x", length=0)

    # Spines
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")

    # Domain header box
    ax.set_title(domain, fontsize=15, fontweight="bold", color=color,
                 pad=14, backgroundcolor=BG)

    # Overall score badge
    avg = np.mean([s for _, s in caps])
    ax.text(5.55, -0.7, f"avg {avg:.1f}", fontsize=8, color=color,
            ha="right", va="bottom", style="italic")

# ── super-title ───────────────────────────────────────────────────────────────
fig.suptitle("CoinGeckoAnalytical — Maturity Map",
             fontsize=18, fontweight="bold", color=TEXT_MAIN, y=0.97)
fig.text(0.5, 0.93, "DataOps · MLOps · LLMOps — all capabilities at Level 5 (Optimised)",
         ha="center", fontsize=11, color="#f59e0b")

# ── legend ────────────────────────────────────────────────────────────────────
legend_patches = [mpatches.Patch(color=c, label=d) for d, c in COLORS.items()]
fig.legend(handles=legend_patches, loc="lower center", ncol=3,
           frameon=False, fontsize=10,
           labelcolor=TEXT_MAIN, bbox_to_anchor=(0.5, 0.01))

plt.tight_layout(rect=[0, 0.06, 1, 0.92])

out = "docs/maturity_map.png"
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
print(f"Saved → {out}")

#!/usr/bin/env python3
"""Generate Figure 1 (HSF CDB data model) for the CHEP2026 paper.

Outputs cdb-datamodel.pdf (vector, for LaTeX) and cdb-datamodel.png (preview).
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# Entity colors follow the presentation slide (blue/green/orange/purple),
# slightly muted for print; auxiliary entities are neutral gray.
MAIN = [
    ("Global Tag", "#3D6FB6", "Consistent, named\nsnapshot of all\nconditions"),
    ("Payload List", "#3E8E5A", "Collection of IOVs for\none data type within\na Global Tag"),
    ("Payload IOV", "#C87A2C", "Conditions record\nwith a validity range\n(start/end)"),
    ("Payload Data", "#7B5EA7", "Actual file stored\non external storage"),
]
AUX = [
    # (title, definition, index of the main box it attaches to)
    ("Global Tag Status", "Edit permissions for a\nGlobal Tag: unlocked,\nlocked, or frozen", 0),
    ("Payload Type", "Category of\nconditions data (e.g.\n“CalorimeterCalib”)", 1),
]
AUX_FC = "#8A9199"

BOX_W, BOX_H = 2.15, 0.62
AUX_W, AUX_H = 2.65, 0.58
GAP = 0.75
Y_MAIN = 1.55
Y_AUX = 3.05

fig, ax = plt.subplots(figsize=(10.4, 3.0))
ax.set_xlim(-0.3, 4 * BOX_W + 3 * GAP + 0.3)
ax.set_ylim(0.45, 3.75)
ax.set_aspect("equal")
ax.axis("off")


def box(x, y, w, h, fc, title, fontsize=15):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec="none"))
    ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
            color="white", fontsize=fontsize, fontweight="bold")


for i, (title, fc, definition) in enumerate(MAIN):
    x = i * (BOX_W + GAP)
    box(x, Y_MAIN, BOX_W, BOX_H, fc, title)
    ax.text(x + BOX_W / 2, Y_MAIN - 0.22, definition, ha="center", va="top",
            color="#3A3F45", fontsize=12.5, linespacing=1.35)
    if i < 3:
        ax.add_patch(FancyArrowPatch((x + BOX_W + 0.10, Y_MAIN + BOX_H / 2),
                                     (x + BOX_W + GAP - 0.10, Y_MAIN + BOX_H / 2),
                                     arrowstyle="-|>", mutation_scale=22,
                                     lw=2.2, color="#6B7280"))

for title, definition, attach in AUX:
    xc = attach * (BOX_W + GAP) + BOX_W / 2
    x = xc - AUX_W / 2
    box(x, Y_AUX, AUX_W, AUX_H, AUX_FC, title, fontsize=13)
    ax.text(xc, Y_AUX + AUX_H + 0.14, definition, ha="center", va="bottom",
            color="#3A3F45", fontsize=12, linespacing=1.35)
    ax.add_patch(FancyArrowPatch((xc, Y_AUX - 0.05), (xc, Y_MAIN + BOX_H + 0.10),
                                 arrowstyle="-|>", mutation_scale=18,
                                 lw=1.8, color="#6B7280"))

fig.tight_layout(pad=0.2)
fig.savefig("cdb-datamodel.pdf")
fig.savefig("cdb-datamodel.png", dpi=200)
print("wrote cdb-datamodel.pdf / cdb-datamodel.png")

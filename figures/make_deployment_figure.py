#!/usr/bin/env python3
"""Generate Figure 2 (HSF CDB deployment architecture) for the CHEP2026 paper.

Outputs cdb-deployment.pdf (vector, for LaTeX) and cdb-deployment.png (preview).
Visual style matches cdb-datamodel (Figure 1). Three-line layout:
line 1: Clients -> Cache, arrow down into the cluster;
line 2: OpenShift cluster row (Route -> Nginx -> Django API -> PgBouncer);
line 3: PostgreSQL write DB, with the two read replicas below it.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

GRAY_TEXT = "#3A3F45"
ARROW = "#6B7280"
BOX_H = 0.62
Y1 = 3.55  # line 1: Clients / Cache (bottom edge)
Y2 = 2.00  # line 2: cluster row
Y3 = 0.35  # line 3: PostgreSQL


def box(ax, x, y, w, h, fc, title, fontsize=18, dashed=False, sub=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=GRAY_TEXT if dashed else "none",
                                ls=(0, (4, 3)) if dashed else "-",
                                lw=1.4 if dashed else 0))
    dy = 0.09 if sub else 0.0
    ax.text(x + w / 2, y + h / 2 + dy, title, ha="center", va="center",
            color="white", fontsize=fontsize, fontweight="bold")
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.17, sub, ha="center", va="center",
                color="white", fontsize=13.5, style="italic")


def arr(ax, p0, p1, mutation=20, lw=2.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>",
                                 mutation_scale=mutation, lw=lw, color=ARROW))


fig, ax = plt.subplots(figsize=(11.0, 5.2))
ax.set_aspect("equal")
ax.axis("off")

# --- line 2: cluster row ------------------------------------------------------
GAP = 0.55
row = [
    ("Route", 1.55, "#B0533A", None),
    ("Nginx", 1.55, "#45657D", None),
    ("Django API", 2.15, "#3D6FB6", None),
    ("PgBouncer", 2.05, "#C87A2C", "(optional)"),
]
x = 2.225  # chosen so that Route sits centered under Cache
xs = []
for title, w, fc, sub in row:
    xs.append((x, w))
    box(ax, x, Y2, w, BOX_H, fc, title, dashed=(title == "PgBouncer"), sub=sub)
    x += w + GAP
row_end = x - GAP

for i in range(len(xs) - 1):
    arr(ax, (xs[i][0] + xs[i][1] + 0.06, Y2 + BOX_H / 2),
        (xs[i + 1][0] - 0.06, Y2 + BOX_H / 2))

route_cx = xs[0][0] + xs[0][1] / 2
pgb_cx = xs[3][0] + xs[3][1] / 2

# cluster boundary
cl_x0 = xs[0][0] - 0.25
cl_x1 = row_end + 0.25
cl_y0 = Y2 - 0.30
cl_y1 = Y2 + BOX_H + 0.52
ax.add_patch(FancyBboxPatch((cl_x0, cl_y0), cl_x1 - cl_x0, cl_y1 - cl_y0,
                            boxstyle="round,pad=0.02,rounding_size=0.10",
                            fc="none", ec="#B0533A", lw=1.6, ls=(0, (5, 3))))
ax.text((cl_x0 + cl_x1) / 2, cl_y1 - 0.06,
        "OpenShift / Kubernetes cluster — Helm chart",
        ha="center", va="top", color="#B0533A", fontsize=15.5, fontweight="bold")

# --- line 1: Clients -> Cache, arrow down into the cluster ---------------------
CLW, CAW = 1.85, 1.70
cache_x = route_cx - CAW / 2
clients_x = cache_x - 0.55 - CLW
box(ax, clients_x, Y1, CLW, BOX_H, "#454B54", "Clients")
box(ax, cache_x, Y1, CAW, BOX_H, "#7B5EA7", "Cache")
arr(ax, (clients_x + CLW + 0.08, Y1 + BOX_H / 2), (cache_x - 0.08, Y1 + BOX_H / 2))
# Cache down to Route (entering the cluster over HTTPS)
arr(ax, (route_cx, Y1 - 0.05), (route_cx, Y2 + BOX_H + 0.08))
ax.text(route_cx + 0.15, Y1 - 0.22, "HTTPS",
        ha="left", va="center", color=GRAY_TEXT, fontsize=14)

# --- line 3: PostgreSQL under PgBouncer, replicas below ------------------------
PGW = 2.25
pg_x = pgb_cx - PGW / 2
box(ax, pg_x, Y3, PGW, BOX_H, "#3E8E5A", "PostgreSQL", sub="write DB")
arr(ax, (pgb_cx, Y2 - 0.05), (pgb_cx, Y3 + BOX_H + 0.08))

rep_w, rep_h, rep_gap = 2.05, 0.55, 0.30
rep_y = Y3 - 0.90
for i in (0, 1):
    rx = pgb_cx - (rep_w + rep_gap / 2) + i * (rep_w + rep_gap)
    box(ax, rx, rep_y, rep_w, rep_h, "#6FAF87", f"Read replica {i + 1}",
        fontsize=14)
    arr(ax, (pgb_cx, Y3 - 0.04), (rx + rep_w / 2, rep_y + rep_h + 0.05),
        mutation=14, lw=1.5)

ax.set_xlim(min(clients_x, cl_x0) - 0.15, max(cl_x1, pgb_cx + rep_w + rep_gap / 2) + 0.15)
ax.set_ylim(rep_y - 0.18, Y1 + BOX_H + 0.15)

fig.tight_layout(pad=0.2)
fig.savefig("cdb-deployment.pdf")
fig.savefig("cdb-deployment.png", dpi=200)
print("wrote cdb-deployment.pdf / cdb-deployment.png")

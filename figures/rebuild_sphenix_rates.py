#!/usr/bin/env python3
"""Rebuild Figure 4 (sPHENIX access rates) from the slide plot images.

Digitizes the bar heights from the original plot rasters (p8_img1.png,
p9_img1.png extracted from the CHEP2026 slides) and re-renders both plots
with large, crisp text. The bar data are taken pixel-exact from the original
plots; only the text/labels are re-rendered.

Outputs cdb-sphenix-rates.pdf (vector) and cdb-sphenix-rates.png (preview).
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

plt.rcParams.update({
    "axes.titlesize": 21,
    "axes.labelsize": 19,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 16,
})


def find_axes_box(a):
    """Locate the plot box (spines) as (left, right, top, bottom) pixels."""
    dark = (a[..., :3] < 120).all(axis=2)
    h, w = dark.shape
    col_runs = dark.sum(axis=0)
    row_runs = dark.sum(axis=1)
    cols = np.where(col_runs > h * 0.5)[0]
    rows = np.where(row_runs > w * 0.5)[0]
    return cols.min(), cols.max(), rows.min(), rows.max()


def tick_positions(a, box, axis):
    """Find tick pixel positions just outside the spine."""
    left, right, top, bottom = box
    dark = (a[..., :3] < 120).all(axis=2)
    if axis == "y":
        strip = dark[:, left - 4]
        pos = np.where(strip)[0]
    else:
        strip = dark[bottom + 4, :]
        pos = np.where(strip)[0]
    # cluster consecutive pixels
    groups, cur = [], [pos[0]]
    for p in pos[1:]:
        if p - cur[-1] <= 2:
            cur.append(p)
        else:
            groups.append(int(np.mean(cur)))
            cur = [p]
    groups.append(int(np.mean(cur)))
    lo, hi = (top - 2, bottom + 2) if axis == "y" else (left - 2, right + 2)
    return [g for g in groups if lo <= g <= hi]


def digitize(path, ytick_vals, exclude=()):
    a = np.asarray(Image.open(path).convert("RGB")).astype(int)
    box = find_axes_box(a)
    left, right, top, bottom = box

    yticks = tick_positions(a, box, "y")          # top -> bottom
    ytv = sorted(ytick_vals, reverse=True)        # match: top = max value
    if len(yticks) != len(ytv):
        raise SystemExit(f"{path}: found {len(yticks)} y ticks, "
                         f"expected {len(ytv)}: {yticks}")
    # linear pixel->value from first/last tick
    p0, p1 = yticks[0], yticks[-1]
    v0, v1 = ytv[0], ytv[-1]

    def val(row):
        return v0 + (row - p0) * (v1 - v0) / (p1 - p0)

    xticks = tick_positions(a, box, "x")

    # steelblue bar mask (matplotlib "steelblue" = #4682B4)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mask = (np.abs(r - 70) < 50) & (np.abs(g - 130) < 50) & (np.abs(b - 180) < 45)
    for x0, x1, y0, y1 in exclude:  # blank out legend boxes etc.
        mask[y0:y1, x0:x1] = False

    cols, vals = [], []
    for c in range(left + 1, right):
        rows = np.where(mask[top:bottom, c])[0]
        if rows.size:
            cols.append(c)
            vals.append(max(0.0, val(top + rows.min())))
    return np.array(cols), np.array(vals), xticks


def draw_panel(ax, cols, vals, xticks, xtick_labels, ytick_vals, title,
               avg, avg_label, peak=None, peak_label=None,
               bar_label="", legend_loc="upper left"):
    ax.bar(cols, vals, width=1.0, color="steelblue", label=bar_label)
    ax.axhline(y=avg, color="red", linestyle="--", linewidth=2, label=avg_label)
    if peak is not None:
        ax.axhline(y=peak, color="orange", linestyle=":", linewidth=2.5,
                   label=peak_label)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels, rotation=30, ha="right")
    ax.set_yticks(ytick_vals)
    ax.set_ylim(0, max(ytick_vals) * 1.12)
    ax.set_xlim(min(cols.min(), xticks[0]) - 15,
                max(cols.max(), xticks[-1]) + 25)
    ax.set_ylabel("Request rate (Hz)")
    ax.set_title(title)
    ax.legend(loc=legend_loc)


def main():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

    # --- panel (a): daily overview (slide 8) ---------------------------------
    cols, vals, xticks = digitize("p8_img1.png", [0, 5, 10, 15, 20, 25],
                                  exclude=[(85, 450, 45, 155)])
    draw_panel(ax1, cols, vals, xticks,
               ["2025-12-01", "2026-01-01", "2026-02-01", "2026-03-01",
                "2026-04-01", "2026-05-01"][:len(xticks)],
               [0, 5, 10, 15, 20, 25],
               "Nginx Access Rate — Daily Overview",
               avg=9.0, avg_label="Overall average (9.0 Hz)",
               bar_label="Daily avg rate", legend_loc="upper left")

    # --- panel (b): peak ±5 min (slide 9) ------------------------------------
    cols, vals, xticks = digitize("p9_img1.png",
                                  [0, 1000, 2000, 3000, 4000, 5000],
                                  exclude=[(1395, 2040, 45, 170)])
    draw_panel(ax2, cols, vals, xticks,
               ["2026-01-28 16:35:00", "2026-01-28 16:40:00",
                "2026-01-28 16:45:00"][:len(xticks)],
               [0, 1000, 2000, 3000, 4000, 5000],
               "Nginx Access Rate — Peak ±5 min (2026-01-28 16:39:37)",
               avg=464.6, avg_label="Window average (464.6 Hz)",
               peak=5006, peak_label="Peak (5006 Hz at 16:39:37)",
               bar_label="Requests per second", legend_loc="upper right")
    ax2.set_xlabel("Time")
    ax1.set_xlabel("Date")

    for ax, tag in ((ax1, "(a)"), (ax2, "(b)")):
        ax.text(-0.06, 1.06, tag, transform=ax.transAxes, fontsize=24,
                fontweight="bold", va="top", ha="left")

    fig.tight_layout(h_pad=3.0)
    fig.savefig("cdb-sphenix-rates.pdf")
    fig.savefig("cdb-sphenix-rates.png", dpi=150)
    print("wrote cdb-sphenix-rates.pdf / cdb-sphenix-rates.png")


if __name__ == "__main__":
    main()

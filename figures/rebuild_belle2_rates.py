#!/usr/bin/env python3
"""Rebuild the Belle II access-rate figure from the slide plot images.

Same approach as rebuild_sphenix_rates.py: digitizes the bar heights from the
original plot rasters (p14_plot.png, p15_plot.png extracted from the CHEP2026
slides, pages 14-15) and re-renders both plots with large, crisp text.

Outputs cdb-belle2-rates.pdf (vector) and cdb-belle2-rates.png (preview).
"""

import matplotlib.pyplot as plt

from rebuild_sphenix_rates import digitize, draw_panel


def main():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

    # --- panel (a): daily overview (slide 14) --------------------------------
    yticks_a = [0, 20, 40, 60, 80, 100, 120]
    cols, vals, xticks = digitize("p14_plot.png", yticks_a,
                                  exclude=[(1600, 2040, 45, 145)])
    draw_panel(ax1, cols, vals, xticks,
               ["2026-01-15", "2026-02-01", "2026-02-15", "2026-03-01",
                "2026-03-15", "2026-04-01", "2026-04-15",
                "2026-05-01"][:len(xticks)],
               yticks_a,
               "Nginx Access Rate — Daily Overview",
               avg=42.8, avg_label="Overall average (42.8 Hz)",
               bar_label="Daily avg rate", legend_loc="upper right")
    ax1.set_xlabel("Date")

    # --- panel (b): typical day (slide 15) ------------------------------------
    yticks_b = [0, 100, 200, 300, 400, 500, 600, 700, 800]
    cols, vals, xticks = digitize("p15_plot.png", yticks_b,
                                  exclude=[(1600, 2040, 45, 135)])
    draw_panel(ax2, cols, vals, xticks,
               [f"2026-03-31 {h:02d}:00:00"
                for h in range(4, 21, 2)][:len(xticks)],
               yticks_b,
               "Nginx Access Rate — Typical Day ±500 min (2026-03-31)",
               avg=54.7, avg_label="Window average (54.7 Hz)",
               bar_label="Requests per second", legend_loc="upper right")
    ax2.set_xlabel("Time")

    for ax, tag in ((ax1, "(a)"), (ax2, "(b)")):
        ax.text(-0.06, 1.06, tag, transform=ax.transAxes, fontsize=24,
                fontweight="bold", va="top", ha="left")

    fig.tight_layout(h_pad=3.0)
    fig.savefig("cdb-belle2-rates.pdf")
    fig.savefig("cdb-belle2-rates.png", dpi=150)
    print("wrote cdb-belle2-rates.pdf / cdb-belle2-rates.png")


if __name__ == "__main__":
    main()

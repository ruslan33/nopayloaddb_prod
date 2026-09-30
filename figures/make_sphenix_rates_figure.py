#!/usr/bin/env python3
"""Generate Figure 4 (sPHENIX conditions access rates) for the CHEP2026 paper.

Usage:
    python3 make_sphenix_rates_figure.py <access.log | access.log.tar.gz>

Parses the nginx access log (plain file, or a .tar.gz archive containing it)
into per-second request counts and recreates the two plots from the CHEP2026
slides — the daily-overview plot of plot_access_rate8.py and the
"Peak ±5 min" plot of plot_access_rate5.py — as one two-panel figure with
paper-sized fonts.

Outputs cdb-sphenix-rates.pdf (vector) and cdb-sphenix-rates.png (preview)
in the current directory.
"""

import io
import sys
import tarfile
from collections import Counter
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

plt.rcParams.update({
    "axes.titlesize": 21,
    "axes.labelsize": 19,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 16,
})


def fast_parse_timestamp(line):
    i = line.find("[")
    if i == -1:
        return None
    s = line[i + 1:]
    try:
        return datetime(int(s[7:11]), MONTHS[s[3:6]], int(s[0:2]),
                        int(s[12:14]), int(s[15:17]), int(s[18:20]))
    except (KeyError, ValueError, IndexError):
        return None


def iter_log_lines(path):
    """Yield lines from a plain log file or from log file(s) inside a tar.gz."""
    if path.endswith((".tar.gz", ".tgz")):
        with tarfile.open(path, "r:gz") as tar:
            for member in tar:
                if not member.isfile():
                    continue
                print(f"Reading {member.name} from archive...")
                f = tar.extractfile(member)
                for line in io.TextIOWrapper(f, errors="replace"):
                    yield line
    else:
        with open(path, errors="replace") as f:
            yield from f


def parse_log(path):
    per_second = Counter()
    n_lines = 0
    for line in iter_log_lines(path):
        n_lines += 1
        if n_lines % 500000 == 0:
            print(f"\r  {n_lines:,} lines...", end="", flush=True)
        ts = fast_parse_timestamp(line)
        if ts:
            per_second[ts] += 1
    print(f"\r  {n_lines:,} lines, {sum(per_second.values()):,} matched")
    return per_second


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    per_second = parse_log(sys.argv[1])
    if not per_second:
        sys.exit("No log entries found.")
    print(f"Time range: {min(per_second)} — {max(per_second)}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

    # --- panel (a): daily average rate (as in plot_access_rate8.py) ----------
    per_day = Counter()
    for ts, n in per_second.items():
        per_day[ts.replace(hour=0, minute=0, second=0)] += n
    days = sorted(per_day)
    daily_hz = [per_day[d] / 86400 for d in days]
    avg_hz = sum(daily_hz) / len(daily_hz)

    ax1.bar(days, daily_hz, width=0.8, color="steelblue", label="Daily avg rate")
    ax1.axhline(y=avg_hz, color="red", linestyle="--", linewidth=2,
                label=f"Overall average ({avg_hz:.1f} Hz)")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax1.set_ylabel("Request rate (Hz)")
    ax1.set_title("Nginx Access Rate — Daily Overview")
    ax1.legend(loc="upper left")
    ax1.tick_params(axis="x", rotation=30)
    for lbl in ax1.get_xticklabels():
        lbl.set_ha("right")

    # --- panel (b): peak ±5 min (as in plot_access_rate5.py) -----------------
    peak_ts = max(per_second, key=per_second.get)
    peak_hz = per_second[peak_ts]
    print(f"Peak: {peak_hz} req/s at {peak_ts}")

    window = timedelta(minutes=5)
    zoom_times = sorted(ts for ts in per_second
                        if peak_ts - window <= ts <= peak_ts + window)
    zoom_hz = [per_second[t] for t in zoom_times]
    zoom_avg = sum(zoom_hz) / len(zoom_hz)

    ax2.bar(zoom_times, zoom_hz, width=0.8 / 86400, color="steelblue",
            label="Requests per second")
    ax2.axhline(y=zoom_avg, color="red", linestyle="--", linewidth=2,
                label=f"Window average ({zoom_avg:.1f} Hz)")
    ax2.axhline(y=peak_hz, color="orange", linestyle=":", linewidth=2,
                label=f"Peak ({peak_hz} Hz at {peak_ts.strftime('%H:%M:%S')})")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Request rate (Hz)")
    ax2.set_title(f"Nginx Access Rate — Peak ±5 min "
                  f"({peak_ts.strftime('%Y-%m-%d %H:%M:%S')})")
    ax2.legend(loc="upper right")
    ax2.tick_params(axis="x", rotation=30)
    for lbl in ax2.get_xticklabels():
        lbl.set_ha("right")

    # panel tags
    for ax, tag in ((ax1, "(a)"), (ax2, "(b)")):
        ax.text(-0.06, 1.06, tag, transform=ax.transAxes, fontsize=24,
                fontweight="bold", va="top", ha="left")

    fig.tight_layout(h_pad=3.0)
    fig.savefig("cdb-sphenix-rates.pdf")
    fig.savefig("cdb-sphenix-rates.png", dpi=150)
    print("wrote cdb-sphenix-rates.pdf / cdb-sphenix-rates.png")


if __name__ == "__main__":
    main()

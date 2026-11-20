"""
Azimuth-vs-altitude tracks for the two constellations (3 figures).

Needs:  pip3 install pandas matplotlib
Input (same folder):  stellarium_constellations_2026_wide.csv
        columns used: Date, Betelgeuse_Az_deg, Betelgeuse_Alt_deg, Dubhe_Az_deg, Dubhe_Alt_deg
Output: fig3_orion_azalt.png, fig4_ursamajor_azalt.png, fig5_both_azalt.png
Run:    python3 make_azalt_plots.py
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")                       # draw to files, no window needed
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

CSV = "stellarium_constellations_2026_wide.csv"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ---- load: one row per day of 2026; fill a missing day by interpolation ----
w = pd.read_csv(CSV, parse_dates=["Date"]).set_index("Date")
w = w.reindex(pd.date_range("2026-01-01", "2026-12-31"))
w = w.interpolate(limit_area="inside")


def track(ax, star, marker, signed=False):
    """Plot one star's azimuth (x) against altitude (y), coloured by month."""
    az = w[f"{star}_Az_deg"].copy()
    alt = w[f"{star}_Alt_deg"].copy()
    if signed:                                   # degrees east(+)/west(-) of north,
        az = ((az + 180) % 360) - 180            # so a track around north is not cut at 0/360
    line = az.copy()
    line[az.diff().abs() > 180] = np.nan         # don't draw a line across the 0/360 wrap
    ax.plot(line, alt, color="grey", lw=0.6, alpha=0.6, zorder=1)
    sc = ax.scatter(az, alt, c=w.index.month, cmap="turbo", vmin=1, vmax=12,
                    s=16, marker=marker, zorder=2)
    return az, alt, sc


def mark_dates(ax, az, alt, dates):
    """Black dots + labels on chosen dates, e.g. [(1, '1 Jan'), (4, '1 Apr')]."""
    for month, label in dates:
        d = pd.Timestamp(f"2026-{month:02d}-01")
        ax.plot(az[d], alt[d], "ko", ms=4, zorder=3)
        ax.annotate(label, (az[d], alt[d]), fontsize=8, xytext=(6, 6),
                    textcoords="offset points",
                    arrowprops=dict(arrowstyle="-", color="k", lw=0.5))


def month_colorbar(fig, ax, sc):
    cb = fig.colorbar(sc, ax=ax, ticks=range(1, 13), shrink=0.8, pad=0.02)
    cb.ax.set_yticklabels(MONTHS)
    cb.set_label("Month")


def horizon(ax, lowest):
    ax.axhline(0, color="k", lw=1)               # the horizon
    ax.axhspan(lowest, 0, color="k", alpha=0.07)  # shaded = below the horizon


QUARTERS = [(1, "1 Jan"), (4, "1 Apr"), (7, "1 Jul"), (10, "1 Oct")]

# ---------------- Figure 3: Orion (Betelgeuse) ----------------
fig, ax = plt.subplots(figsize=(9, 6))
az, alt, sc = track(ax, "Betelgeuse", "o")
mark_dates(ax, az, alt, QUARTERS)
horizon(ax, -60)
ax.set_xlim(0, 360); ax.set_ylim(-60, 75); ax.set_xticks(range(0, 361, 45))
ax.text(5, -8, "below horizon (not visible)", fontsize=8)
ax.set_xlabel("Azimuth (deg, N=0, E=90, S=180, W=270)")
ax.set_ylabel("Altitude (deg)")
ax.set_title("Orion (Betelgeuse): azimuth and altitude at 21:00 IST, every day of 2026", fontsize=10)
ax.grid(alpha=0.3)
month_colorbar(fig, ax, sc)
fig.tight_layout(); fig.savefig("fig3_orion_azalt.png", dpi=170); plt.close(fig)

# ---------------- Figure 4: Ursa Major (Dubhe) ----------------
fig, ax = plt.subplots(figsize=(9, 6))
az, alt, sc = track(ax, "Dubhe", "^", signed=True)
mark_dates(ax, az, alt, QUARTERS)
horizon(ax, -2)
ax.set_xlim(-40, 40); ax.set_ylim(-2, 62)
ticks = [-40, -30, -20, -10, 0, 10, 20, 30, 40]
ax.set_xticks(ticks); ax.set_xticklabels([f"{t % 360}\u00b0" for t in ticks])
ax.set_xlabel("Azimuth (deg; 0 = due north, 330 = 30\u00b0 west of north, 30 = 30\u00b0 east of north)")
ax.set_ylabel("Altitude (deg)")
ax.set_title("Ursa Major (Dubhe): azimuth and altitude at 21:00 IST, every day of 2026", fontsize=10)
ax.grid(alpha=0.3)
month_colorbar(fig, ax, sc)
fig.tight_layout(); fig.savefig("fig4_ursamajor_azalt.png", dpi=170); plt.close(fig)

# ---------------- Figure 5: both on one plot ----------------
fig, ax = plt.subplots(figsize=(10, 6))
for star, marker, name in [("Betelgeuse", "o", "Orion"), ("Dubhe", "^", "Ursa Major")]:
    az, alt, sc = track(ax, star, marker)        # normal 0-360 azimuth here
    d = pd.Timestamp("2026-01-01")
    ax.plot(az[d], alt[d], "ko", ms=4, zorder=3)
    ax.annotate(f"{name}, 1 Jan", (az[d], alt[d]), fontsize=8, xytext=(8, 8),
                textcoords="offset points",
                arrowprops=dict(arrowstyle="-", color="k", lw=0.5))
horizon(ax, -60)
ax.set_xlim(0, 360); ax.set_ylim(-60, 75); ax.set_xticks(range(0, 361, 45))
ax.text(5, -8, "below horizon (not visible)", fontsize=8)
ax.set_xlabel("Azimuth (deg, N=0, E=90, S=180, W=270)")
ax.set_ylabel("Altitude (deg)")
ax.set_title("Both constellations: azimuth and altitude at 21:00 IST, every day of 2026\n"
             "(circle = Orion/Betelgeuse, triangle = Ursa Major/Dubhe)", fontsize=10)
ax.grid(alpha=0.3)
ax.legend(handles=[Line2D([], [], marker="o", ls="", color="grey", label="Orion (Betelgeuse)"),
                   Line2D([], [], marker="^", ls="", color="grey", label="Ursa Major (Dubhe)")],
          loc="lower right")
month_colorbar(fig, ax, sc)
fig.tight_layout(); fig.savefig("fig5_both_azalt.png", dpi=170); plt.close(fig)

print("Saved fig3_orion_azalt.png, fig4_ursamajor_azalt.png, fig5_both_azalt.png")

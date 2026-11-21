"""
Azimuth-vs-altitude yearly tracks for ANY stars you have collected.
Makes one figure per star plus one combined figure.

Needs:  pip3 install pandas matplotlib
Input:  a "wide" CSV from the scraper, one row per date, with columns named
        <StarName>_Az_deg and <StarName>_Alt_deg   (e.g. Antares_Az_deg, Antares_Alt_deg)
Run:    python3 azalt_plots_any_star.py

TO USE DIFFERENT STARS: edit only the SETTINGS block below.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ======================= SETTINGS (edit these) =======================
CSV = "stellarium_constellations_2026_wide.csv"
STARS = {                      # column prefix in the CSV : name shown on the plots
    "Betelgeuse": "Orion (Betelgeuse)",
    "Dubhe": "Ursa Major (Dubhe)",
}
OBS_TIME = "21:00 IST"         # only used in the plot titles
# =====================================================================

MARKERS = ["o", "^", "s", "D", "v", "P", "X", "*"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

w = pd.read_csv(CSV, parse_dates=["Date"]).set_index("Date")
year = w.index[0].year
w = w.reindex(pd.date_range(f"{year}-01-01", f"{year}-12-31")).interpolate(limit_area="inside")


def safe(name):
    return "".join(ch if ch.isalnum() else "_" for ch in name)


def prepare(star):
    """Return azimuth to plot, altitude, and how the azimuth axis should be drawn."""
    az, alt = w[f"{star}_Az_deg"], w[f"{star}_Alt_deg"]
    wraps = (az.diff().abs() > 180).any()                # track crosses north (0/360)
    signed = ((az + 180) % 360) - 180                    # degrees east (+) / west (-) of north
    if wraps and (signed.max() - signed.min()) < 270:    # a loop around north (circumpolar-type)
        return signed, alt, "signed"
    return az, alt, "full"


def draw_track(ax, az, alt, marker):
    line = az.copy()
    line[az.diff().abs() > 180] = np.nan                 # no line across the 0/360 wrap
    ax.plot(line, alt, color="grey", lw=0.6, alpha=0.6, zorder=1)
    return ax.scatter(az, alt, c=w.index.month, cmap="turbo", vmin=1, vmax=12,
                      s=16, marker=marker, zorder=2)


def mark_dates(ax, az, alt, months=(1, 4, 7, 10), prefix=""):
    for m in months:
        d = pd.Timestamp(f"{year}-{m:02d}-01")
        ax.plot(az[d], alt[d], "ko", ms=4, zorder=3)
        ax.annotate(f"{prefix}1 {MONTHS[m-1]}", (az[d], alt[d]), fontsize=8, xytext=(6, 6),
                    textcoords="offset points", arrowprops=dict(arrowstyle="-", color="k", lw=0.5))


def finish(fig, ax, sc, ylo, yhi):
    ax.axhline(0, color="k", lw=1)
    ax.axhspan(ylo, 0, color="k", alpha=0.07)
    ax.set_ylim(ylo, yhi)
    ax.set_ylabel("Altitude (deg)")
    ax.grid(alpha=0.3)
    cb = fig.colorbar(sc, ax=ax, ticks=range(1, 13), shrink=0.8, pad=0.02)
    cb.ax.set_yticklabels(MONTHS)
    cb.set_label("Month")
    fig.tight_layout()


# ---------------- one figure per star ----------------
for star, label in STARS.items():
    az, alt, mode = prepare(star)
    fig, ax = plt.subplots(figsize=(9, 6))
    sc = draw_track(ax, az, alt, "o")
    mark_dates(ax, az, alt)
    if mode == "signed":
        lo, hi = np.floor((az.min() - 8) / 10) * 10, np.ceil((az.max() + 8) / 10) * 10
        ax.set_xlim(lo, hi)
        ticks = np.arange(lo, hi + 1, 10)
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{int(t) % 360}\u00b0" for t in ticks])
        ax.set_xlabel("Azimuth (deg; 0 = due north, 330 = 30\u00b0 west of north, 30 = 30\u00b0 east of north)")
    else:
        if (w[f"{star}_Az_deg"].diff().abs() > 180).any():
            lo, hi = 0, 360
        else:
            lo = np.floor((az.min() - 10) / 10) * 10
            hi = np.ceil((az.max() + 10) / 10) * 10
        ax.set_xlim(lo, hi)
        ax.set_xticks(np.arange(np.ceil(lo / 45) * 45, hi + 1, 45))
        ax.set_xlabel("Azimuth (deg, N=0, E=90, S=180, W=270)")
    ylo, yhi = min(alt.min() - 6, -3), alt.max() + 8
    ax.set_title(f"{label}: azimuth and altitude at {OBS_TIME}, every day of {year}", fontsize=10)
    finish(fig, ax, sc, ylo, yhi)
    if ylo < -10:
        ax.text(lo + 0.01 * (hi - lo), -8, "below horizon (not visible)", fontsize=8)
    fig.savefig(f"azalt_{safe(star)}.png", dpi=170)
    plt.close(fig)

# ---------------- combined figure ----------------
fig, ax = plt.subplots(figsize=(10, 6))
handles, all_alt = [], []
for i, (star, label) in enumerate(STARS.items()):
    az, alt = w[f"{star}_Az_deg"], w[f"{star}_Alt_deg"]    # normal 0-360 azimuth for all
    mk = MARKERS[i % len(MARKERS)]
    sc = draw_track(ax, az, alt, mk)
    d = pd.Timestamp(f"{year}-01-01")
    ax.plot(az[d], alt[d], "ko", ms=4, zorder=3)
    ax.annotate(f"{label.split(' (')[0]}, 1 Jan", (az[d], alt[d]), fontsize=8, xytext=(8, 8),
                textcoords="offset points", arrowprops=dict(arrowstyle="-", color="k", lw=0.5))
    handles.append(Line2D([], [], marker=mk, ls="", color="grey", label=label))
    all_alt.append(alt)
alt_all = pd.concat(all_alt)
ax.set_xlim(0, 360)
ax.set_xticks(range(0, 361, 45))
ax.set_xlabel("Azimuth (deg, N=0, E=90, S=180, W=270)")
ax.set_title(f"All stars: azimuth and altitude at {OBS_TIME}, every day of {year}", fontsize=10)
ax.legend(handles=handles, loc="lower right")
finish(fig, ax, sc, min(alt_all.min() - 6, -3), alt_all.max() + 8)
fig.savefig("azalt_all.png", dpi=170)
plt.close(fig)

print("Saved:", ", ".join([f"azalt_{safe(s)}.png" for s in STARS] + ["azalt_all.png"]))

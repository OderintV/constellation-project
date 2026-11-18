import re, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as mdates

import os, glob
# Run this script from the folder that holds your two data files.
def find(*names):
    for n in names:
        if os.path.exists(n):
            return n
    raise SystemExit(f"Could not find any of {names} in {os.getcwd()}")
LAT = 28.9948
c = pd.read_csv(find("stellarium_constellations_2026.csv", "stellarium_constellations_2026_1.csv"), parse_dates=["Date"])
s = pd.read_csv(find("stellarium_sun_2026.csv"), parse_dates=["Date"])

# --- tidy: one row per date -------------------------------------------------
w = c.pivot(index="Date", columns="Object", values=["Az_deg", "Alt_deg"])
w.columns = [f"{b}_{a}" for a, b in w.columns]
w = w.reindex(pd.date_range("2026-01-01", "2026-12-31"))
w.index.name = "Date"
w["Dubhe_filled"] = w["Dubhe_Az_deg"].isna()          # flag any gap
w = w.interpolate(limit_area="inside")                # fill 1-day gap (20 Jun)
sun = s.set_index("Date")[["Az_deg", "Alt_deg", "RA_Dec_shown"]]

def hms(txt):                                          # '18h 47m10.5s   -22°59'49.3"'
    m = re.match(r"(\d+)h\s*(\d+)m([\d.]+)s\s+([+\-−])(\d+)°(\d+)'([\d.]+)", txt)
    ra = (int(m[1]) + int(m[2]) / 60 + float(m[3]) / 3600) * 15
    dec = (int(m[5]) + int(m[6]) / 60 + float(m[7]) / 3600) * (-1 if m[4] in "-−" else 1)
    return ra, dec
sun[["RA", "Dec"]] = [hms(t) for t in sun.RA_Dec_shown]

seasons = {"Mar equinox": "2026-03-20", "Jun solstice": "2026-06-21",
           "Sep equinox": "2026-09-23", "Dec solstice": "2026-12-21"}
mark = {k: pd.Timestamp(v) for k, v in seasons.items()}
star = {"Betelgeuse": ("Orion", "tab:red"), "Dubhe": ("Ursa Major", "tab:blue")}
months = mdates.MonthLocator(); fmt = mdates.DateFormatter("%b")

def season_lines(ax):
    for k, d in mark.items():
        ax.axvline(d, color="grey", ls=":", lw=.9)
        ax.text(d, ax.get_ylim()[1], " " + k, rotation=90, va="top", ha="right", fontsize=7, color="grey")

# ---- Fig 1: altitude vs date -------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.8))
for o, (con, col) in star.items():
    ax.plot(w.index, w[f"{o}_Alt_deg"], color=col, lw=2, label=f"{con} ({o})")
ax.axhline(0, color="k", lw=1); ax.fill_between(w.index, -60, 0, color="k", alpha=.07)
ax.text(w.index[3], -8, "below horizon (not visible)", fontsize=8)
ax.set_ylim(-60, 75); ax.set_ylabel("Altitude (deg)"); ax.set_title("Altitude at 21:00 IST, Sonipat, 2026")
ax.xaxis.set_major_locator(months); ax.xaxis.set_major_formatter(fmt); ax.legend(loc="lower left"); ax.grid(alpha=.3)
season_lines(ax); fig.tight_layout(); fig.savefig("fig1_altitude.png", dpi=170); plt.close()

# ---- Fig 2: azimuth vs date --------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.8))
for o, (con, col) in star.items():
    az = w[f"{o}_Az_deg"].copy()
    if o == "Betelgeuse": az[w["Betelgeuse_Alt_deg"] < 0] = np.nan   # only while above horizon
    ax.plot(w.index, az, color=col, lw=2, label=f"{con} ({o})" + (" - above horizon only" if o == "Betelgeuse" else ""))
ax.set_ylim(0, 360); ax.set_yticks(range(0, 361, 45)); ax.set_ylabel("Azimuth (deg, N=0, E=90, S=180, W=270)")
ax.set_title("Azimuth at 21:00 IST, Sonipat, 2026")
ax.xaxis.set_major_locator(months); ax.xaxis.set_major_formatter(fmt); ax.legend(loc="center left"); ax.grid(alpha=.3)
season_lines(ax); fig.tight_layout(); fig.savefig("fig2_azimuth.png", dpi=170); plt.close()

# ---- Fig 3: sky path (polar) -------------------------------------------------
fig = plt.figure(figsize=(7.4, 7.4)); ax = fig.add_subplot(111, projection="polar")
ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
for o, (con, col) in star.items():
    up = w[f"{o}_Alt_deg"] > 0
    sc = ax.scatter(np.radians(w.loc[up, f"{o}_Az_deg"]), 90 - w.loc[up, f"{o}_Alt_deg"],
                    c=w.index[up].month, cmap="twilight", s=14, marker="o" if o == "Betelgeuse" else "^", label=con)
ax.set_rlim(0, 90); ax.set_yticks([0, 30, 60, 90]); ax.set_yticklabels(["90", "60", "30", "0 (horizon)"], fontsize=7)
ax.set_title("Where each star sits in the sky at 21:00 (centre = overhead)\ncircle = Orion/Betelgeuse, triangle = Ursa Major/Dubhe; colour = month", fontsize=9)
cb = fig.colorbar(sc, ax=ax, pad=.1, shrink=.7); cb.set_label("Month"); ax.legend(loc="lower left", bbox_to_anchor=(-.05, -.08))
fig.tight_layout(); fig.savefig("fig3_sky_path.png", dpi=170); plt.close()

# ---- Fig 4: Sun altitude / azimuth / declination -----------------------------
fig, axs = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
axs[0].plot(sun.index, sun.Alt_deg, color="darkorange", lw=2); axs[0].set_ylabel("Altitude (deg)")
axs[0].set_title("Sun at 12:00 IST, Sonipat, 2026")
axs[1].plot(sun.index, sun.Az_deg, color="goldenrod", lw=2); axs[1].set_ylabel("Azimuth (deg)")
axs[2].plot(sun.index, sun.Dec, color="firebrick", lw=2); axs[2].axhline(0, color="k", lw=.8)
axs[2].set_ylabel("Declination (deg)")
for a in axs:
    a.grid(alpha=.3)
    for d in mark.values(): a.axvline(d, color="grey", ls=":", lw=.9)
axs[2].xaxis.set_major_locator(months); axs[2].xaxis.set_major_formatter(fmt)
fig.tight_layout(); fig.savefig("fig4_sun_year.png", dpi=170); plt.close()

# ---- Fig 5: analemma (az/alt) ------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 8))
sc = ax.scatter(sun.Az_deg, sun.Alt_deg, c=sun.index.dayofyear, cmap="viridis", s=14)
ax.plot(sun.Az_deg, sun.Alt_deg, color="grey", lw=.5, alpha=.5)
for k, d in mark.items():
    r = sun.loc[d]; ax.annotate(f"{k}\n{d:%d %b}", (r.Az_deg, r.Alt_deg), fontsize=8,
                                xytext=(8, 6), textcoords="offset points", arrowprops=dict(arrowstyle="-", color="k", lw=.5))
    ax.plot(r.Az_deg, r.Alt_deg, "ko", ms=5)
ax.set_xlabel("Azimuth (deg)"); ax.set_ylabel("Altitude (deg)"); ax.grid(alpha=.3)
ax.set_title("Analemma: the Sun at 12:00 IST every day of 2026\n(azimuth vs altitude, Sonipat)", fontsize=10)
fig.colorbar(sc, label="Day of year", shrink=.8); fig.tight_layout(); fig.savefig("fig5_analemma_altaz.png", dpi=170); plt.close()

# ---- Fig 6: analemma in the textbook form (equation of time vs declination) ---
T = (pd.DatetimeIndex(sun.index) + pd.Timedelta(hours=12 - 5.5) - pd.Timestamp("2000-01-01 12:00")) / pd.Timedelta(days=36525)
L0 = (280.46646 + 36000.76983 * np.asarray(T)) % 360
eot = ((L0 - 0.00569 - sun.RA.values + 180) % 360 - 180) * 4         # minutes of time
sun["EoT_min"] = eot
fig, ax = plt.subplots(figsize=(6.2, 8))
sc = ax.scatter(eot, sun.Dec, c=sun.index.dayofyear, cmap="viridis", s=14); ax.plot(eot, sun.Dec, color="grey", lw=.5, alpha=.5)
for k, d in mark.items():
    ax.annotate(k, (sun.loc[d, "EoT_min"], sun.loc[d, "Dec"]), fontsize=8, xytext=(8, 4), textcoords="offset points")
ax.axhline(0, color="k", lw=.6); ax.axvline(0, color="k", lw=.6)
ax.set_xlabel("Equation of time (minutes): sundial minus clock"); ax.set_ylabel("Solar declination (deg)")
ax.set_title("Analemma from Stellarium's RA/Dec of the Sun", fontsize=10); ax.grid(alpha=.3)
fig.colorbar(sc, label="Day of year", shrink=.8); fig.tight_layout(); fig.savefig("fig6_analemma_eot_dec.png", dpi=170); plt.close()

# ===== numbers ================================================================
out = {}
mnames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
rows = []
for o, (con, _) in star.items():
    a = w[f"{o}_Alt_deg"]
    for m in range(1, 13):
        x = a[a.index.month == m]
        rows.append(dict(Constellation=con, Star=o, Month=mnames[m-1], Days=len(x),
                         Days_above_0=int((x > 0).sum()), Days_above_10=int((x > 10).sum()),
                         Min_alt=round(x.min(), 1), Mean_alt=round(x.mean(), 1), Max_alt=round(x.max(), 1)))
vis = pd.DataFrame(rows)

# hour angle drift (verifies ~0.9856 deg/day)
def hour_angle(az, alt, dec):
    az, alt, dec, p = map(np.radians, (az, alt, dec, LAT))
    sH = -np.sin(az) * np.cos(alt); cH = (np.sin(alt) - np.sin(p) * np.sin(dec)) * 1.0
    cH = (np.sin(alt) * np.cos(p) - np.cos(alt) * np.sin(p) * np.cos(az))
    return np.degrees(np.arctan2(sH, cH))
decB, decD = 7.4114, 61.605
HB = np.unwrap(np.radians(hour_angle(w.Betelgeuse_Az_deg, w.Betelgeuse_Alt_deg, decB)))
HD = np.unwrap(np.radians(hour_angle(w.Dubhe_Az_deg, w.Dubhe_Alt_deg, decD)))
drift = {"Betelgeuse": np.degrees(np.diff(HB)).mean(), "Dubhe": np.degrees(np.diff(HD)).mean()}

summary = dict(
    Bet_first_below=str(w.index[(w.Betelgeuse_Alt_deg < 0)].min().date()),
    Bet_last_below=str(w.index[(w.Betelgeuse_Alt_deg < 0)].max().date()),
    Bet_days_up=int((w.Betelgeuse_Alt_deg > 0).sum()),
    Bet_max=(round(w.Betelgeuse_Alt_deg.max(), 2), str(w.Betelgeuse_Alt_deg.idxmax().date())),
    Bet_min=(round(w.Betelgeuse_Alt_deg.min(), 2), str(w.Betelgeuse_Alt_deg.idxmin().date())),
    Dub_max=(round(w.Dubhe_Alt_deg.max(), 2), str(w.Dubhe_Alt_deg.idxmax().date())),
    Dub_min=(round(w.Dubhe_Alt_deg.min(), 2), str(w.Dubhe_Alt_deg.idxmin().date())),
    Dub_days_gt10=int((w.Dubhe_Alt_deg > 10).sum()),
    Bet_days_gt10=int((w.Betelgeuse_Alt_deg > 10).sum()),
    Sun_max=(round(sun.Alt_deg.max(), 2), str(sun.Alt_deg.idxmax().date())),
    Sun_min=(round(sun.Alt_deg.min(), 2), str(sun.Alt_deg.idxmin().date())),
    Dec_max=round(sun.Dec.max(), 3), Dec_min=round(sun.Dec.min(), 3),
    EoT_max=(round(sun.EoT_min.max(), 1), str(sun.EoT_min.idxmax().date())),
    EoT_min=(round(sun.EoT_min.min(), 1), str(sun.EoT_min.idxmin().date())),
    Sun_az_range=(round(sun.Az_deg.min(), 1), round(sun.Az_deg.max(), 1)),
    drift=drift, dubhe_filled=list(map(str, w.index[w.Dubhe_filled].date)),
    daily_az_bet=round(w.Betelgeuse_Az_deg.diff().abs()[w.Betelgeuse_Alt_deg > 0].median(), 3),
    daily_az_dub=round(w.Dubhe_Az_deg.diff().abs().median(), 3),
    eq_alts={k: round(sun.loc[d, "Alt_deg"], 2) for k, d in mark.items()},
    eq_dec={k: round(sun.loc[d, "Dec"], 3) for k, d in mark.items()},
)
for k, v in summary.items(): print(k, v)
print(vis.pivot(index="Month", columns="Star", values=["Days_above_0", "Days_above_10", "Mean_alt"]).reindex(mnames).to_string())
vis.to_csv("monthly_visibility_2026.csv", index=False)
with pd.ExcelWriter("analysis_tables_2026.xlsx") as xw:
    vis.to_excel(xw, sheet_name="Monthly visibility", index=False)
    w.reset_index().round(5).to_excel(xw, sheet_name="Stars daily (clean)", index=False)
    sun.reset_index().drop(columns=["RA_Dec_shown"]).round(5).to_excel(xw, sheet_name="Sun daily (clean)", index=False)

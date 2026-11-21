# Constellations and the Sun through the year

The project records the **azimuth and altitude** of two reference stars (Betelgeuse in Orion, Dubhe in Ursa Major) every day of 2026 at 21:00 IST, and of the **Sun** every day at 12:00 IST, from **Sonipat, Haryana (28.9948° N, 77.0151° E)**. The readings are taken from [Stellarium Web](https://stellarium-web.org) by a script that automates the page. A second set of scripts turns the readings into graphs, tables and a written report.

Author: Vihaan Jakhetiya

This is for a Principle of Science (POS) course offered in Monsoon 2026 at Ashoka University by Prof. Somak Raychaudhury & Shraddha Karve. 


## 1. What is in this folder

| File | What it is |
|---|---|
| `stellarium_constellations.py` | **Scraper.** Collects Az/Alt for the stars listed in `OBJECTS` at 21:00 IST. |
| `stellarium_sun.py` | **Scraper.** Same program, set up for the Sun at 12:00 IST. |
| `stellarium_constellations_2026.csv` | Raw readings for the stars, one row per reading (730 rows). |
| `stellarium_constellations_2026_wide.csv` | Same Az/Alt values, one row per date, one column per star. |
| `stellarium_sun_2026.csv` | Raw readings for the Sun (365 rows). |
| `stellarium_sun_2026_wide.csv` | Same values, one row per date. |
| `analysis.py` | Makes all the report figures and tables from the two raw CSVs. |
| `analysis_tables_2026.xlsx`, `monthly_visibility_2026.csv` | Tables made by `analysis.py`. |
| `azalt_plots_any_star.py` | **General** azimuth-vs-altitude plots for any stars (one figure per star plus a combined one). |
| `make_azalt_plots.py` | The same plots, fixed to Betelgeuse and Dubhe only (older, simpler version). |
| `Constellations_and_Sun_Report.docx` | The written report with figures and tables. |
| `Graphs/` | Output figures. |
| `stellarium_scraper.py`, `stellarium_constellations_old.py` | **Old versions** of the scraper, kept for reference. They are replaced by the two scrapers above and can be deleted or moved to an `old/` folder. |

---

## 2. Requirements

- Python 3.9 or newer
- Google Chrome (the scraper controls it)
- An internet connection
- Python packages:

```
pip3 install selenium pandas matplotlib openpyxl
```

Selenium downloads the Chrome driver automatically. You do not need to install it.

---

## 3. Quick start: getting your own data

### Step 1 - test the scraper on one date

```
python3 stellarium_constellations.py test
```

Chrome opens, loads Stellarium for 10 January 2026, searches for each star and prints something like:

```
2026-01-10 Betelgeuse  Az=122°04'35.2" (122.07644)  Alt=+54°52'04.9" (54.86803)  RA/Dec: 05h 56m36.6s +07°24'41.4"  [21:00:00]
```

Check that the **page clock** (the last value in brackets) is close to the time you asked for. If the test works, go on. If not, see section 7.

### Step 2 - run the full year

```
python3 stellarium_constellations.py     # the stars, 21:00 IST
python3 stellarium_sun.py                # the Sun, 12:00 IST
```

- Run **one script at a time** and leave the Chrome window visible. Do not minimise it, cover it, or use it for other things.
- Keep the computer awake and plugged in. On a Mac: `caffeinate -i python3 stellarium_constellations.py`.
- Each script takes roughly 1 hour, because it loads a fresh page for every reading and pauses a few seconds between loads.
- **It saves after every day.** Stop it with `Ctrl + C` at any time and run the same command again: it skips the dates it has already done. Dates that failed are not saved, so rerunning the script fills any gaps.
- When a script finishes, it writes the `_wide.csv` file. That file does not exist until the whole year is done.

### Step 3 - make the figures and tables

Put `analysis.py` in the same folder as `stellarium_constellations_2026.csv` and `stellarium_sun_2026.csv`, then run:

```
python3 analysis.py
```

It produces:

| Output | Content |
|---|---|
| `fig1_altitude.png`, `fig2_azimuth.png` | Altitude and azimuth of both stars through the year |
| `fig3_orion_azalt.png`, `fig4_ursamajor_azalt.png`, `fig5_both_azalt.png` | Azimuth-vs-altitude track of each star, and of both together |
| `fig6_sky_path.png` | Polar sky chart of both stars (centre = overhead, edge = horizon) |
| `fig7_sun_year.png` | Sun altitude, azimuth and declination through the year |
| `fig8_analemma_altaz.png`, `fig9_analemma_eot_dec.png` | The analemma, as azimuth vs altitude and as equation of time vs declination |
| `analysis_tables_2026.xlsx`, `monthly_visibility_2026.csv` | Monthly visibility table and cleaned daily data |

The key numbers (when each star is above the horizon, maximum and minimum altitudes, Earth's axial tilt measured from the Sun's declination, and so on) are printed in the terminal.

---

## 4. Using a different constellation (or object)

**To collect data for other stars**, open `stellarium_constellations.py` and change one line near the top:

```python
OBJECTS = ['Betelgeuse', 'Dubhe']
```

- Use the name of a **star**, not the constellation. A constellation covers an area, and its "centre" in Stellarium moves between sessions, so it is not a fixed point. Pick a bright star in your constellation (for Scorpius, `'Antares'`).
- The name must work when typed into Stellarium Web's search box. The script picks the first suggestion.
- If you want a separate dataset, also change `OUT = "stellarium_constellations_2026.csv"` to a new filename. Otherwise the new stars are added to the existing file.

**To plot the new stars**, open `azalt_plots_any_star.py` and edit only the settings block at the top:

```python
CSV = "stellarium_constellations_2026_wide.csv"
STARS = {
    "Antares": "Scorpius (Antares)",
    "Vega": "Lyra (Vega)",
}
```

The name on the left must match the object name used in the scraper (the wide CSV has columns like `Antares_Az_deg`). The name on the right is the label shown on the plots. Run `python3 azalt_plots_any_star.py`. It chooses its own axis ranges, and it draws a star that circles the north pole as a loop around north.

**Not general:** `analysis.py` (including its visibility table, hour-angle calculation and report figures) is written for Betelgeuse and Dubhe, and `make_azalt_plots.py` is fixed to those two as well. For other stars, use `azalt_plots_any_star.py` and rework the rest of the analysis.

---

## 5. Using a different place, time or year

In both scraper files, near the top:

| Setting | Meaning |
|---|---|
| `LAT`, `LNG` | Observer's latitude and longitude in degrees (east and north are positive) |
| `HOUR`, `MINUTE` | Time of day for each reading, in the time zone below |
| `IST = timezone(timedelta(hours=5, minutes=30))` | Time zone of `HOUR` and `MINUTE`. Change it if you are not in India. |
| `DELAY`, `WAIT` | Seconds to pause between loads, and seconds to wait for each page |

The **year** is written into the code: the dates are built from `date(2026, 1, 1)` and `range(365)` in `main()`, so change the 2026 and use 366 for a leap year.

`analysis.py` also contains values specific to this project: the latitude, the 2026 equinox and solstice dates, the UTC+5.5 offset in the equation-of-time calculation, and the two stars' declinations. Update these if you change the place, year or stars.

---

## 6. File formats

**Raw CSV** (`stellarium_constellations_2026.csv`, `stellarium_sun_2026.csv`), one row per reading:

| Column | Meaning |
|---|---|
| `Date` | Date of the reading |
| `Object` | Star or `Sun` |
| `Az_deg`, `Az_DMS` | Azimuth in decimal degrees and in degrees-minutes-seconds. Azimuth is measured from north through east: N = 0, E = 90, S = 180, W = 270. |
| `Alt_deg`, `Alt_DMS` | Altitude above the horizon. A negative value means the object is below the horizon. |
| `RA_Dec_shown` | Right ascension and declination as shown in Stellarium's panel |
| `PageClock`, `PageDate` | The clock and date Stellarium displayed when the value was read, as a check on timing |

**Wide CSV:** one row per `Date`, with columns `<Object>_Az_deg` and `<Object>_Alt_deg`. It contains the same numbers, reshaped, and drops the other columns. It involves no extra calculation.

---

## 7. How the scraper works, and what can go wrong

For each date, the script:

1. Opens Stellarium Web with the date, time and location in the address.
2. Types the object's name into the search box and clicks the first result.
3. Reads the **Az/Alt** row from the information panel that opens.
4. Saves the reading with the clock the page displayed.

Known limits:

- **It depends on Stellarium Web's current layout** (the search box and the "Az/Alt" row). If the site changes, the script may stop working and need updating.
- **The clock is not paused.** Stellarium's clock keeps running after a page loads, so a reading can be a few seconds late. Every row records the page clock so this can be checked. A star moves about 15 arcseconds per second of time, so a delay of 10 seconds is about 0.04°.
- **Direct links to a star did not work reliably** (`stellarium-web.org/skysource/<name>` sometimes loaded the sky without selecting the star), which is why the script uses the search box.
- **Be gentle with the website.** The script pauses between loads. Do not run several copies at once or lower the delay by much.

Troubleshooting:

| Problem | What to try |
|---|---|
| `panel not found (skipped)` | The page was slow or the star was not selected. Check your internet connection, keep the Chrome window visible and in front, then run the script again to fill the gaps. |
| It fails on every date | Stop with `Ctrl + C` and look at the Chrome window. If the search or the panel does not behave as described above, the site has changed. |
| Page clock far from the target time | The page was very slow to load. Check the connection and rerun that day. |
| Chrome does not open | Make sure Google Chrome is installed, and update Selenium: `pip3 install -U selenium`. |
| Two scripts at once both fail | Run them one at a time. A Chrome window that is covered or minimised stops drawing the sky. |

---

## 8. Accuracy

The readings were compared with an independent calculation from standard astronomical formulas (sidereal time, precession and atmospheric refraction). They agree to within a few hundredths of a degree for most dates. The largest differences, up to about 0.7°, occur for a star within about 1° of the horizon, where different refraction models disagree most.

Other limits to keep in mind:

- One star stands for each constellation, so another star in the same constellation would give slightly different numbers but the same seasonal pattern.
- Stellarium shows an ideal horizon. Real visibility also depends on buildings, trees, haze and moonlight.
- "Above the horizon" means altitude greater than 0°. A date at the boundary can change by about a day with a different refraction model. A practical minimum altitude, such as 10°, may suit your site better.
- The Sun is recorded at 12:00 clock time, not at solar noon, so the dates of its maximum and minimum altitude differ from the solstices by several days.

---

## 9. Data source and notes

Positions come from [Stellarium Web](https://stellarium-web.org). This project is for personal and educational use. Check the website's terms before collecting large amounts of data or using the scraper for anything beyond a school project.

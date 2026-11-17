"""
PART 2 - the Sun at 12:00
Records Az/Alt from Stellarium Web in Chrome, Sonipat, every day of 2026,
at 12:00 IST.

SETUP (once):  pip3 install selenium pandas      (and have Google Chrome installed)
RUN:
  python3 stellarium_sun.py test     # one date only (10 Jan 2026) - compare with Stellarium
  python3 stellarium_sun.py          # full year; saves after every day, safe to stop/restart

About "pausing" the time: each page is loaded with the date/time fixed in the URL and
Az/Alt is read within about a second, so clock drift is under 0.01 deg. The script also
reads the clock shown on the page and warns if it is not 12:00 on the right date.
"""
import re, sys, os, time
from datetime import date, datetime, timedelta, timezone
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

LAT, LNG = 28.9948, 77.0151
IST = timezone(timedelta(hours=5, minutes=30))
HOUR, MINUTE = 12, 0
OBJECTS = ['Sun']
OUT = "stellarium_sun_2026.csv"
WAIT = 25

DMS = r"([+\-\u2212]?)\s*(\d+)\s*\u00b0\s*(\d+)\s*[\u2032'\u2019]\s*([\d.]+)\s*[\u2033\"\u201d]"

def make_url(obj, dt):
    utc = dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (f"https://stellarium-web.org/skysource/{obj.replace(' ', '%20')}"
            f"?date={utc}&lat={LAT}&lng={LNG}&elev=0")

def dms(sign, d, m, s):
    v = int(d) + int(m) / 60 + float(s) / 3600
    return -v if (sign and sign in "-\u2212") else v

def to_dms(v, width=3, signed=False):
    """decimal degrees -> 033deg45'09.2" style text, like Stellarium's panel"""
    sign = "-" if v < 0 else ("+" if signed else "")
    v = abs(v)
    d = int(v); m = int((v - d) * 60); sec = round(((v - d) * 60 - m) * 60, 1)
    if sec >= 60: sec = 0.0; m += 1
    if m >= 60: m = 0; d += 1
    return f"{sign}{d:0{width}d}\u00b0{m:02d}'{sec:04.1f}\""

FREEZE_JS = """
var stel = null, v2 = 0, v3 = 0;
var all = document.querySelectorAll('*');
for (var i = 0; i < all.length && !stel; i++) {
  var el = all[i];
  if (el.__vue__) { v2++; if (el.__vue__.$stel) stel = el.__vue__.$stel; }
  if (el.__vue_app__) { v3++;
    var gp = el.__vue_app__.config && el.__vue_app__.config.globalProperties;
    if (gp && gp.$stel) stel = gp.$stel; }
}
if (!stel && window.$stel) stel = window.$stel;
if (!stel && window.stel) stel = window.stel;
if (!stel) return 'no-stel(vue2=' + v2 + ',vue3=' + v3 + ')';
stel.core.time_speed = 0;
stel.core.observer.utc = arguments[0];
stel.core.observer.latitude = arguments[1] * Math.PI / 180;
stel.core.observer.longitude = arguments[2] * Math.PI / 180;
return 'ok';
"""

def freeze(driver, dt):
    mjd = dt.timestamp() / 86400.0 + 40587.0
    try:
        return driver.execute_script(FREEZE_JS, mjd, LAT, LNG)
    except Exception as e:
        return "err"

def read_page(driver):
    txt = driver.find_element(By.TAG_NAME, "body").text
    m = re.search(r"Az/Alt\s*" + DMS + r"\s*" + DMS, txt)
    if not m:
        return None
    g = m.groups()
    clock = re.search(r"\b(\d{2}:\d{2}:\d{2})\b", txt)
    day = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", txt)
    radec = re.search(r"RA/Dec\s*([^\n]*)", txt)
    az = dms(*g[0:4])
    return dict(az_raw=az, az=az % 360, alt=dms(*g[4:8]),
                clock=clock.group(1) if clock else "",
                day=day.group(1) if day else "",
                radec=radec.group(1).strip() if radec else "")

def _get_once(driver, obj, dt):
    driver.get(make_url(obj, dt))
    end = time.time() + WAIT
    want = f"{dt.hour:02d}:{dt.minute:02d}:00"
    last, frozen = None, None
    while time.time() < end:
        time.sleep(1)
        if frozen != "ok":
            frozen = freeze(driver, dt)
        if frozen == "ok":
            time.sleep(1)                      # let the panel refresh
        r = read_page(driver)
        if not r:
            continue
        r["frozen"] = frozen
        last = r
        if frozen == "ok" and r["clock"] == want:
            return r
    return last   # may be unfrozen; main() prints a warning

def get_one(driver, obj, dt, tries=3):
    for attempt in range(1, tries + 1):
        r = _get_once(driver, obj, dt)
        if r:
            return r
        try:
            body = driver.find_element(By.TAG_NAME, "body").text.replace("\n", " | ")[:160]
        except Exception:
            body = "(could not read page)"
        print(f"   attempt {attempt}/{tries} failed for {obj} {dt.date()} - page says: {body}")
    return None

def main():
    test = len(sys.argv) > 1 and sys.argv[1] == "test"
    days = [date(2026, 1, 10)] if test else [date(2026, 1, 1) + timedelta(d) for d in range(365)]
    cols = ["Date", "Object", "Az_deg", "Az_DMS", "Alt_deg", "Alt_DMS", "RA_Dec_shown", "PageClock", "PageDate"]
    done = pd.read_csv(OUT) if (os.path.exists(OUT) and not test) else pd.DataFrame(columns=cols)
    seen = set(zip(done["Date"].astype(str), done["Object"]))
    rows = done.to_dict("records")
    opts = webdriver.ChromeOptions()
    for flag in ["--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows",
                 "--disable-background-timer-throttling", "--window-size=750,800",
                 "--window-position=760,0"]:
        opts.add_argument(flag)
    driver = webdriver.Chrome(options=opts)
    try:
        for d in days:
            for obj in OBJECTS:
                if (str(d), obj) in seen:
                    continue
                dt = datetime(d.year, d.month, d.day, HOUR, MINUTE, tzinfo=IST)
                r = get_one(driver, obj, dt)
                if r is None:
                    print(f"{d} {obj}: panel not found (skipped)")
                    continue
                az, alt, clock, pday = r["az"], r["alt"], r["clock"], r["day"]
                warn = ""
                if r["frozen"] != "ok":
                    warn += f"  <-- time NOT frozen ({r['frozen']})"
                if clock and clock != f"{HOUR:02d}:{MINUTE:02d}:00":
                    warn += f"  <-- page clock {clock}"
                if pday and pday != str(d):
                    warn += f"  <-- page date {pday}, expected {d}"
                rows.append(dict(zip(cols, [d, obj, round(az, 5), to_dms(az), round(alt, 5), to_dms(alt, 2, True), r["radec"], clock, pday])))
                print(f"{d} {obj:11s} Az={to_dms(az)} ({az:.5f})  Alt={to_dms(alt, 2, True)} ({alt:.5f})  RA/Dec: {r['radec']}  [{clock}]{warn}")
            if not test:
                pd.DataFrame(rows).to_csv(OUT, index=False)
    finally:
        driver.quit()
    if not test and rows:
        df = pd.DataFrame(rows)
        wide = df.pivot(index="Date", columns="Object", values=["Az_deg", "Alt_deg"])
        wide.columns = [f"{b}_{a}" for a, b in wide.columns]
        wide.to_csv(OUT.replace(".csv", "_wide.csv"))
        print("Done:", OUT, "and", OUT.replace(".csv", "_wide.csv"))

if __name__ == "__main__":
    main()

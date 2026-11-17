"""
Automates https://stellarium-web.org in Safari and records Az/Alt for
a list of objects, daily through 2026, at 21:00 IST in Sonipat.

ONE-TIME SETUP:
  1. Install Google Chrome if you don't have it.
  2. In Terminal:            pip3 install selenium pandas
     (no driver install needed; selenium downloads it automatically)

RUN:
  python3 stellarium_scraper.py test      # 1 date only - compare with what you see
  python3 stellarium_scraper.py           # full year (about 30-60 min per object)

The script can be stopped and restarted: it resumes from the CSV it saves.
"""
import re, sys, os, time
from datetime import date, datetime, timedelta, timezone
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

LAT, LNG = 28.9948, 77.0151
IST = timezone(timedelta(hours=5, minutes=30))
HOUR, MINUTE = 21, 0

# names exactly as Stellarium Web's URL / search uses them
OBJECTS = ["Orion", "Ursa Major", "Sun"]       # edit freely (e.g. "Scorpius")
SUN_EXTRA_HOUR = 12                            # also record Sun at 12:00 (visible!)

OUT = "stellarium_2026.csv"
WAIT = 20  # seconds to wait for the info panel


def make_url(obj, dt_ist):
    utc = dt_ist.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    slug = obj.replace(" ", "%20")
    return (f"https://stellarium-web.org/skysource/{slug}"
            f"?date={utc}&lat={LAT}&lng={LNG}&elev=0")


# panel text looks like:  Az/Alt   131°31'35.3"   +57°48'08.8"
DMS = r"([+\-−]?)\s*(\d+)\s*°\s*(\d+)\s*[′'’]\s*([\d.]+)\s*[″\"”]"


def dms(sign, d, m, s):
    v = int(d) + int(m) / 60 + float(s) / 3600
    return -v if sign in "-−" else v


def read_azalt(driver):
    """Return (az, alt) in degrees from the open info panel, or None."""
    txt = driver.find_element(By.TAG_NAME, "body").text
    m = re.search(r"Az/Alt\s*" + DMS + r"\s*" + DMS, txt)
    if not m:
        return None
    g = m.groups()
    return dms(*g[0:4]), dms(*g[4:8])


def get_one(driver, obj, dt_ist):
    driver.get(make_url(obj, dt_ist))
    end = time.time() + WAIT
    while time.time() < end:
        time.sleep(1)
        r = read_azalt(driver)
        if r:
            return r
    return None


def main():
    test = len(sys.argv) > 1 and sys.argv[1] == "test"
    days = [date(2026, 1, 10)] if test else \
        [date(2026, 1, 1) + timedelta(d) for d in range(365)]

    jobs = []  # (label, object, hour)
    for o in OBJECTS:
        jobs.append((o, o, HOUR))
        if o == "Sun":
            jobs.append((f"Sun_{SUN_EXTRA_HOUR}h", "Sun", SUN_EXTRA_HOUR))

    done = pd.read_csv(OUT) if (os.path.exists(OUT) and not test) else \
        pd.DataFrame(columns=["Date", "Label", "Az", "Alt"])
    seen = set(zip(done["Date"].astype(str), done["Label"]))
    rows = done.to_dict("records")

    driver = webdriver.Chrome()
    try:
        for d in days:
            for label, obj, hour in jobs:
                if (str(d), label) in seen:
                    continue
                dt = datetime(d.year, d.month, d.day, hour, MINUTE, tzinfo=IST)
                r = get_one(driver, obj, dt)
                if r is None:
                    print(f"{d} {label}: panel not found (skipping)")
                    continue
                rows.append({"Date": d, "Label": label,
                             "Az": round(r[0], 4), "Alt": round(r[1], 4)})
                print(f"{d} {label:12s} Az={r[0]:9.4f}  Alt={r[1]:9.4f}")
            if not test:
                pd.DataFrame(rows).to_csv(OUT, index=False)
    finally:
        driver.quit()

    df = pd.DataFrame(rows)
    if not test and len(df):
        wide = df.pivot(index="Date", columns="Label", values=["Az", "Alt"])
        wide.columns = [f"{b}_{a}" for a, b in wide.columns]
        wide.to_csv("stellarium_2026_wide.csv")
        print("Saved stellarium_2026.csv and stellarium_2026_wide.csv")


if __name__ == "__main__":
    main()

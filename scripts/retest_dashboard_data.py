"""Data for the EIA Retest Dashboard, from the one source file (EQ-Trends-Raw-Data.csv), with no IDs or dates:
  retest-pairs.csv  one row per person: first self-assessment vs. first retest (2021-2026, at least 30 days later),
                    both with all 28 items answered. Same rule as the Does EQ Improve? page.
  retest-rate.csv   for people whose first self-assessment was in each year: how many retested (any retest, any gap).
Usage: python -I retest_dashboard_data.py <EQ-Trends-Raw-Data.csv> <out folder>"""
import sys
from pathlib import Path

import pandas as pd

SRC, OUT = sys.argv[1], Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
LEVEL = {1: "Independently employed / consultant", 2: "Employee", 3: "Supervisor", 4: "Manager", 5: "Director",
         6: "Vice president", 7: "Senior vice president", 8: "C-level executive", 9: "CEO", 10: "Owner / founder",
         11: "Board member"}
IND = {1: "Aerospace / aviation", 2: "Agriculture", 3: "Biotechnology", 4: "Consulting", 5: "Communications / media",
       6: "Education", 7: "Electronics", 8: "Energy", 9: "Entertainment / arts", 10: "Finance / banking",
       11: "Food service", 12: "Food and beverage", 13: "Government", 14: "Health / wellness", 15: "Healthcare",
       16: "Hospitality", 17: "Insurance", 18: "Manufacturing / consumer goods", 19: "Medical devices", 20: "Military",
       21: "Nonprofit", 22: "Pharmaceuticals", 23: "Professional services", 24: "Real estate", 25: "Religious",
       26: "Retail", 27: "Technology", 28: "Transportation", 29: "Utilities", 30: "Other"}
SK = [("sa", "Self-Awareness"), ("sm", "Self-Management"), ("so", "Social Awareness"), ("rm", "Relationship Management")]
skill_of = lambda n: "sa" if n <= 6 else "sm" if n <= 15 else "so" if n <= 20 else "rm"

f = pd.read_csv(SRC, encoding="utf-8-sig", low_memory=False, parse_dates=["Date"])
f["Year"] = f.Date.dt.year
self_ = f[f["Test version"] == "Self"]

# ---- pairs: the same rule as the page (file is in date order; first row per person) ----
first = self_.groupby("Participant ID").nth(0).set_index("Participant ID")
again = f[(f["Test version"] == "Re-Assessment") & (f.Year >= 2021)].groupby("Participant ID").nth(0).set_index("Participant ID")
m = first.join(again, rsuffix="_r", how="inner")
m["days"] = (m.Date_r - m.Date).dt.days
m = m[m.days >= 30]

rows = []
for _, r in m.iterrows():
    A = {r[f"Behavior {i}_r"] for i in (1, 2, 3) if pd.notna(r[f"Behavior {i}_r"])}
    F = [r[f"Behavior {i}"] for i in (1, 2, 3) if pd.notna(r[f"Behavior {i}"])]
    tot = {k: 0 for k, _ in SK}; mv = {k: 0 for k, _ in SK}
    for b in F:
        k = skill_of(int(str(b).rstrip("AB")))
        tot[k] += 1; mv[k] += b not in A
    row = {"first_year": int(r.Year), "retest_year": int(r.Year_r), "days_apart": int(r.days),
           "industry": IND.get(int(r.Industry), "") if pd.notna(r.Industry) else "",
           "job_level": LEVEL.get(int(r["Job level"]), "") if pd.notna(r["Job level"]) else "",
           "first_eq": int(r.EQ), "retest_eq": int(r.EQ_r)}
    for k, name in SK:
        row[f"first_{k}"] = int(r[name]); row[f"retest_{k}"] = int(r[f"{name}_r"])
    row["behaviors"] = len(F); row["behaviors_moved"] = sum(mv.values())
    for k, _ in SK:
        row[f"{k}_behaviors"] = tot[k]; row[f"{k}_moved"] = mv[k]
    rows.append(row)
pairs = pd.DataFrame(rows)
pairs.to_csv(OUT / "retest-pairs.csv", index=False)

# ---- retest rate by first-assessment year (any retest, any gap) ----
fs = self_.groupby("Participant ID").Date.first()
ever = set(f.loc[f["Test version"] == "Re-Assessment", "Participant ID"])
rate = []
for y in range(2021, 2027):
    c = fs[fs.dt.year == y]
    k = int(c.index.isin(list(ever)).sum())
    rate.append({"first_year": y, "people": len(c), "retested": k, "pct_retested": round(k / len(c) * 100, 2),
                 "complete_year": "yes" if y <= 2025 else "no"})
pd.DataFrame(rate).to_csv(OUT / "retest-rate.csv", index=False)

g = pairs.retest_eq - pairs.first_eq
print("pairs", len(pairs), "gain %.3f" % g.mean(), "higher %.1f" % ((g > 0).mean() * 100),
      "median days", pairs.days_apart.median(), "moved>=1 %.1f" % ((pairs.behaviors_moved > 0)[pairs.behaviors > 0].mean() * 100))
print(pd.DataFrame(rate).to_string(index=False))

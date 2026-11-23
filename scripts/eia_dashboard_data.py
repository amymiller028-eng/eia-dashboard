"""Summary data for the EIA Dashboard, from the one source file (EQ-Trends-Raw-Data.csv): self-assessments
2021-2026 with all 28 items answered (the site total), aggregated so no person can be picked out.
  eia-summary.csv       one row per group: section, group, order, people, eq, sa, sm, so, rm, pct_low, pct_high
                        (sections: overall, year, gender, age_band, generation, region, job_level, job_function,
                        industry, company_size, employment; groups under 100 people are left out)
  eia-distribution.csv  people at each EQ score
Usage: python -I eia_dashboard_data.py <EQ-Trends-Raw-Data.csv> <out folder>"""
import sys
from pathlib import Path

import pandas as pd

SRC, OUT = sys.argv[1], Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
CODES = {
    "Gender": {1: "Men", 2: "Women", 3: "Nonbinary"},
    "Age band": {1: "18–19", 2: "20–29", 3: "30–39", 4: "40–49", 5: "50–59", 6: "60–69", 7: "70–79", 8: "80 and over"},
    "Region": {1: "North America", 2: "Central America", 3: "South America", 4: "Western Europe", 5: "Eastern Europe",
               6: "Middle East", 7: "Asia", 8: "Africa", 9: "Australia", 10: "New Zealand", 11: "Polynesia"},
    "Job level": {1: "Independently employed / consultant", 2: "Employee", 3: "Supervisor", 4: "Manager", 5: "Director",
                  6: "Vice president", 7: "Senior vice president", 8: "C-level executive", 9: "CEO", 10: "Owner / founder",
                  11: "Board member"},
    "Job function": {1: "Administration / office", 2: "Customer service", 3: "Community / social service", 4: "Consultant / advisor",
                     5: "Engineering", 6: "Faculty / educator", 7: "Finance / accounting", 8: "Facility maintenance",
                     9: "Government official", 10: "HR / training", 11: "IT", 12: "Legal", 13: "Law enforcement / security",
                     14: "Nursing", 15: "Physician", 16: "Allied health", 17: "Planning / strategy", 18: "Projects / programs",
                     19: "Manufacturing", 20: "Marketing", 21: "Operations", 22: "Research and development",
                     23: "Services worker", 24: "Sales", 25: "Other"},
    "Industry": {1: "Aerospace / aviation", 2: "Agriculture", 3: "Biotechnology", 4: "Consulting", 5: "Communications / media",
                 6: "Education", 7: "Electronics", 8: "Energy", 9: "Entertainment / arts", 10: "Finance / banking",
                 11: "Food service", 12: "Food and beverage", 13: "Government", 14: "Health / wellness", 15: "Healthcare",
                 16: "Hospitality", 17: "Insurance", 18: "Manufacturing / consumer goods", 19: "Medical devices", 20: "Military",
                 21: "Nonprofit", 22: "Pharmaceuticals", 23: "Professional services", 24: "Real estate", 25: "Religious",
                 26: "Retail", 27: "Technology", 28: "Transportation", 29: "Utilities", 30: "Other"},
    "Company size": {1: "1 employee", 2: "2–100", 3: "101–500", 4: "501–1,000", 5: "1,001–5,000", 6: "5,000–50,000", 7: "50,000+"},
    "Employment status": {1: "Not currently employed", 2: "Retired", 3: "Full-time student", 4: "Full-time", 5: "Part-time"},
}
SECTION = {"Gender": "gender", "Age band": "age_band", "Region": "region", "Job level": "job_level",
           "Job function": "job_function", "Industry": "industry", "Company size": "company_size",
           "Employment status": "employment"}
MID = {1: 18.5, 2: 24.5, 3: 34.5, 4: 44.5, 5: 54.5, 6: 64.5, 7: 74.5, 8: 82}

f = pd.read_csv(SRC, encoding="utf-8-sig", low_memory=False, parse_dates=["Date"])
d = f[(f["Test version"] == "Self") & f.Date.dt.year.between(2021, 2026)].copy()
d["Year"] = d.Date.dt.year
d["Generation"] = pd.cut(d.Year - d["Age band"].map(MID), [1900, 1964, 1980, 1996, 2015],
                         labels=["Baby Boomers", "Gen X", "Millennials", "Gen Z"]).astype(str).replace("nan", None)


def stats(g):
    return {"people": len(g), "eq": round(g.EQ.mean(), 1), "sa": round(g["Self-Awareness"].mean(), 1),
            "sm": round(g["Self-Management"].mean(), 1), "so": round(g["Social Awareness"].mean(), 1),
            "rm": round(g["Relationship Management"].mean(), 1),
            "pct_low": round((g.EQ < 65).mean() * 100, 1), "pct_high": round((g.EQ > 85).mean() * 100, 1)}


rows = [{"section": "overall", "group": "Everyone", "order": 0, **stats(d)}]
for i, (y, g) in enumerate(d.groupby("Year")):
    rows.append({"section": "year", "group": str(y) + (" (through Sept.)" if y == 2026 else ""), "order": i, **stats(g)})
for col, codes in CODES.items():
    for i, (code, name) in enumerate(codes.items()):
        g = d[d[col] == code]
        if len(g) >= 100:
            rows.append({"section": SECTION[col], "group": name, "order": i, **stats(g)})
for i, name in enumerate(["Gen Z", "Millennials", "Gen X", "Baby Boomers"]):
    rows.append({"section": "generation", "group": name, "order": i, **stats(d[d.Generation == name])})
pd.DataFrame(rows).to_csv(OUT / "eia-summary.csv", index=False)

dist = d.EQ.value_counts().sort_index()
pd.DataFrame({"score": dist.index.astype(int), "people": dist.values}).to_csv(OUT / "eia-distribution.csv", index=False)
print(pd.DataFrame(rows).query("section in ['overall','gender','year']").to_string(index=False))
print("groups", len(rows), "scores", len(dist), "sd %.2f" % d.EQ.std())

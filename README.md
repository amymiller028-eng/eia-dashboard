# EQ Research & Insights (EIA Dashboard)

An interactive dashboard of TalentSmartEQ's Emotional Intelligence Appraisal (EIA) data, plus a library of third-party research facts.

## What's here

| Folder | What it holds |
|---|---|
| `dashboard/index.html` | The dashboard page. It runs inside its Claude dashboard (it uses that tool's data and drawing functions), so opening it straight from GitHub won't show the charts. |
| `data/eia-summary.csv` | Average EQ, the four skills, and the share scoring low and high, for everyone and by year, gender, age, generation, region, job level, job function, industry, company size, and employment status. Groups under 100 people are left out. |
| `data/eia-distribution.csv` | Number of people at each EQ score (the bell curve). |
| `data/retest-rate.csv` | Share of people who retest, by the year they first took the EIA. |
| `data/retest-pairs.csv` | One anonymous row per retest: first and retest scores, days apart, industry, and job level. No IDs. |
| `data/research-facts.csv` / `.json` | The Third-Party Research Facts: headline, big number, fact, short source, full APA citation, and link. |
| `scripts/` | The Python scripts that build the data files from the one source file, `EQ-Trends-Raw-Data.csv`. |

## The data

- Source: the EQ Trends raw data file (October 26, 2026 data snapshot).
- Everything outside the retests uses self-assessments from 2021 through September 2026 with all 28 questions answered: 731,371 people. This is the same group as the EQ trends research pages.
- Scores are on a 0–100 scale. Low is below 65 and high is above 85.

## Rebuilding the data

```
python scripts/eia_dashboard_data.py EQ-Trends-Raw-Data.csv data
python scripts/retest_dashboard_data.py EQ-Trends-Raw-Data.csv data
```

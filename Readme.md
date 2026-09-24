# Shark Attacks: A Coastal Safety Analysis

Data cleaning and exploratory analysis of the real **Global Shark Attack File (GSAF)**, built for the Ironhack Data Analytics bootcamp's "Quest: Shark Attacks Mini-Project."

## Business case

Acting as a **coastal safety authority**, this project asks: where — and during which activities — do shark attacks happen most, and how dangerous is each situation really? The goal is to turn raw incident reports into a signal for where to prioritize lifeguard presence and warning signage.

## Hypotheses

1. **Surfing is the activity most associated with shark attacks.**
2. **Shark attacks occur more frequently in the USA than in other countries.**

## Team

| Name | Columns cleaned |
|---|---|
| Pariya | `Activity`, `State` — plus dropping unnecessary columns, standardizing column names, and merging everyone's functions into one notebook |
| Zahid | `Time`, `Date` |
| Miguel | `Sex`, `Country`, `Year` |
| Effie | `Location`, `Injury`, `Fatal Y/N` |

## Repository structure

```
shark_attacks/
├── shark_attacks_quest.ipynb   # main notebook: cleaning + EDA + findings
├── cleaning_functions.py       # standalone clean_<column>(df) functions, by teammate
├── sharks.xls                  # raw dataset (GSAF, source: sharkattackfile.net)
└── README.md
```

## Dataset

The real Global Shark Attack File — **7,117 recorded incidents, 23 raw columns**, spanning over a century of manually logged reports. Only the **10 columns relevant to the business case are kept** for analysis (13 dropped): `Date`, `Year`, `Country`, `State`, `Location`, `Activity`, `Sex`, `Injury`, `Fatal Y/N`, `Time`.

The raw data is messy in the ways real-world data usually is: inconsistent casing and whitespace (`"usa"`, `"AUSTRALIA"`, `" PHILIPPINES"`), fake-missing values hiding as text (`"UNKNOWN"`, `"?"`), junk entries in the wrong column (a year typed into `Fatal Y/N`), and free-text fields that need parsing rather than a simple type conversion.

## Cleaning techniques applied

Each teammate cleaned their assigned columns using a shared convention — `clean_<column>(df)`, always returning `df`. All four members' functions are merged into a single pipeline in the main notebook, with column selection and column-name standardization run first/last so casing stays consistent across everyone's code.

| Technique | Applied to |
|---|---|
| Irrelevant column removal | dropped 13 of 23 raw columns, keeping only the 10 needed for the business case |
| Column name standardization | all kept columns (lowercase, underscores, no stray whitespace) |
| Whitespace & casing standardization | `Activity`, `State`, `Country`, `Location` |
| Fake-missing → real `NaN` / `Unknown` | `Fatal Y/N`, `Sex`, `Injury` |
| Category mapping | `Fatal Y/N` (`"Y"`/`"N"` → `"Yes"`/`"No"`) |
| Keyword-based inference for unresolved values | `Fatal Y/N`, inferred from `Injury` text when the raw value is missing/junk |
| Duplicate row removal | whole dataset (16 duplicate rows found and dropped) |
| Regex extraction | `Time` (e.g. `"1400h"` → `14:00`), `Date` (e.g. `"23rd August"` → day-month text cleaned for parsing) |

## Key findings

**Hypothesis 1 — supported.** `Surfing` has the highest number of recorded attacks among individual activities (1,161), ahead of `Swimming` (1,071).

**Hypothesis 2 — supported.** The USA has by far the highest number of recorded attacks (2,592), well ahead of Australia (1,534) and South Africa (599).

**Beyond frequency — a risk nuance for the safety authority:** the activity with the *most* incidents isn't the *most dangerous* one per incident. `Surfing` has a fatality rate of just 5.9%, while `Swimming` (36.7%) and `Bathing` (47.3%) are far more likely to be fatal when an attack does occur. Similarly, the USA sees more attacks overall but a lower fatality rate (10.8%) than the rest of the world combined (32.8%) — likely reflecting factors like medical response time, though the dataset alone can't confirm the cause.

## Recommendations

- Prioritize signage and lifeguard presence by **activity type**, not just location — surfing spots see the most incidents.
- Weight lifeguard staffing by **fatality rate**, not just incident count — swimming and bathing areas are less frequent but more dangerous per incident.
- Track both frequency and fatality rate over time, since they tell different stories.

## How to run

1. Clone this repository.
2. Install dependencies: `pandas`, `numpy`, `matplotlib`, `seaborn`, and `xlrd` (needed to read the legacy `.xls` format).
3. Open `shark_attacks_quest.ipynb` in Jupyter and run all cells top to bottom.

## Presentation

Slides: [Shark Attacks: A Coastal Safety Analysis](https://docs.google.com/presentation/d/1h_5b9WHAi3uCA4_4xrz5WKfyQb9KK5F8LA0GGuihCEg/edit)

---
*Ironhack Data Analytics Bootcamp — Data Cleaning & EDA Quest*

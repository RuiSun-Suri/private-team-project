# Project Deliverable 2 — One-shot Prompt

You are the coding agent responsible for building a complete, working first release of **Mortgage Market Growth and Risk Screening**. Treat **this entire Markdown file as the single, authoritative build prompt**. Make the implementation decisions specified below without asking for clarification. Produce executable code, a usable dashboard, instructions and tests—not just a mockup, plan, or another prompt. Work from an empty local directory if needed; do not assume that any previous conversation, agent state, source code, or downloaded data is available.

**Team GitHub repository (include this link in the hand-in):** https://github.com/clgarman/dso-576-team-project

The repository is private; access may require an authorized GitHub account. If accessible, inspect it and use its canonical file `county_metrics_2024.csv`. If not accessible, build from the exact 25-row snapshot provided later in this prompt. That fallback is a copy of the team's existing canonical file, **not invented or synthetic data**. Do not let an inability to open the repository stop you from building and testing the product. If the repository is accessible, preserve its existing history and original files.

## A. Decision and scope

Build a single-page, locally runnable **California Mortgage Activity & Complaints** dashboard for a bank strategy or risk manager deciding **which counties deserve additional investigation**. The original team vision considered growth opportunities alongside financial risk using HMDA, CFPB and SEC data. The **available, agreed cleaned dataset supports a narrower 2024 proof of concept**: county-level comparisons of mortgage originations and geographically mapped complaints associated with JPMorgan Chase. It does **not** support multi-bank comparisons, year-over-year growth, SEC financial health trends or a market-entry recommendation. Do not implement controls or claims implying those unsupported functions.

Use cases (each feature must serve one):
1. **Manager opens the app** → sees 2024 coverage, counts, exploratory complaint/origination index and ranked represented counties → chooses counties for deeper review.
2. **Manager selects a county** → sees its mapped complaints, originations and index alongside their denominators → decides whether the county's observed signals warrant further examination.
3. **Manager changes the minimum origination count** → sees the county ranking shrink accordingly without changing the overall unfiltered totals → avoids overinterpreting small-denominator outliers.

## B. Data contract — use only evidence supplied here

The canonical data is a county-aggregate table, exactly one row per **California county with at least one mapped complaint**. It is **not all California counties**. Treat this table as read-only; do not call, import, or run `cleaning_homework.py` in application startup, dashboard tests or deployment, because rerunning cleaning may overwrite the file. Never quietly regenerate different data. This task does not require live APIs, SEC downloads, GIS services, a database or confidential credentials.

The **only five input columns** are:

| Column | Meaning | Type |
|---|---|---|
| `GEOID_COUNTY_20` | Five-character CA county FIPS code, including leading zero; primary key | string |
| `NAMELSAD_COUNTY_20` | County label | string |
| `complaints` | 2024 CA mortgage complaints mapped from CFPB records attributed to Company `JPMORGAN CHASE & CO.` | nonnegative integer |
| `originations` | 2024 HMDA originations (`action_taken == 1`) for JPMorgan Chase Bank, National Association; LEI `7H6GLXDRUGQFU57RNE97` | positive integer in submitted rows |
| `complaints_per_1000_originations` | Stored `1000 * complaints / originations` | numeric |

The parent-company CFPB complaints and bank-level HMDA records **have not been proven to describe identical reporting entities or individual loan cohorts**. Use labels naming the sources. Call the quotient **"exploratory cross-source index per 1,000"**, never "bank risk rate," "complaint probability," "loan failure rate" or "market growth." The numerator is complaints received in 2024, not complaints necessarily arising from loans originated in 2024. The analysis is an *investigation queue*, not a causal model or bank expansion recommendation.

Known upstream exclusions and coverage (display these in the app's methodology panel): 68 targeted CFPB complaints, 64 mapped to county (3 masked ZIP codes, 1 complete but unmatched ZIP); 10,826 total CA originations in the 2024 HMDA export, of which **9,966 fall in the 25 counties represented in the canonical table**; geographic assignments use a 2020 Census ZCTA-to-county crosswalk with the largest-land-area match where a ZCTA spans counties. The approximate geography and missing counties constrain conclusions. Do not invent values or assign zero complaints to absent counties.

Use this **verbatim canonical CSV snapshot** if the GitHub file is inaccessible. On a new project, create `county_metrics_2024.csv` with these exact bytes and names. If the repo is accessible and the file exists, use that file and ensure the values agree with this snapshot; on disagreement report and stop rather than silently choosing another definition.

```csv
GEOID_COUNTY_20,NAMELSAD_COUNTY_20,complaints,originations,complaints_per_1000_originations
06007,Butte County,1,16,62.5
06087,Santa Cruz County,1,41,24.390243902439025
06055,Napa County,1,43,23.25581395348837
06099,Stanislaus County,3,137,21.897810218978105
06017,El Dorado County,1,51,19.607843137254903
06079,San Luis Obispo County,1,58,17.241379310344826
06013,Contra Costa County,5,343,14.577259475218659
06047,Merced County,1,78,12.82051282051282
06095,Solano County,1,80,12.5
06075,San Francisco County,5,435,11.494252873563218
06097,Sonoma County,1,88,11.363636363636363
06041,Marin County,1,92,10.869565217391305
06061,Placer County,1,93,10.752688172043012
06073,San Diego County,9,975,9.230769230769232
06001,Alameda County,4,533,7.5046904315197
06077,San Joaquin County,1,135,7.407407407407407
06029,Kern County,1,175,5.714285714285714
06065,Riverside County,3,619,4.846526655896607
06019,Fresno County,1,225,4.444444444444445
06085,Santa Clara County,3,709,4.2313117066290555
06067,Sacramento County,1,246,4.065040650406504
06037,Los Angeles County,13,3211,4.048582995951417
06059,Orange County,3,753,3.9840637450199203
06081,San Mateo County,1,353,2.8328611898017
06071,San Bernardino County,1,477,2.0964360587002098
```

## C. Technical specification

**Stack:** Python 3.12, pandas, NumPy, Streamlit. Build a single app page launched by `python -m streamlit run app.py` from the project root. Use local CSV data only; 25 rows require no database or external API. The app must work locally even with no network connection after dependencies have been installed. Specify `streamlit`, `pandas` and `numpy` in a root `requirements.txt`. Avoid extra dependencies or a complicated build system. Use a clean, readable Streamlit layout and descriptive labels; no fabricated charts, credentials, dummy integrations or generic marketing filler.

**Files to create or maintain:**
- `county_metrics_2024.csv`: original five-column canonical snapshot, unchanged once established.
- `analysis_backend.py`: pure, reusable data functions, independent of Streamlit.
- `app.py`: presentation that calls the backend and does not reimplement metrics.
- `tests/test_analysis_backend.py`: executable `unittest` tests covering real records, bad inputs and filters.
- `requirements.txt`: runtime dependencies, and `README.md`: installation, local run, tests, data scope and how to deploy.

If an existing repo already contains a working `analysis_backend.py`, inspect and reuse it rather than rewrite it unnecessarily. Do not remove teammates' code or overwrite their Module 6 notebooks. The one-shot prompt—not any hidden preexisting implementation—defines the required behavior.

### Backend contracts

Implement callable functions with these signatures and return values:
- `load_county_metrics(csv_path=None) -> pandas.DataFrame`: default path is `county_metrics_2024.csv` relative to the backend script's `__file__`, **not the current working directory**. Check required columns, nonblank names, five-digit CA FIPS codes, unique counties, nonnegative integer counts, strictly positive origination denominators, finite numeric indices, and no missing values. Validate stored index using `numpy.isclose` against `1000 * complaints / originations` (`rtol=1e-10`, `atol=1e-8`). Preserve FIPS leading zeros. Return a fresh clean DataFrame or raise an informative exception; never silently fill corrupt numbers.
- `overview_metrics(frame) -> dict`: return `counties_with_mapped_complaints`, `mapped_complaints`, `originations_in_these_counties`, and `pooled_complaints_per_1000_originations`. Calculate the last value as **total complaints / total originations × 1,000**, not a mean of county indices. This covers all 25 rows regardless of ranking controls.
- `rank_counties(frame, min_originations=0, limit=None) -> pandas.DataFrame`: return county rows with `originations >= min_originations`, sorted by index descending then FIPS ascending; optional limit applied after sorting. Reject negative or noninteger thresholds and invalid limits. If none qualify, return a correctly typed **empty DataFrame** with expected columns.
- `county_detail(frame, county_fips) -> pandas.DataFrame`: one row for a selected FIPS. If FIPS is not represented, raise `KeyError` rather than invent a zero row.

Keep the CSV immutable during the app's normal operation. Verify the repo version or fallback snapshot is the expected 25-row dataset before displaying any result. At minimum, validate both its schema/formula and the independent known-row/total checks below. If you choose to lock to a content hash, document the expected hash and test the failure path; do not assume the older backend has already implemented such a lock.

### Dashboard screen

1. **Header:** `California Mortgage Activity & Complaints` with `2024 | Exploratory county screening` subtitle. Directly below, an easily noticed plain-language warning: `Data cover 25 counties with mapped CFPB complaints, not all California counties. CFPB company complaints and bank HMDA originations are not verified as the same loan or reporting-entity population.`
2. **Four summary metrics:** `Counties represented: 25`, `CFPB complaints mapped: 64`, `Bank originations in those counties: 9,966`, and `Exploratory index per 1,000: 6.42`. Recompute from loaded data, never store the displayed totals as independent constants.
3. **Controls:** county selectbox keyed by FIPS with readable county labels (default Los Angeles `06037`); a nonnegative integer minimum-originations control (default `0`; allow thresholds above the largest origination value so an empty state can be tested); optional top-N ranking control (default all represented counties).
4. **Ranking:** a table sorted highest index first, showing county, mapped CFPB complaints, bank originations and index (two decimal places). Display number of ranked rows after filtering. Optional bar chart may mirror the table if it doesn't obscure denominator context. The filter must affect **ranking only**, not the summary metrics or selected-county detail.
5. **County detail:** show selected county's exact complaints, originations and index; warn that a high index based on few originations can be unstable. If selected county doesn't satisfy current ranking threshold, keep the detail visible and explain the exclusion.
6. **Empty ranking:** when no county meets the threshold, show exactly `No counties meet this minimum origination count. Lower the threshold.` Show no empty chart placeholder or invented county, and keep summary and selected-county details visible.
7. **Methodology and limitations:** an expandable section covering the five input field definitions, ratio, missing-county bias, 64/68 geographic coverage, 9,966/10,826 origination coverage, Census crosswalk approximation, CFPB/HMDA legal-entity mismatch and the absence of loan-cohort matching. State clearly that these figures cannot establish causation, year-over-year growth or a validated bank risk rate.
8. **Data failure:** if CSV is missing, has changed unexpectedly or fails validation, show a visible error and stop rendering analytic outputs. Do not display stale results or substitute made-up values.

### Build and verification sequence

1. Inspect the available repo if authorized. Establish the canonical CSV using the repo file or exact embedded fallback; do not pull unverified newer data or run the historic cleaning script.
2. Build/reuse the backend and execute tests without importing Streamlit.
3. Build the Streamlit app with source-labeled metrics and controls wired to backend functions.
4. Run unit tests and launch the app locally; check default, selected county, filtering, empty state and data-failure behavior.
5. Write a concise README explaining installation, execution, tests, known limitations and deploy steps. For Streamlit Community Cloud, deploy the repository with `app.py` as the entrypoint and Python 3.12 plus the root `requirements.txt`; no API keys or raw downloads required. A live hosted deployment requires repository access and is a follow-on operational step; don't claim one exists without its actual URL and verification.
6. Deliver code and a short final report of which acceptance checks passed or failed. If a required operation was not run, report it as unverified; do not claim success based solely on writing tests.

## D. Acceptance checks (must be demonstrable)

- Source contains exactly **25 unique** California county keys and the columns above; complaints sum to **64**, originations in those rows to **9,966**, pooled index to approximately **6.42**, calculated from totals.
- Los Angeles County (`06037`): **13** complaints, **3,211** originations, index approximately **4.05**.
- Butte County (`06007`) is the highest raw index: **1** complaint / **16** originations = **62.50**; clearly identify the small denominator and avoid calling Butte objectively highest risk.
- `rank_counties(..., min_originations=100)` excludes Butte; the original county detail remains available. A threshold greater than **3,211** produces zero ranking rows and the exact empty-state message.
- Unknown FIPS (e.g. `06003`) cannot generate a fabricated row. A deliberately corrupted index, duplicate FIPS, blank name, or zero denominator must cause validation failure.
- Changing the ranking filter does not change the four unfiltered summary totals. Rounding affects display, never analysis.
- UI contains no lender picker, year picker, SEC financial charts, inferred growth forecasts or unverified risk scores. Every numeric display and statement is traceable to the canonical source and to these definitions.
- The app starts using the documented command and shows useful errors if its data are invalid; checks run reproducibly using `python -m unittest discover -s tests -v`.

**Finish by delivering the working app and its tests, not by asking for additional product choices.** If a task requires more data than provided here, state that limitation and keep it out of the initial release rather than inventing it.

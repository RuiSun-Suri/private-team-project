# California Mortgage Activity & Complaints

Single-page Streamlit dashboard built from `ONE_SHOT_PROMPT.md`. Python 3.12 is
the specified runtime. All calculations use the existing `analysis_backend.py`;
the app reads the original local CSV and makes no API calls.

## Install and run on Windows

From this folder, create an environment if one does not already exist:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If `.venv` is already installed, only the final command is needed. Keep that
terminal running; open the local URL it prints. Press Ctrl+C to stop the server.
In VS Code use Python: Select Interpreter and select `.venv\Scripts\python.exe`.
Standard activated-environment command: `python -m streamlit run app.py`.
The app resolves its CSV next to its own source file, even from another directory.

## Use

- Default selection: Los Angeles County; ranking includes all 25 represented counties.
- Choose a county to see source counts and its exploratory index.
- Minimum originations affects ranking only. Try 100 to exclude Butte or 3212
  to see the empty-state message. Summary totals and selected detail stay visible.
- Ranking rows optionally limits the table after sorting; defaults to all.
- Expand methodology to understand source definitions and coverage limitations.

## Data and safeguards

The canonical CSV has 25 counties with mapped complaints, 64 complaints and 9,966
originations. It is not a complete statewide county table. Overall index is about
6.42 per 1,000; LA is 13 / 3,211 × 1,000, about 4.05. Butte is 1 / 16 × 1,000 = 62.50;
that small denominator does not establish that it is objectively highest risk.
CFPB parent-company complaints and bank-level HMDA records are not verified as
the same reporting population or loan cohort. No growth forecast, causal claim,
SEC financial-health analysis, or multi-bank comparison is supported.

The app checks the canonical CSV's SHA-256 on every run, normalizing CRLF to LF:
`8bbaa2526418a77723a911e4f7788a04edabcc8afa5a33dd90f279dd1f4cba6d`.
Missing, invalid or unexpectedly altered data stops analytic output. The app
does not cache previous results or rerun the original cleaning script. Deliberate
data changes require team review, updated specifications, hash and acceptance tests.

## Verify

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests include source totals, known rows, invalid inputs, filtering, snapshot
protection and Streamlit interactions (including data failure using temporary files).

## Optional deployment

Team reference: https://github.com/clgarman/dso-576-team-project

Push this app and required source files to an authorized GitHub repository, excluding
`.venv`, credentials and temporary files. For Streamlit Community Cloud, choose that
repository, `app.py` as entrypoint, Python 3.12 and root `requirements.txt`.
After deploying, verify the live URL, selected-county behavior and an empty filter.
No deployment or push is performed by creating these local files.

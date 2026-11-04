"""Streamlit presentation for the agreed 2024 county-screening snapshot."""
from hashlib import sha256
from pathlib import Path

import streamlit as st

from analysis_backend import (
    COUNTY_ID, COUNTY_NAME, COMPLAINTS, ORIGINATIONS, RATE,
    load_county_metrics, overview_metrics, rank_counties, county_detail,
)

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "county_metrics_2024.csv"
# Normalize only Windows/Unix line endings; every other byte must match.
EXPECTED_DATA_SHA256 = "8bbaa2526418a77723a911e4f7788a04edabcc8afa5a33dd90f279dd1f4cba6d"
EMPTY_MESSAGE = "No counties meet this minimum origination count. Lower the threshold."
DATA_ERROR = "Dataset unavailable or failed validation. Contact the project team."


def load_verified_data():
    """Reject an unexpected snapshot before showing any analytic outputs."""
    content = DATA_PATH.read_bytes().replace(b"\r\n", b"\n")
    if sha256(content).hexdigest() != EXPECTED_DATA_SHA256:
        raise ValueError("The county dataset does not match the agreed snapshot.")
    return load_county_metrics(DATA_PATH)


def main():
    st.set_page_config(
        page_title="California Mortgage Activity & Complaints",
        page_icon="📊", layout="wide",
    )
    st.title("California Mortgage Activity & Complaints")
    st.caption("2024 | Exploratory county screening")
    st.warning(
        "Data cover 25 counties with mapped CFPB complaints, not all California counties. "
        "CFPB company complaints and bank HMDA originations are not verified as the same "
        "loan or reporting-entity population."
    )

    # Intentionally no cache: validate the current file on every interaction.
    try:
        data = load_verified_data()
    except (OSError, ValueError, TypeError, OverflowError):
        st.error(DATA_ERROR)
        st.stop()

    summary = overview_metrics(data)
    cards = st.columns(4)
    cards[0].metric("Counties represented", f"{summary['counties_with_mapped_complaints']:,}")
    cards[1].metric("CFPB complaints mapped", f"{summary['mapped_complaints']:,}")
    cards[2].metric("Bank originations in those counties", f"{summary['originations_in_these_counties']:,}")
    cards[3].metric("Exploratory index per 1,000", f"{summary['pooled_complaints_per_1000_originations']:.2f}")
    st.caption(
        f"Overall index: {summary['mapped_complaints']:,} mapped CFPB complaints / "
        f"{summary['originations_in_these_counties']:,} HMDA originations × 1,000. "
        "These totals always cover every represented county, regardless of ranking controls."
    )
    st.divider()

    county_options = data.sort_values(COUNTY_NAME)[COUNTY_ID].tolist()
    names = dict(zip(data[COUNTY_ID], data[COUNTY_NAME]))
    controls = st.columns([2, 1, 1])
    selected = controls[0].selectbox(
        "County detail", county_options,
        index=county_options.index("06037") if "06037" in county_options else 0,
        format_func=lambda fips: f"{names[fips]} ({fips})", key="county",
    )
    minimum = controls[1].number_input(
        "Minimum originations", min_value=0, value=0, step=1, key="minimum",
        help="Applies to the ranking only. There is no upper cap: try 3,212 for an empty ranking.",
    )
    top_n = controls[2].selectbox(
        "Ranking rows", [None, 5, 10, 15, 20],
        format_func=lambda n: "All represented counties" if n is None else f"Top {n}",
        key="top_n",
    )

    ranked = rank_counties(data, min_originations=int(minimum))
    shown = rank_counties(data, min_originations=int(minimum), limit=top_n)
    ranking_panel, detail_panel = st.columns([2, 1], gap="large")
    with ranking_panel:
        st.subheader("County ranking")
        st.caption(
            f"{len(ranked)} counties meet the minimum; showing {len(shown)}. "
            "Sorted by exploratory index, highest first. High values based on few "
            "originations can be unstable and do not establish higher underlying risk."
        )
        if ranked.empty:
            st.info(EMPTY_MESSAGE)
        else:
            st.dataframe(
                shown[[COUNTY_NAME, COMPLAINTS, ORIGINATIONS, RATE]].rename(columns={
                    COUNTY_NAME: "County", COMPLAINTS: "Mapped CFPB complaints",
                    ORIGINATIONS: "HMDA originations", RATE: "Exploratory index per 1,000",
                }),
                hide_index=True, width="stretch",
                column_config={
                    "Mapped CFPB complaints": st.column_config.NumberColumn(format="%d"),
                    "HMDA originations": st.column_config.NumberColumn(format="%d"),
                    "Exploratory index per 1,000": st.column_config.NumberColumn(format="%.2f"),
                },
            )

    with detail_panel:
        st.subheader("Selected county")
        try:
            detail = county_detail(data, selected).iloc[0]
        except KeyError:
            st.info("This county is not represented in the dataset. No zero values have been assumed.")
        else:
            st.markdown(f"**{detail[COUNTY_NAME]}**")
            st.caption(f"County FIPS: {detail[COUNTY_ID]}")
            st.metric("Mapped CFPB complaints", f"{int(detail[COMPLAINTS]):,}")
            st.metric("Bank HMDA originations", f"{int(detail[ORIGINATIONS]):,}")
            st.metric("Exploratory cross-source index per 1,000", f"{detail[RATE]:.2f}")
            st.caption(
                f"{int(detail[COMPLAINTS]):,} complaints / "
                f"{int(detail[ORIGINATIONS]):,} originations × 1,000."
            )
            if detail[ORIGINATIONS] < minimum:
                st.info("This county is excluded from the ranking by the minimum-origination filter. Its source detail remains available.")
            elif selected not in set(shown[COUNTY_ID]):
                st.info("This county meets the minimum but is outside the selected top-N ranking. Its source detail remains available.")
            st.caption("A high index based on few originations can be unstable. Read the counts together; this is not a complaint probability.")

    st.divider()
    with st.expander("Methodology, sources and limitations"):
        st.markdown("""
**Decision supported.** Choose represented counties for additional investigation.
These figures cannot establish causation, year-over-year growth, market-entry
attractiveness, or a validated bank risk rate.

**Sources and populations.** CFPB complaints name `JPMORGAN CHASE & CO.`;
HMDA originations are reported by JPMorgan Chase Bank, National Association,
LEI `7H6GLXDRUGQFU57RNE97`, for 2024 California activity with `action_taken == 1`.
Parent-company complaints and bank filings are not verified to cover the same
reporting-entity population. Complaints received in 2024 may concern older loans;
no complaint-to-loan cohort matching has been established.

**Geographic coverage.** Of 68 target complaints, 64 were mapped to counties:
three masked ZIP codes and one complete but unmatched ZIP were excluded from
county counts. The table contains only the 25 counties with a mapped complaint,
not every California county. Absent counties must not be assigned zero complaints.
Of 10,826 statewide HMDA originations in the export, 9,966 fall in these 25 counties.
Both the exclusions and the missing-county selection limit statewide comparisons.

**Geographic approximation.** ZIP codes are mapped through a 2020 Census
ZCTA-to-county crosswalk. If a ZCTA spans counties, the largest-land-area match
is used. This is approximate geography, not address-level geocoding.

**Calculation.** County index = mapped complaints / county originations × 1,000.
The overall index uses summed complaints divided by summed originations; it is
not the average of county indices. Only presentation is rounded to two decimals.
The overall totals and selected detail remain independent of ranking controls.

**Earlier sketch.** The specification's pooled figure uses 64 mapped complaints
and 9,966 represented-county originations (about 6.42 per 1,000). The earlier sketch
used 68 target complaints and 10,826 statewide originations (about 6.28).
These are different population definitions, not a change over time.
""")
        st.markdown("**Input field definitions**")
        st.table({
            "Field": [COUNTY_ID, COUNTY_NAME, COMPLAINTS, ORIGINATIONS, RATE],
            "Meaning": [
                "Unique five-character California county FIPS; leading zero preserved",
                "County name", "Mapped 2024 target CFPB mortgage complaints",
                "2024 target-bank HMDA originations in that county",
                "Stored exploratory cross-source index: 1,000 × complaints / originations",
            ],
        })


if __name__ == "__main__":
    main()

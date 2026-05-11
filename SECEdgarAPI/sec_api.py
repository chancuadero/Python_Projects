import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# =========================================================
# CONFIG
# =========================================================

HEADERS = {
    "User-Agent": "ChanAutomatedSolutions (chancuadero22@gmail.com)"
}

st.set_page_config(
    page_title="Proxy Voting Comparison Tool",
    layout="wide"
)

st.title("📊 Proxy Voting Comparison Tool")

# =========================================================
# LOAD ALL N-PX FILERS
# =========================================================

@st.cache_data(ttl=86400)
def get_npx_filers(years=[2024, 2025]):

    filings = []

    for year in years:

        for quarter in [1, 2, 3, 4]:

            url = (
                f"https://www.sec.gov/Archives/edgar/full-index/"
                f"{year}/QTR{quarter}/master.idx"
            )

            response = requests.get(url, headers=HEADERS)

            if response.status_code != 200:
                continue

            lines = response.text.splitlines()

            start_parsing = False

            for line in lines:

                if line.startswith("-----"):
                    start_parsing = True
                    continue

                if not start_parsing:
                    continue

                parts = line.split("|")

                if len(parts) != 5:
                    continue

                cik, company, form_type, filing_date, filename = parts

                if form_type == "N-PX":

                    filings.append({
                        "CIK": cik.zfill(10),
                        "Company": company
                    })

    df = pd.DataFrame(filings)

    if df.empty:
        return pd.DataFrame()

    # Remove duplicates
    df = df.drop_duplicates(subset=["CIK"])

    # Sort alphabetically
    df = df.sort_values("Company").reset_index(drop=True)

    return df

# =========================================================
# LOAD FILERS
# =========================================================

with st.spinner("Loading all N-PX filers from SEC..."):
    filer_df = get_npx_filers()

if filer_df.empty:
    st.error("Could not load N-PX filers.")
    st.stop()

# =========================================================
# SELECT FUND
# =========================================================

st.subheader("🏢 Select a Fund")

selected_row = st.selectbox(
    "Select a Fund to View",
    options=filer_df.index,
    format_func=lambda x: (
        f"{filer_df.loc[x, 'Company']} "
    )
)

selected_fund_name = filer_df.loc[selected_row, "Company"]
selected_cik = filer_df.loc[selected_row, "CIK"]

st.success(
    f"Selected Fund: {selected_fund_name} "
    f"(CIK: {selected_cik})"
)

# =========================================================
# GET ALL N-PX FILINGS FOR SELECTED FUND
# =========================================================

@st.cache_data(ttl=3600)
def get_all_npx_filings(target_cik):

    base_url = f"https://data.sec.gov/submissions/CIK{target_cik}.json"

    response = requests.get(base_url, headers=HEADERS)

    if response.status_code != 200:
        return pd.DataFrame()

    data = response.json()

    all_filings = []

    # -----------------------------------------------------
    # RECENT FILINGS
    # -----------------------------------------------------

    recent = data.get("filings", {}).get("recent", {})

    if recent and "form" in recent:

        recent_df = pd.DataFrame(recent)

        npx_recent = recent_df[recent_df["form"] == "N-PX"]

        if not npx_recent.empty:
            all_filings.append(npx_recent)

    # -----------------------------------------------------
    # HISTORICAL FILINGS
    # -----------------------------------------------------

    historical_files = data.get("filings", {}).get("files", [])

    for file_info in historical_files:

        hist_name = file_info.get("name")

        if not hist_name:
            continue

        hist_url = f"https://data.sec.gov/submissions/{hist_name}"

        try:

            hist_res = requests.get(hist_url, headers=HEADERS)

            if hist_res.status_code != 200:
                continue

            hist_data = hist_res.json()

            hist_df = pd.DataFrame(hist_data)

            if "form" not in hist_df.columns:
                continue

            npx_hist = hist_df[hist_df["form"] == "N-PX"]

            if not npx_hist.empty:
                all_filings.append(npx_hist)

        except Exception:
            continue

    # -----------------------------------------------------
    # COMBINE RESULTS
    # -----------------------------------------------------

    if all_filings:

        final_df = pd.concat(all_filings, ignore_index=True)

        final_df = final_df.drop_duplicates(
            subset=["accessionNumber"]
        )

        if "filingDate" in final_df.columns:

            final_df = final_df.sort_values(
                by="filingDate",
                ascending=False
            )

        return final_df

    return pd.DataFrame()

# =========================================================
# LOAD FILINGS
# =========================================================

with st.spinner("Loading N-PX filings..."):
    npx_df = get_all_npx_filings(selected_cik)

# =========================================================
# DISPLAY FILINGS
# =========================================================

if not npx_df.empty:

    st.subheader("📁 Available N-PX Filings")

    display_cols = [
        col for col in [
            "accessionNumber",
            "filingDate",
            "reportDate",
            "primaryDocument"
        ]
        if col in npx_df.columns
    ]

    st.dataframe(
        npx_df[display_cols],
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("No N-PX filings found.")
    st.stop()

# =========================================================
# FIND XML FILE
# =========================================================

def find_xml_file(cik, accession_raw, primary_doc):

    acc_no_path = accession_raw.replace("-", "")
    cik_path = str(int(cik))

    base_url = (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_path}/{acc_no_path}/"
    )

    index_url = base_url + "index.json"

    response = requests.get(index_url, headers=HEADERS)

    if response.status_code != 200:
        return primary_doc, base_url + primary_doc

    try:

        files = response.json().get(
            "directory",
            {}
        ).get(
            "item",
            []
        )

        xml_candidates = []

        for f in files:

            name = f.get("name", "")

            if name.lower().endswith(".xml"):
                xml_candidates.append(name)

        # PRIORITY ORDER
        priority_keywords = [
            "vote",
            "proxy",
            "npx",
            "table"
        ]

        for keyword in priority_keywords:

            for file in xml_candidates:

                if keyword in file.lower():
                    return file, base_url + file

        # fallback to first xml
        if xml_candidates:
            return xml_candidates[0], base_url + xml_candidates[0]

    except Exception:
        pass

    return primary_doc, base_url + primary_doc

# =========================================================
# PARSE VOTING DATA
# =========================================================

@st.cache_data(ttl=3600)
def get_voting_data(cik, accession_raw, primary_doc):

    target_filename, final_url = find_xml_file(
        cik,
        accession_raw,
        primary_doc
    )

    response = requests.get(final_url, headers=HEADERS)

    if response.status_code != 200:
        return pd.DataFrame(), final_url

    soup = BeautifulSoup(response.content, "xml")

    votes = []

    # Namespace-agnostic search
    items = soup.find_all(
        lambda tag: tag.name and tag.name.endswith("proxyTable")
    )

    for item in items:

        issuer = item.find(
            lambda tag: tag.name and tag.name.endswith("issuerName")
        )

        agenda = item.find(
            lambda tag: tag.name and (
                tag.name.endswith("voteDescription")
                or tag.name.endswith("votedItemDescription")
            )
        )

        vote = item.find(
            lambda tag: tag.name and tag.name.endswith("howVoted")
        )

# -------------------------------------------------
# MANAGEMENT RECOMMENDATION
# -------------------------------------------------

        status = item.find(
            lambda tag: tag.name and (
                tag.name.endswith("managementRecommendation")
                or tag.name.endswith("voteInstruction")
                )
            )

        meeting_date = item.find(
            lambda tag: tag.name and tag.name.endswith("meetingDate")
        )

        shares_voted = item.find(
            lambda tag: tag.name and tag.name.endswith("sharesVoted")
        )

        vote_record = {
            "Company": issuer.text.strip() if issuer else "N/A",
            "Agenda": agenda.text.strip() if agenda else "N/A",
            "Vote": vote.text.strip() if vote else "N/A",
            "Status": status.text.strip() if status else "N/A",
            "Meeting Date": meeting_date.text.strip() if meeting_date else "N/A",
            "Shares Voted": shares_voted.text.strip() if shares_voted else "N/A"
        }

        votes.append(vote_record)

    votes_df = pd.DataFrame(votes)

    return votes_df, final_url

# =========================================================
# SELECT FILING
# =========================================================

st.subheader("🗳 Extract Voting Data")

selected_filing = st.selectbox(
    "Select a Filing",
    options=npx_df.index,
    format_func=lambda x: (
        f"Filing Date: "
        f"{npx_df.loc[x, 'filingDate']} | "
        f"Accession: "
        f"{npx_df.loc[x, 'accessionNumber']}"
    )
)

acc_no = npx_df.loc[selected_filing, "accessionNumber"]
primary_doc = npx_df.loc[selected_filing, "primaryDocument"]

# =========================================================
# EXTRACT VOTES
# =========================================================

if st.button("🚀 Extract Agenda & Votes"):

    with st.spinner("Extracting voting data from SEC XML filing..."):

        votes_df, source_url = get_voting_data(
            selected_cik,
            acc_no,
            primary_doc
        )

        if not votes_df.empty:

            st.success("Voting data extracted successfully!")

            st.markdown("### Source XML")
            st.code(source_url)

            # -------------------------------------------------
            # SEARCH FILTER
            # -------------------------------------------------

            search_query = st.text_input(
                "🔎 Filter by Company Name"
            )

            filtered_df = votes_df.copy()

            if search_query:

                filtered_df = filtered_df[
                    filtered_df["Company"].str.contains(
                        search_query,
                        case=False,
                        na=False
                    )
                ]

            st.markdown("### Voting Records")

            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )

            # -------------------------------------------------
            # DOWNLOAD CSV
            # -------------------------------------------------

            csv = filtered_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇ Download CSV",
                data=csv,
                file_name=(
                    f"{selected_fund_name}_votes.csv"
                ),
                mime="text/csv"
            )

        else:

            st.warning(
                "Could not find structured voting data "
                "inside this filing."
            )
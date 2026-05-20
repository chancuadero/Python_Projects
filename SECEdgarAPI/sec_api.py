import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px

# =========================================================
# CONFIG
# =========================================================

HEADERS = {
    "User-Agent": "ChanAutomatedSolutions (chancuadero22@gmail.com)"
}

st.set_page_config(
    page_title="Proxy Voting Tool",
    layout="wide"
)

st.title("📊 Proxy Voting Tool")

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
        votes_df, source_url = get_voting_data(selected_cik, acc_no, primary_doc)

        if not votes_df.empty:
            st.success("Voting data extracted successfully!")
            
            # Create two clean tabs at the top of your dashboard
            tab1, tab2 = st.tabs(["📊 Analytics Dashboard", "📋 Raw Data Table"])

            # ==========================================
            # TAB 1: ANALYTICS DASHBOARD
            # ==========================================
            with tab1:
                st.subheader(f"Voting Insights for {selected_fund_name}")
                
                # --- Helper Function to Categorize Agendas ---
                def categorize_agenda(agenda_text):
                    text = str(agenda_text).lower()
                    if "elect" in text or "director" in text or "nominee" in text:
                        return "Board Elections"
                    elif "compensation" in text or "say on pay" in text or "equity plan" in text or "auditor" in text:
                        return "Executive Pay & Governance"
                    elif "shareholder proposal" in text or "climate" in text or "human rights" in text:
                        return "Shareholder & ESG Proposals"
                    else:
                        return "Routine / Other Business"

                # Apply categorization to the DataFrame
                votes_df["Agenda Category"] = votes_df["Agenda"].apply(categorize_agenda)

                # --- KPI Metrics Row ---
                total_votes = len(votes_df)
                for_votes = len(votes_df[votes_df["Status"].str.lower() == "for"])
                against_votes = len(votes_df[votes_df["Status"].str.lower() == "against"])
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Items Voted", f"{total_votes:,}")
                col2.metric("🟢 'FOR' Votes", f"{for_votes:,}", f"{(for_votes/total_votes*100):.1f}%" if total_votes else "0%")
                col3.metric("🔴 'AGAINST' Votes", f"{against_votes:,}", f"-{(against_votes/total_votes*100):.1f}%" if total_votes else "0%", delta_color="inverse")
                
                # Handle Shares Voted calculation safely
                votes_df["Shares Cleaned"] = pd.to_numeric(votes_df["Shares Voted"].str.replace(",", ""), errors="coerce").fillna(0)
                total_shares = votes_df["Shares Cleaned"].sum()
                col4.metric("Total Shares Swung", f"{int(total_shares):,}")

                st.markdown("---")

                # --- Charts Section ---
                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    st.markdown("#### Overall Voting Distribution")
                    # Pie chart showing For vs Against vs Abstain
                    vote_counts = votes_df["Status"].value_counts().reset_index()
                    vote_counts.columns = ["Vote Decision", "Count"]
                    fig_pie = px.pie(
                        vote_counts, 
                        values="Count", 
                        names="Vote Decision",
                        color="Vote Decision",
                        color_discrete_map={"FOR": "#2ecc71", "AGAINST": "#e74c3c", "ABSTAIN": "#f1c40f"},
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                with chart_col2:
                    st.markdown("#### Voting Behavior by Agenda Type")
                    # Grouped Bar Chart: Category vs Vote Type
                    category_votes = votes_df.groupby(["Agenda Category", "Status"]).size().reset_index(name="Count")
                    fig_bar = px.bar(
                        category_votes,
                        x="Agenda Category",
                        y="Count",
                        color="Status",
                        barmode="group",
                        color_discrete_map={"FOR": "#2ecc71", "AGAINST": "#e74c3c", "ABSTAIN": "#f1c40f"},
                        labels={"Count": "Number of Proposals"}
                    )
                    fig_bar.update_layout(xaxis_title=None)
                    st.plotly_chart(fig_bar, use_container_width=True)

            # ==========================================
            # TAB 2: RAW DATA TABLE (Your existing UI)
            # ==========================================
            with tab2:
                st.markdown(f"#### Source XML: `{source_url}`")
                
                search_query = st.text_input("🔎 Filter by Company Name")
                filtered_df = votes_df.copy()

                if search_query:
                    filtered_df = filtered_df[
                        filtered_df["Company"].str.contains(search_query, case=False, na=False)
                    ]

                st.dataframe(
                    filtered_df[["Company", "Agenda", "Vote", "Status", "Meeting Date", "Shares Voted"]],
                    use_container_width=True,
                    hide_index=True
                )

                csv = filtered_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇ Download CSV",
                    data=csv,
                    file_name=f"{selected_fund_name}_votes.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Could not find structured voting data inside this filing.")
import streamlit as st
import pandas as pd
import http.client
import json
import base64
from io import BytesIO

# Set page layout to full width
st.set_page_config(layout="wide")

# Function to get the domain stats for a specific date
def get_domain_stats(domain, api_id, secret_key, month, year, country_code):
    credentials = f"{api_id}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {encoded_credentials}'}

    conn = http.client.HTTPSConnection("www.spyfu.com")
    conn.request("GET", f"/apis/domain_stats_api/v2/getDomainStatsForExactDate?month={month}&year={year}&domain={domain}&countryCode={country_code}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

# Function to extract valuable keywords from SpyFu
def get_valuable_keywords(domain, api_id, secret_key, country_code):
    credentials = f"{api_id}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {encoded_credentials}'}

    conn = http.client.HTTPSConnection("www.spyfu.com")
    conn.request("GET", f"/apis/serp_api/v2/seo/getMostValuableKeywords?query={domain}&sortBy=seoClicks&sortOrder=Descending&startingRow=1&pageSize=11&countryCode={country_code}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

# Function to extract newly ranked keywords from SpyFu
def get_newly_ranked_keywords(domain, api_id, secret_key, country_code):
    credentials = f"{api_id}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {encoded_credentials}'}

    conn = http.client.HTTPSConnection("www.spyfu.com")
    conn.request("GET", f"/apis/serp_api/v2/seo/getNewlyRankedKeywords?query={domain}&sortBy=SeoClicks&sortOrder=Descending&startingRow=1&pageSize=10&countryCode={country_code}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

# Function to extract gained clicks keywords from SpyFu
def get_gained_clicks_keywords(domain, api_id, secret_key, country_code):
    credentials = f"{api_id}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {encoded_credentials}'}

    conn = http.client.HTTPSConnection("www.spyfu.com")
    conn.request("GET", f"/apis/serp_api/v2/seo/getGainedClicksKeywords?query={domain}&sortBy=SearchVolume&sortOrder=Descending&startingRow=1&pageSize=5&countryCode={country_code}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

# Function to handle competitors input from Excel or manual input
def get_competitor_domains():
    competitor_option = st.radio("How would you like to provide competitor domains?", ('Upload Excel File', 'Enter Manually'))
    
    competitor_domains = []

    if competitor_option == 'Upload Excel File':
        uploaded_file = st.file_uploader("Upload Competitor Domains Excel File", type=["xlsx", "xls"], key="competitor_file")
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            competitor_domains = df.iloc[:, 0].tolist()  # Assuming domains are in the first column

    elif competitor_option == 'Enter Manually':
        manual_input = st.text_area("Enter competitor domains (comma-separated)", "")
        if manual_input:
            competitor_domains = [domain.strip() for domain in manual_input.split(",")]

    return competitor_domains

# Function to display KPIs
def display_kpis(stats, domain, backlinks_data=None):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"Organic Rank ({domain})", stats["averageOrganicRank"])
    col2.metric(f"Organic Results ({domain})", stats["totalOrganicResults"])
    col3.metric(f"Organic Clicks ({domain})", stats["monthlyOrganicClicks"])
    
    # Calculate and display backlinks KPI
    if backlinks_data is not None:
        total_backlinks = len(backlinks_data)
        col4.metric(f"Total Backlinks ({domain})", total_backlinks)
    else:
        col4.metric(f"Total Backlinks ({domain})", "N/A")

# Function to display and collect valuable keywords
def display_keywords(keywords_data):
    if keywords_data and "results" in keywords_data:
        keywords_list = []
        for keyword in keywords_data["results"]:
            keywords_list.append({
                "Keyword": keyword.get("keyword"),
                "Search Volume": keyword.get("searchVolume"),
                "SEO Clicks": keyword.get("seoClicks")
            })
        
        df = pd.DataFrame(keywords_list).iloc[1:,:]
        st.dataframe(df, use_container_width=True)  # Display a sortable dataframe with full width
        return df
    else:
        st.write("No valuable keyword data available.")
        return pd.DataFrame()

# Function to display and collect newly ranked keywords
def display_newly_ranked_keywords(new_keywords_data):
    if new_keywords_data and "results" in new_keywords_data:
        newly_ranked_list = []
        for keyword in new_keywords_data["results"]:
            newly_ranked_list.append({
                "Keyword": keyword.get("keyword"),
                "Search Volume": keyword.get("searchVolume"),
                "Rank": keyword.get("rank"),
                "SEO Clicks": keyword.get("seoClicks")
            })
        
        df = pd.DataFrame(newly_ranked_list)
        st.dataframe(df, use_container_width=True)
        return df
    else:
        st.write("No newly ranked keyword data available.")
        return pd.DataFrame()

# Function to display and collect gained clicks keywords
def display_gained_clicks_keywords(gained_keywords_data):
    if gained_keywords_data and "results" in gained_keywords_data:
        gained_clicks_list = []
        for keyword in gained_keywords_data["results"]:
            gained_clicks_list.append({
                "Keyword": keyword.get("keyword"),
                "Rank": keyword.get("rank"),
                "SEO Clicks": keyword.get("seoClicks")
            })
        
        df = pd.DataFrame(gained_clicks_list)
        st.dataframe(df, use_container_width=True)
        return df
    else:
        st.write("No gained clicks keyword data available.")
        return pd.DataFrame()

# Function to handle Excel file upload
def handle_excel_upload(file_type):
    uploaded_file = st.file_uploader(f"Upload {file_type} Excel file", type=["xlsx", "xls"], key=f"{file_type}_file")
    if uploaded_file is not None:
        # Read all sheets into a dictionary of DataFrames
        df_dict = pd.read_excel(uploaded_file, sheet_name=None)  # Read all sheets
        return df_dict
    return None

# Function to display data from a specific sheet
def display_sheet_data(sheet_df, domain_name, data_type):
    if sheet_df is not None:
        st.subheader(f"{data_type} for {domain_name}")
        st.dataframe(sheet_df, use_container_width=True)
        return sheet_df
    else:
        st.write(f"No {data_type.lower()} data available for {domain_name}.")
        return pd.DataFrame()

# Function to create a downloadable Excel file
def create_excel(domains_data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for domain, data_dict in domains_data.items():
            for sheet_name, df in data_dict.items():
                try:
                    sanitized_name = sheet_name+'_'+ domain.split('.')[0]
                    df.to_excel(writer, sheet_name=sanitized_name[:31], index=False)
                except: 
                    break 
    output.seek(0)
    return output

# Streamlit App
def main():
    st.title("Domain KPI and Competitors Dashboard")

    # Input for API ID and Secret Key
    api_id = "356b218d-0d19-412c-83aa-2fafa98384cb"
    secret_key = "J6VPTMMZ"
    domain = st.text_input("Enter the main domain", "lidl.fr")

    # Country Code Selection
    country_codes = ['AR', 'AU', 'BR', 'CA', 'DE', 'ES', 'FR', 'IE', 'IN', 'IT', 'JP', 'MX', 'NL', 'NZ', 'SG', 'UA', 'UK', 'US', 'ZA']
    country_code = st.selectbox("Select Country Code", country_codes, index=6)  # Default to FR

    # Input for competitors
    competitor_domains = get_competitor_domains()

    # Create tabs for SEO and SEA overview
    tab1, tab2 = st.tabs(["SEO Overview", "SEA Overview"])

    # Dictionary to store data for each domain for export
    domains_data = {}

    # SEO Overview Tab
    with tab1:
        # Separate Excel uploads for Backlinks and Top Pages
        st.subheader("Upload Backlinks and Top Pages Excel Files")
        col1, col2 = st.columns(2)
        with col1:
            backlinks_data = handle_excel_upload("Backlinks")
        with col2:
            top_pages_data = handle_excel_upload("Top Pages")

        # Input for month and year selection
        col1, col2 = st.columns(2)
        month = col1.selectbox("Select Month", list(range(1, 13)), index=5)  # Default is June (month 6)
        year = col2.selectbox("Select Year", list(range(2015, 2025)), index=5)  # Default is 2020

        if st.button("Get SEO Data"):
            if api_id and secret_key and domain:
                # Fetch and display data for main domain first
                st.subheader(f"KPIs for {domain}")

                # Dictionary to store the main domain's data for export
                domain_data = {}

                # Fetch and display organic metrics and backlinks KPI for the main domain
                data = get_domain_stats(domain, api_id, secret_key, month, year, country_code)
                if data and "results" in data and data["results"]:
                    stats = data["results"][0]
                    main_backlinks_data = backlinks_data[list(backlinks_data.keys())[0]] if backlinks_data else None
                    display_kpis(stats, domain, main_backlinks_data)

                # Fetch and display most valuable keywords for the main domain
                keywords_data = get_valuable_keywords(domain, api_id, secret_key, country_code)
                st.subheader(f"Most Valuable Keywords for {domain}")
                keywords_df = display_keywords(keywords_data)
                domain_data['Most Valuable Keywords'] = keywords_df

                # Fetch and display newly ranked keywords for the main domain
                new_keywords_data = get_newly_ranked_keywords(domain, api_id, secret_key, country_code)
                st.subheader(f"Newly Ranked Keywords for {domain}")
                newly_ranked_df = display_newly_ranked_keywords(new_keywords_data)
                domain_data['Newly Ranked Keywords'] = newly_ranked_df

                # Fetch and display gained clicks keywords for the main domain
                gained_clicks_keywords_data = get_gained_clicks_keywords(domain, api_id, secret_key, country_code)
                st.subheader(f"Gained Clicks Keywords for {domain}")
                gained_clicks_df = display_gained_clicks_keywords(gained_clicks_keywords_data)
                domain_data['Gained Clicks Keywords'] = gained_clicks_df

                # Display backlinks and top pages for the main domain
                if backlinks_data is not None:
                    main_backlinks_df = display_sheet_data(main_backlinks_data, domain, "Backlinks")
                    domain_data['Backlinks'] = main_backlinks_df
                if top_pages_data is not None:
                    main_top_pages_data = top_pages_data[list(top_pages_data.keys())[0]]  # First sheet is main domain
                    main_top_pages_df = display_sheet_data(main_top_pages_data, domain, "Top Pages")
                    domain_data['Top Pages'] = main_top_pages_df

                # Save the main domain's data to the overall dictionary
                domains_data[domain] = domain_data

                # Loop through competitors
                for idx, competitor in enumerate(competitor_domains):
                    st.subheader(f"KPIs for Competitor {idx + 1}: {competitor}")

                    # Dictionary to store the competitor's data for export
                    competitor_data = {}

                    # Fetch and display organic metrics and backlinks KPI for the competitor
                    competitor_data_api = get_domain_stats(competitor, api_id, secret_key, month, year, country_code)
                    if competitor_data_api and "results" in competitor_data_api and competitor_data_api["results"]:
                        stats = competitor_data_api["results"][0]
                        competitor_backlinks_data = backlinks_data[list(backlinks_data.keys())[idx + 1]] if backlinks_data and len(backlinks_data) > idx + 1 else None
                        display_kpis(stats, competitor, competitor_backlinks_data)

                    # Fetch and display most valuable keywords for the competitor
                    competitor_keywords_data = get_valuable_keywords(competitor, api_id, secret_key, country_code)
                    st.subheader(f"Most Valuable Keywords for Competitor {idx + 1}: {competitor}")
                    competitor_keywords_df = display_keywords(competitor_keywords_data)
                    competitor_data['Most Valuable Keywords'] = competitor_keywords_df

                    # Fetch and display newly ranked keywords for the competitor
                    competitor_new_keywords_data = get_newly_ranked_keywords(competitor, api_id, secret_key, country_code)
                    st.subheader(f"Newly Ranked Keywords for Competitor {idx + 1}: {competitor}")
                    competitor_newly_ranked_df = display_newly_ranked_keywords(competitor_new_keywords_data)
                    competitor_data['Newly Ranked Keywords'] = competitor_newly_ranked_df

                    # Fetch and display gained clicks keywords for the competitor
                    competitor_gained_clicks_keywords_data = get_gained_clicks_keywords(competitor, api_id, secret_key, country_code)
                    st.subheader(f"Gained Clicks Keywords for Competitor {idx + 1}: {competitor}")
                    competitor_gained_clicks_df = display_gained_clicks_keywords(competitor_gained_clicks_keywords_data)
                    competitor_data['Gained Clicks Keywords'] = competitor_gained_clicks_df

                    # Display backlinks and top pages for each competitor
                    if competitor_backlinks_data is not None:
                        competitor_backlinks_df = display_sheet_data(competitor_backlinks_data, competitor, "Backlinks")
                        competitor_data['Backlinks'] = competitor_backlinks_df
                    if top_pages_data is not None and len(top_pages_data) > idx + 1:
                        competitor_top_pages_data = top_pages_data[list(top_pages_data.keys())[idx + 1]]
                        competitor_top_pages_df = display_sheet_data(competitor_top_pages_data, competitor, "Top Pages")
                        competitor_data['Top Pages'] = competitor_top_pages_df

                    # Save the competitor's data to the overall dictionary
                    domains_data[competitor] = competitor_data

    # Allow user to download the data as an Excel file
    if domains_data:
        st.subheader("Download Data as Excel")
        excel_data = create_excel(domains_data)
        st.download_button(label="Download Excel", data=excel_data, file_name="domains_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # SEA Overview Tab (Placeholder for now)
    with tab2:
        st.header("SEA Overview")
        st.write("This section is under construction.")

if __name__ == "__main__":
    main()

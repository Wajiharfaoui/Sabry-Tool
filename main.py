import streamlit as st
import pandas as pd
import http.client
import json
import base64
from io import BytesIO
from datetime import datetime

# Set page layout to full width
st.set_page_config(layout="wide")

# Function to get the domain stats for a specific date (for SEO Overview)
def get_domain_stats(domain, api_id, secret_key, month, year, country_code):
    credentials = f"{api_id}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {encoded_credentials}'}

    conn = http.client.HTTPSConnection("www.spyfu.com")
    conn.request("GET", f"/apis/domain_stats_api/v2/getDomainStatsForExactDate?month={month}&year={year}&domain={domain}&countryCode={country_code}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

# Function to extract most successful PPC keywords
def get_most_successful_ppc_keywords(domain, api_id, secret_key, country_code):
    credentials = f"{api_id}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {encoded_credentials}'}

    conn = http.client.HTTPSConnection("www.spyfu.com")
    conn.request("GET", f"/apis/keyword_api/v2/ppc/getMostSuccessful?query={domain}&excludeDomain=offers.com&sortBy=SearchVolume&sortOrder=Descending&startingRow=1&pageSize=10&countryCode={country_code}&adultFilter=true", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

# Function to extract ad history with metrics
def get_ad_history_with_metrics(domain, api_id, secret_key):
    credentials = f"{api_id}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {encoded_credentials}'}
    conn = http.client.HTTPSConnection("www.spyfu.com")
    conn.request("GET", f"/apis/ad_history_api/domain_ad_history_with_metrics?d={domain}&m=200&countryCode=FR", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

# Function to display ad history data
def display_keyword_data(ad_history_data):
    keyword_list = []
    
    # Check if "keywords" exists and is a list
    if "keywords" in ad_history_data and isinstance(ad_history_data["keywords"], list):
        for keyword_data in ad_history_data["keywords"]:
            keyword = keyword_data.get("keyword", "N/A")
            exact_cpc = keyword_data.get("exact_cpc", "N/A")
            exact_daily_clicks = keyword_data.get("exact_daily_clicks", "N/A")
            
            # Loop through ads associated with each keyword
            ads = keyword_data.get("ads", [])
            for ad in ads:
                ad_title = ad.get("title", "N/A")
                ad_body = ad.get("body", "N/A")
                ad_position = ad.get("position", "N/A")
                search_date_id = ad.get("search_date_id", "N/A")

                # Append all keyword and ad-related info into a list
                keyword_list.append({
                    "Keyword": keyword,
                    "Exact CPC": exact_cpc,
                    "Exact Daily Clicks": exact_daily_clicks,
                    "Ad Title": ad_title,
                    "Ad Body": ad_body,
                    "Ad Position": ad_position,
                    "Search Date ID": datetime.strptime(str(search_date_id), "%Y%m%d").date() if search_date_id != "N/A" else "N/A"
                })

    # Convert the list to a DataFrame and display it
    if keyword_list:
        df = pd.DataFrame(keyword_list)
        st.dataframe(df, use_container_width=True)
        return df  # Return the DataFrame
    else:
        st.write("No keyword data available.")
        return pd.DataFrame()  # Return an empty DataFrame

# Function to display top ads data
def display_top_ads(ad_history_data):
    top_ads_list = []
    
    # Check if "top_ads" exists and is a list
    if "top_ads" in ad_history_data and isinstance(ad_history_data["top_ads"], list):
        for ad in ad_history_data["top_ads"]:
            ad_id = ad.get("ad_id", "N/A")
            title = ad.get("title", "N/A")
            body = ad.get("body", "N/A")
            avg_ad_pos = ad.get("avg_ad_pos", "N/A")
            avg_total_ads = ad.get("avg_total_ads", "N/A")
            coverage = ad.get("coverage", "N/A")

            # Append all ad-related info into a list
            top_ads_list.append({
                "Ad ID": ad_id,
                "Title": title,
                "Body": body,
                "Avg Ad Position": avg_ad_pos,
                "Avg Total Ads": avg_total_ads,
                "Coverage": coverage,
            })

    # Convert the list to a DataFrame and display it
    if top_ads_list:
        df = pd.DataFrame(top_ads_list)
        st.dataframe(df, use_container_width=True)
        return df  # Return the DataFrame
    else:
        st.write("No top ads data available.")
        return pd.DataFrame()  # Return an empty DataFrame

# Function to display PPC keyword data in a table
def display_ppc_keywords(ppc_data):
    if ppc_data and "results" in ppc_data:
        ppc_keywords_list = []
        for keyword in ppc_data["results"]:
            ppc_keywords_list.append({
                "Keyword": keyword.get("keyword"),
                "Search Volume": keyword.get("searchVolume"),
                "Total Monthly Clicks": keyword.get("totalMonthlyClicks"),
                "Percent Paid Clicks": keyword.get("percentPaidClicks"),
                "Broad Monthly Cost": keyword.get("broadMonthlyCost"),
                "Broad Cost Per Click": keyword.get("broadCostPerClick")
            })
        
        df = pd.DataFrame(ppc_keywords_list)
        st.dataframe(df, use_container_width=True)  # Display a sortable dataframe with full width
        return df
    else:
        st.write("No PPC keyword data available.")
        return pd.DataFrame()  # Return an empty DataFrame

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

# Function to display valuable keywords
def display_keywords(keywords_data):
    if keywords_data and "results" in keywords_data:
        keywords_list = []
        for keyword in keywords_data["results"]:
            keywords_list.append({
                "Keyword": keyword.get("keyword"),
                "Search Volume": keyword.get("searchVolume"),
                "SEO Clicks": keyword.get("seoClicks")
            })
        
        df = pd.DataFrame(keywords_list)
        st.dataframe(df, use_container_width=True)  # Display a sortable dataframe with full width
        return df
    else:
        st.write("No valuable keyword data available.")
        return pd.DataFrame()

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

# Function to display newly ranked keywords
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

# Function to display gained clicks keywords
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

# Function to get the SEA stats for a specific date (Paid Keywords, PPC Clicks, PPC Budget)
def get_sea_stats(domain, api_id, secret_key, month, year, country_code):
    credentials = f"{api_id}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {encoded_credentials}'}

    conn = http.client.HTTPSConnection("www.spyfu.com")
    conn.request("GET", f"/apis/domain_stats_api/v2/getDomainStatsForExactDate?month={month}&year={year}&domain={domain}&countryCode={country_code}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

# Function to display KPIs for SEO Overview
def display_kpis(stats, domain, backlinks_data=None):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"Organic Rank ({domain})", stats["averageOrganicRank"])
    col2.metric(f"Organic Results ({domain})", stats["totalOrganicResults"])
    col3.metric(f"Organic Clicks ({domain})", stats["monthlyOrganicClicks"])
    
    if backlinks_data is not None:
        total_backlinks = len(backlinks_data)
        col4.metric(f"Total Backlinks ({domain})", total_backlinks)
    else:
        col4.metric(f"Total Backlinks ({domain})", "N/A")

# Function to display SEA KPIs (Paid Keywords, PPC Clicks, PPC Budget)
def display_sea_kpis(sea_data, domain):
    if sea_data and "results" in sea_data and sea_data["results"]:
        stats = sea_data["results"][0]
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Paid Keywords ({domain})", stats["totalAdsPurchased"])
        col2.metric(f"Est. Monthly PPC Clicks ({domain})", round(stats["monthlyPaidClicks"],2))
        col3.metric(f"Est. Monthly PPC Budget ({domain})", stats["monthlyBudget"])
    else:
        st.write(f"No SEA data available for {domain}")

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

# Function to handle Excel file upload
def handle_excel_upload(file_type):
    uploaded_file = st.file_uploader(f"Upload {file_type} Excel file", type=["xlsx", "xls"], key=f"{file_type}_file")
    if uploaded_file is not None:
        df_dict = pd.read_excel(uploaded_file, sheet_name=None)
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
                if df is not None and not df.empty:  # Only write if DataFrame is not empty
                    sanitized_name = sheet_name + '_' + domain.split('.')[0]
                    df.to_excel(writer, sheet_name=sanitized_name[:31], index=False)
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
    country_code = st.selectbox("Select Country Code", country_codes, index=6, key="country_select")  # Default to FR

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
        month = col1.selectbox("Select Month", list(range(1, 13)), index=5, key="month_select")  # Default is June (month 6)
        year = col2.selectbox("Select Year", list(range(2024, 2025)), index=1, key="year_select")  # Default is 2020

        if st.button("Get SEO Data", key="get_seo_data"):
            if api_id and secret_key and domain:
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
        st.subheader("Download SEO Data as Excel")
        excel_data = create_excel(domains_data)
        st.download_button(label="Download Excel", data=excel_data, file_name="domains_data_seo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # SEA Overview Tab
    with tab2:
        st.subheader("SEA Data")
        col1, col2 = st.columns(2)
        month = col1.selectbox("Select Month", list(range(1, 13)), index=5, key="sea_month_select")
        year = col2.selectbox("Select Year", list(range(2024, 2025)), index=1, key="sea_year_select")

        # Dictionary to store SEA data for each domain
        sea_domains_data = {}

        if st.button("Get SEA Data", key="get_sea_data"):
            if api_id and secret_key and domain:
                st.subheader(f"SEA KPIs for {domain}")

                # Fetch and display SEA data for the main domain
                sea_data = get_sea_stats(domain, api_id, secret_key, month, year, country_code)
                display_sea_kpis(sea_data, domain)

                # Save the main domain's SEA data to the sea_domains_data dictionary
                domain_sea_data = {}

                # Fetch and display most successful PPC keywords for the main domain
                ppc_data = get_most_successful_ppc_keywords(domain, api_id, secret_key, country_code)
                st.subheader(f"Most Successful PPC Keywords for {domain}")
                ppc_df = display_ppc_keywords(ppc_data)
                domain_sea_data['Most Successful PPC Keywords'] = ppc_df

                # Fetch and display ad history with metrics for the main domain
                ad_history_data = get_ad_history_with_metrics(domain, api_id, secret_key)
                st.subheader(f"Google Ads History for {domain}")
                ad_history_df = display_keyword_data(ad_history_data)
                domain_sea_data['Google Ads History'] = ad_history_df

                # Fetch and display top ads for the main domain
                st.subheader(f"Top Ads for {domain}")
                top_ads_df = display_top_ads(ad_history_data)
                domain_sea_data['Top Ads'] = top_ads_df

                # Save the main domain's SEA data to the sea_domains_data dictionary
                sea_domains_data[domain] = domain_sea_data

                # Loop through competitors
                for idx, competitor in enumerate(competitor_domains):
                    st.subheader(f"SEA KPIs for Competitor {idx + 1}: {competitor}")

                    # Dictionary to store the competitor's SEA data
                    competitor_sea_data = {}

                    # Fetch and display SEA data for each competitor
                    competitor_sea_data_api = get_sea_stats(competitor, api_id, secret_key, month, year, country_code)
                    display_sea_kpis(competitor_sea_data_api, competitor)

                    # Fetch and display most successful PPC keywords for each competitor
                    competitor_ppc_data = get_most_successful_ppc_keywords(competitor, api_id, secret_key, country_code)
                    st.subheader(f"Most Successful PPC Keywords for Competitor {idx + 1}: {competitor}")
                    competitor_ppc_df = display_ppc_keywords(competitor_ppc_data)
                    competitor_sea_data['Most Successful PPC Keywords'] = competitor_ppc_df

                    # Fetch and display ad history with metrics for each competitor
                    competitor_ad_history_data = get_ad_history_with_metrics(competitor, api_id, secret_key)
                    st.subheader(f"Google Ads History for Competitor {idx + 1}: {competitor}")
                    competitor_ad_history_df = display_keyword_data(competitor_ad_history_data)
                    competitor_sea_data['Google Ads History'] = competitor_ad_history_df

                    # Fetch and display top ads for each competitor
                    st.subheader(f"Top Ads for Competitor {idx + 1}: {competitor}")
                    competitor_top_ads_df = display_top_ads(competitor_ad_history_data)
                    competitor_sea_data['Top Ads'] = competitor_top_ads_df

                    # Save the competitor's SEA data to the sea_domains_data dictionary
                    sea_domains_data[competitor] = competitor_sea_data

    # Allow user to download SEA data as an Excel file
    if sea_domains_data:
        st.subheader("Download SEA Data as Excel")
        excel_data_sea = create_excel(sea_domains_data)
        st.download_button(label="Download SEA Excel", data=excel_data_sea, file_name="domains_data_sea.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if __name__ == "__main__":
    main()



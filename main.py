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
    
    if "keywords" in ad_history_data and isinstance(ad_history_data["keywords"], list):
        for keyword_data in ad_history_data["keywords"]:
            keyword = keyword_data.get("keyword", "N/A")
            exact_cpc = keyword_data.get("exact_cpc", "N/A")
            exact_daily_clicks = keyword_data.get("exact_daily_clicks", "N/A")
            
            ads = keyword_data.get("ads", [])
            for ad in ads:
                ad_title = ad.get("title", "N/A")
                ad_body = ad.get("body", "N/A")
                ad_position = ad.get("position", "N/A")
                search_date_id = ad.get("search_date_id", "N/A")

                keyword_list.append({
                    "Keyword": keyword,
                    "Exact CPC": exact_cpc,
                    "Exact Daily Clicks": exact_daily_clicks,
                    "Ad Title": ad_title,
                    "Ad Body": ad_body,
                    "Ad Position": ad_position,
                    "Search Date ID": datetime.strptime(str(search_date_id), "%Y%m%d").date()
                })

    if keyword_list:
        df = pd.DataFrame(keyword_list)
        st.dataframe(df, use_container_width=True)
        return df
    else:
        st.write("No data available to display.")
        return pd.DataFrame()

def display_top_ads(ad_history_data):
    top_ads_list = []
    
    if "top_ads" in ad_history_data and isinstance(ad_history_data["top_ads"], list):
        for ad in ad_history_data["top_ads"]:
            ad_id = ad.get("ad_id", "N/A")
            title = ad.get("title", "N/A")
            body = ad.get("body", "N/A")
            avg_ad_pos = ad.get("avg_ad_pos", "N/A")
            avg_total_ads = ad.get("avg_total_ads", "N/A")
            coverage = ad.get("coverage", "N/A")

            top_ads_list.append({
                "Ad ID": ad_id,
                "Title": title,
                "Body": body,
                "Avg Ad Position": avg_ad_pos,
                "Avg Total Ads": avg_total_ads,
                "Coverage": coverage,
            })

    if top_ads_list:
        df = pd.DataFrame(top_ads_list)
        st.dataframe(df, use_container_width=True)
        return df
    else:
        st.write("No top ads data available to display.")
        return pd.DataFrame()

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
        st.dataframe(df, use_container_width=True)
        return df
    else:
        st.write("No PPC keyword data available.")
        return pd.DataFrame()

# Function to create an Excel file for SEA data
def create_excel_sea(domains_data_sea):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for domain, data_dict in domains_data_sea.items():
            for sheet_name, df in data_dict.items():
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

    # Dictionary to store data for each domain for export in SEA
    domains_data_sea = {}

    # SEA Overview Tab
    with tab2:
        st.subheader("SEA Data")
        col1, col2 = st.columns(2)
        month = col1.selectbox("Select Month", list(range(1, 13)), index=5, key="sea_month_select")
        year = col2.selectbox("Select Year", list(range(2015, 2025)), index=5, key="sea_year_select")

        if st.button("Get SEA Data", key="get_sea_data"):
            if api_id and secret_key and domain:
                st.subheader(f"SEA KPIs for {domain}")

                # Dictionary to store the main domain's SEA data for export
                domain_data_sea = {}

                # Fetch and display SEA data for the main domain
                sea_data = get_sea_stats(domain, api_id, secret_key, month, year, country_code)
                display_sea_kpis(sea_data, domain)

                # Fetch and display most successful PPC keywords for the main domain
                ppc_data = get_most_successful_ppc_keywords(domain, api_id, secret_key, country_code)
                st.subheader(f"Most Successful PPC Keywords for {domain}")
                ppc_df = display_ppc_keywords(ppc_data)
                domain_data_sea['Most Successful PPC Keywords'] = ppc_df

                # Fetch and display ad history with metrics for the main domain
                ad_history_data = get_ad_history_with_metrics(domain, api_id, secret_key)
                st.subheader(f"Google Ads History for domain {domain}")
                ad_history_df = display_keyword_data(ad_history_data)
                domain_data_sea['Ad History'] = ad_history_df

                st.subheader(f"Top Ads for {domain}")
                top_ads_df = display_top_ads(ad_history_data)
                domain_data_data_sea['Top Ads'] = top_ads_df

                # Save the main domain's SEA data to the overall dictionary
                domains_data_sea[domain] = domain_data_sea

                # Loop through competitors
                for idx, competitor in enumerate(competitor_domains):
                    st.subheader(f"SEA KPIs for Competitor {idx + 1}: {competitor}")

                    # Dictionary to store each competitor's SEA data for export
                    competitor_data_sea = {}

                    # Fetch and display SEA data for each competitor
                    competitor_sea_data = get_sea_stats(competitor, api_id, secret_key, month, year, country_code)
                    display_sea_kpis(competitor_sea_data, competitor)

                    # Fetch and display most successful PPC keywords for each competitor
                    competitor_ppc_data = get_most_successful_ppc_keywords(competitor, api_id, secret_key, country_code)
                    st.subheader(f"Most Successful PPC Keywords for Competitor {idx + 1}: {competitor}")
                    competitor_ppc_df = display_ppc_keywords(competitor_ppc_data)
                    competitor_data_sea['Most Successful PPC Keywords'] = competitor_ppc_df

                    # Fetch and display ad history with metrics for each competitor
                    competitor_ad_history_data = get_ad_history_with_metrics(competitor, api_id, secret_key)
                    st.subheader(f"Google Ads History for Competitor {idx + 1}: {competitor}")
                    competitor_ad_history_df = display_keyword_data(competitor_ad_history_data)
                    competitor_data_sea['Ad History'] = competitor_ad_history_df

                    st.subheader(f"Top Ads for Competitor {idx + 1}: {competitor}")
                    competitor_top_ads_df = display_top_ads(competitor_ad_history_data)
                    competitor_data_sea['Top Ads'] = competitor_top_ads_df

                    # Save the competitor's SEA data to the overall dictionary
                    domains_data_sea[competitor] = competitor_data_sea

    # Allow user to download the SEA data as an Excel file
    if domains_data_sea:
        st.subheader("Download SEA Data as Excel")
        excel_data_sea = create_excel_sea(domains_data_sea)
        st.download_button(label="Download SEA Excel", data=excel_data_sea, file_name="sea_domains_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Helper function to handle competitor input
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

if __name__ == "__main__":
    main()


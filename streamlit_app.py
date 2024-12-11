# Install necessary libraries
!pip install pandas requests streamlit plotly

import pandas as pd
import requests
import streamlit as st
import os
import plotly.express as px

# Define the CSV file name
csv_file = "dashboard_data.csv"

# Function to fetch data from BLS API without a key
def fetch_bls_data(series_id, start_year, end_year):
    url = f"https://api.bls.gov/publicAPI/v1/timeseries/data/{series_id}?startyear={start_year}&endyear={end_year}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "Results" in data and "series" in data["Results"]:
            return data["Results"]["series"][0]["data"]
        else:
            print("Error in data format", data)
            return []
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

# Function to process fetched BLS data
def process_bls_data(data):
    df = pd.DataFrame(data)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["date"] = pd.to_datetime(
        df["year"].astype(str) + "-" + df["period"].str[1:], errors="coerce", format="%Y-%m"
    )
    df = df.sort_values(by="date")
    df.set_index("date", inplace=True)
    return df[["value"]]

# Check if the CSV file exists
if os.path.exists(csv_file):
    print("Loading data from CSV file...")
    combined_data = pd.read_csv(csv_file, index_col=0, parse_dates=True)
else:
    print("Fetching data from BLS API...")

    # Define series and date range
    series_ids = {
        "Non-Farm Payrolls": "CES0000000001",
        "Unemployment Rate": "LNS14000000",
        "Total Private Avg Hourly Earnings": "CES0500000003",
        "Civilian Labor Force": "LNS11000000"
    }
    start_year = "2022"
    end_year = "2023"

    # Fetch and process each series
    series_dataframes = {}
    for series_name, series_id in series_ids.items():
        raw_data = fetch_bls_data(series_id, start_year, end_year)
        if raw_data:
            series_dataframes[series_name] = process_bls_data(raw_data)

    # Combine all series into a single DataFrame
    if series_dataframes:
        combined_data = pd.concat(
            {name: df["value"] for name, df in series_dataframes.items()},
            axis=1
        )
        combined_data.to_csv(csv_file)
        print(f"Data successfully fetched and saved to {csv_file}")
    else:
        print("Failed to fetch data from API.")
        combined_data = pd.DataFrame()  # Empty DataFrame as fallback

# Ensure data is sorted and properly formatted
combined_data = combined_data.sort_index()

# Streamlit App
# Dashboard Title
st.title("📊 Labor Statistics Dashboard")
st.write("An interactive dashboard visualizing key U.S. labor statistics from 2022 to 2023.")

if not combined_data.empty:
    # Plot Non-Farm Payrolls
    st.subheader("Non-Farm Payrolls Over Time")
    fig1 = px.line(
        combined_data,
        y="Non-Farm Payrolls",
        title="📈 Non-Farm Payrolls",
        labels={"date": "Date", "Non-Farm Payrolls": "Employment (in Thousands)"},
        template="plotly_white",
    )
    fig1.update_traces(line=dict(color="blue", width=3), hoverinfo="y+x")
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

    # Plot Unemployment Rate
    st.subheader("Unemployment Rate Over Time")
    fig2 = px.line(
        combined_data,
        y="Unemployment Rate",
        title="📉 Unemployment Rate",
        labels={"date": "Date", "Unemployment Rate": "Rate (%)"},
        template="plotly_white",
    )
    fig2.update_traces(line=dict(color="green", width=3), hoverinfo="y+x")
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    # Plot Average Hourly Earnings
    st.subheader("Total Private Average Hourly Earnings")
    fig3 = px.line(
        combined_data,
        y="Total Private Avg Hourly Earnings",
        title="💵 Average Hourly Earnings",
        labels={"date": "Date", "Total Private Avg Hourly Earnings": "Earnings ($)"},
        template="plotly_white",
    )
    fig3.update_traces(line=dict(color="purple", width=3), hoverinfo="y+x")
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # Plot Civilian Labor Force
    st.subheader("Civilian Labor Force Over Time")
    fig4 = px.line(
        combined_data,
        y="Civilian Labor Force",
        title="👥 Civilian Labor Force",
        labels={"date": "Date", "Civilian Labor Force": "Labor Force (in Thousands)"},
        template="plotly_white",
    )
    fig4.update_traces(line=dict(color="orange", width=3), hoverinfo="y+x")
    fig4.update_layout(showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.error("No data available to display.")

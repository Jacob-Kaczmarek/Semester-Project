import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
# Install necessary libraries
!pip install pandas requests streamlit

# Import libraries
import pandas as pd
import requests
import os

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

# Process fetched data
def process_bls_data(data):
    df = pd.DataFrame(data)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["period"] = df["periodName"] + " " + df["year"].astype(str)
    df = df.sort_values(by=["year", "period"])
    df.set_index("period", inplace=True)
    return df[["value"]]

# Example: Fetch Non-Farm Payrolls, Unemployment Rates, Average Hourly Earnings, and Civilian Labor Force
nonfarm_series = "CES0000000001"  # Total Nonfarm Employment  # Non-Farm Payrolls
unemployment_series = "LNS14000000"  # Unemployment Rate
hourly_earnings_series = "CES0500000003"  # Total Private Average Hourly Earnings
labor_force_series = "LNS11000000"  # Civilian Labor Force (Seasonally Adjusted)
start_year = "2022"
end_year = "2023"

nonfarm_data = fetch_bls_data(nonfarm_series, start_year, end_year)
unemployment_data = fetch_bls_data(unemployment_series, start_year, end_year)
hourly_earnings_data = fetch_bls_data(hourly_earnings_series, start_year, end_year)
labor_force_data = fetch_bls_data(labor_force_series, start_year, end_year)

if nonfarm_data and unemployment_data and hourly_earnings_data and labor_force_data:
    nonfarm_df = process_bls_data(nonfarm_data)
    unemployment_df = process_bls_data(unemployment_data)

    hourly_earnings_df = process_bls_data(hourly_earnings_data)
    labor_force_df = process_bls_data(labor_force_data)

    # Combine DataFrames
    dashboard_data = pd.concat({
        "Non-Farm Payrolls": nonfarm_df["value"],
        "Unemployment Rate": unemployment_df["value"],
        "Total Private Avg Hourly Earnings": hourly_earnings_df["value"],
        "Civilian Labor Force": labor_force_df["value"]
    }, axis=1)

    # Save Data to CSV
    dashboard_data.to_csv("dashboard_data.csv")

    print("Data saved as dashboard_data.csv")
else:
    print("Failed to fetch data.")

import streamlit as st
import plotly.express as px

def load_data():
    return pd.read_csv("dashboard_data.csv", index_col=0)

data = load_data()

# Dashboard Title
st.title("Labor Statistics Dashboard")
st.write("Interactive dashboard with labor statistics data.")

# Display data
st.subheader("Data Table")
st.dataframe(data)

# Plot data
st.subheader("Non-Farm Payrolls Over Time")
fig1 = px.line(data, y="Non-Farm Payrolls", title="Non-Farm Payrolls")
st.plotly_chart(fig1)

st.subheader("Unemployment Rate Over Time")
fig2 = px.line(data, y="Unemployment Rate", title="Unemployment Rate")
st.plotly_chart(fig2)

st.subheader("Total Private Average Hourly Earnings")
fig3 = px.line(data, y="Total Private Avg Hourly Earnings", title="Hourly Earnings")
st.plotly_chart(fig3)

st.subheader("Civilian Labor Force")
fig4 = px.line(data, y="Civilian Labor Force", title="Civilian Labor Force")
st.plotly_chart(fig4)

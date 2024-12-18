

import pandas as pd
import requests
import os
from datetime import datetime

# Define the file and BLS series
csv_file = "bls_dataframe.csv"
series_ids = {
    "Non-Farm Payrolls": "CES0000000001",
    "Unemployment Rate": "LNS14000000",
    "Total Private Avg Hourly Earnings": "CES0500000003",
    "Civilian Labor Force": "LNS11000000",
}
current_year = datetime.now().year

def fetch_bls_data(series_id, start_year, end_year):
    url = f"https://api.bls.gov/publicAPI/v1/timeseries/data/{series_id}?startyear={start_year}&endyear={end_year}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "Results" in data and "series" in data["Results"]:
            return data["Results"]["series"][0]["data"]
    return []

def process_bls_data(raw_data):
    df = pd.DataFrame(raw_data)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["date"] = pd.to_datetime(
        df["year"].astype(str) + "-" + df["period"].str[1:], errors="coerce", format="%Y-%m"
    )
    df.set_index("date", inplace=True)
    return df[["value"]]

# Fetch and process all series
series_dataframes = {}
for series_name, series_id in series_ids.items():
    raw_data = fetch_bls_data(series_id, current_year - 1, current_year)
    if raw_data:
        series_dataframes[series_name] = process_bls_data(raw_data)

# Combine all series into a single DataFrame
if series_dataframes:
    combined_data = pd.concat(
        {name: df["value"] for name, df in series_dataframes.items()},
        axis=1
    )
else:
    combined_data = pd.DataFrame()  # Create an empty DataFrame as fallback

# Always overwrite the file
combined_data.to_csv(csv_file)
print(f"Data successfully replaced in {csv_file}.")

import pandas as pd
import os
from ortools.linear_solver import pywraplp
import warnings

from arbitrage_loop_nem import spread, calculate_arbitrage_revenue, dt, time_interval_mins

# Suppress warnings
warnings.filterwarnings("ignore")

# Get the folder containing the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder paths relative to the script's directory
input_folder = os.path.join(script_dir, "input_data")
results_folder = os.path.join(script_dir, "results")
os.makedirs(results_folder, exist_ok=True)

# Loop information
files = ['NEM'] # loop through these files within input_folder
region_select = ['NSW1']  # loop through these regions within the data or all if None
years_mode = ""  # Set to 'auto' to use all years in the data (will loop through)
select_years = list(range(2024, 2027))  # Specify the range of years to process
hours_list = list(range (1, 4)) # (1,12)) # hours of storage duration to loop through

# Format of input price data
datetime_col = "SETTLEMENTDATE" # the column heading containing time data
datetime_format = "%Y-%m-%d %H:%M:%S" # the format of the time data
price_col = "RRP" # the column for price data

# Cost €/MW values for each hour
cost_per_mw = {
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 0,
    9: 0,
    10: 0,
    11: 0,
    12: 0,
    13: 0,
    14: 0,
    15: 0,
    16: 0
}

# Central results list
central_results = []

# Main loop
for file in files:
    all_df = pd.read_csv(os.path.join(input_folder, file + ".csv"))
    all_df.rename(columns={datetime_col: 'datetime', price_col: 'price'}, inplace=True)
    all_df['datetime'] = pd.to_datetime(all_df['datetime'], format=datetime_format)
    regions = region_select if region_select else all_df['REGIONID'].unique()

    for region in regions:
        print(f"Processing region: {region}")
        df = all_df[['datetime', 'price', 'REGIONID']].copy()
        df = df[df['REGIONID'] == region]

        if years_mode == 'auto':
            years = sorted(df['datetime'].dt.year.unique().tolist())
        else:
            years = select_years

        for hours in hours_list:
            print(f"hours list is {hours_list}")
            print(f"Processing {region} for {hours} hours...")

            for year in years:
                for quarter in [1, 2, 3, 4]:
                    quarterly_df = df[
                        (df['datetime'].dt.year == year) &
                        (df['datetime'].dt.quarter == quarter)
                    ]

                    if quarterly_df.empty:
                        print(f"No data for {year} Q{quarter} in {file}.")
                        continue

                    print(f"Processing {region}, {year} Q{quarter}, {hours} hours...")

                    # Calculate spread for the specific quarter and hours
                    daily_spread = spread(quarterly_df, hours)

                    results, total_profit, cycles, avg_sell_price, avg_buy_price = calculate_arbitrage_revenue(
                        quarterly_df,
                        hours
                    )

                    if results is not None:
                        """Use the line below to save operational data for an optimisation run"""
                        # results.to_csv(os.path.join(results_folder, f"{file}_{year}_Q{quarter}_{hours}_arbitrage_results.csv"))

                        central_results.append({
                            "Region": region,
                            "Year": year,
                            "Quarter": f"Q{quarter}",
                            "System duration (hrs)": hours,
                            "daily_spread_avg": round(daily_spread['daily_spread'].mean(), 2),
                            "Total arbitrage profit ($/MW/yr)": 4 * round(total_profit, 2),
                            "Cycles (full cycle equivalents)": round(cycles, 2),
                            "Avg sell price ($/MWh)": round(avg_sell_price, 2),
                            "Avg purchase price ($/MWh)": round(-avg_buy_price, 2),
                            "Cost €/MW": round(cost_per_mw.get(hours, 0), 2)
                        })

# Save central results to a CSV
central_results_df = pd.DataFrame(central_results)
central_results_df.to_csv(os.path.join(results_folder, "arbitrage_results_nem_split.csv"), index=False)

print("Processing complete.")
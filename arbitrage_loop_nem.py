import pandas as pd
import os
from ortools.linear_solver import pywraplp
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Get the folder containing the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder paths relative to the script's directory
input_folder = os.path.join(script_dir, "input_data")
results_folder = os.path.join(script_dir, "results")
os.makedirs(results_folder, exist_ok=True)

# Time interval of input data
time_interval_mins = 5
dt = time_interval_mins / 60  # hours per timestep

# Parameters for storage
rte = 0.95  # Round-trip efficiency
max_charge_rate = 1  # MW
max_discharge_rate = 1 # MW
hrs = 4  # hours of storage duration
battery_capacity = max_discharge_rate * hrs  # MWh energy capacity
initial_soc = 0  # Initial state-of-charge (proportion of energy capacity)
min_soc = 0  # Minimum SOC (proportion of energy capacity)
max_soc = 1  # Maximum SOC (proportion of energy capacity)

# Loop information
files = ['NEM'] # loop through these files within input_folder
region = 'NSW1'
years_mode = ""  # Set to 'auto' to use all years in the data (will loop through)
select_years = list(range(2024, 2027))  # Specify the range of years to process
hours_list = list(range(1,12)) # hours of storage duration to loop through

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

# Helper functions
def spread(df, hrs):
    df = df.copy()
    df['date'] = pd.to_datetime(df['datetime']).dt.date

    # Convert storage duration in hours into number of data intervals
    intervals = int(round(hrs / dt))

    top_hours = df.groupby('date', group_keys=False).apply(
        lambda x: x.nlargest(intervals, 'price')
    ).reset_index(drop=True)

    bottom_hours = df.groupby('date', group_keys=False).apply(
        lambda x: x.nsmallest(intervals, 'price')
    ).reset_index(drop=True)

    top_avg = top_hours.groupby('date')['price'].mean()
    bottom_avg = bottom_hours.groupby('date')['price'].mean()

    daily_spread = pd.DataFrame({
        'date': top_avg.index,
        'top_avg': top_avg.values,
        'bottom_avg': bottom_avg.values
    })

    daily_spread['daily_spread'] = daily_spread['top_avg'] - daily_spread['bottom_avg']

    return daily_spread

def calculate_arbitrage_revenue(df, hrs):
    battery_capacity = max_discharge_rate * hrs  # MWh
    time_steps = len(df)
    solver = pywraplp.Solver.CreateSolver("CBC")
    inf = solver.infinity()

    charge = [solver.NumVar(0, max_charge_rate, f"charge_{t}") for t in range(time_steps)]  # MW
    discharge = [solver.NumVar(0, max_discharge_rate, f"discharge_{t}") for t in range(time_steps)]  # MW
    soc = [solver.NumVar(min_soc, max_soc, f"soc_{t}") for t in range(time_steps)]

    for t in range(time_steps):
        if t == 0:
            solver.Add(
                soc[t] == initial_soc
                + ((charge[t] * dt) / battery_capacity) * rte
                - ((discharge[t] * dt) / battery_capacity)
            )
        else:
            solver.Add(
                soc[t] == soc[t - 1]
                + ((charge[t] * dt) / battery_capacity) * rte
                - ((discharge[t] * dt) / battery_capacity)
            )

    objective = solver.Objective()

    for t in range(time_steps):
        objective.SetCoefficient(discharge[t], df.iloc[t]['price'] * dt)
        objective.SetCoefficient(charge[t], -df.iloc[t]['price'] * dt)

    objective.SetMaximization()

    status = solver.Solve()

    if status == solver.OPTIMAL:
        results = pd.DataFrame({
            "charge": [charge[t].solution_value() for t in range(time_steps)],  # MW
            "discharge": [discharge[t].solution_value() for t in range(time_steps)],  # MW
            "soc": [soc[t].solution_value() for t in range(time_steps)],
            "price": df['price'].values
        }, index=df.index)

        # Convert MW dispatch into MWh per 5-minute interval
        results['charge_mwh'] = results['charge'] * dt
        results['discharge_mwh'] = results['discharge'] * dt

        results['revenue'] = results['discharge_mwh'] * results['price']
        results['cost'] = -results['charge_mwh'] * results['price']
        results['profit'] = results['revenue'] + results['cost']

        total_profit = results['profit'].sum()
        total_discharge = results['discharge_mwh'].sum()
        total_charge = results['charge_mwh'].sum()

        cycles = total_discharge / battery_capacity if battery_capacity > 0 else 0
        avg_sell_price = results['revenue'].sum() / total_discharge if total_discharge > 0 else 0
        avg_buy_price = results['cost'].sum() / total_charge if total_charge > 0 else 0

        print(f"Total Arbitrage Profit {year}: {total_profit:.2f} AUD")

        return results, total_profit, cycles, avg_sell_price, avg_buy_price

    else:
        print(f"No optimal solution found for {file} in {year}.")
        return None, 0, 0, 0, 0

# Main loop
for file in files:
    all_df = pd.read_csv(os.path.join(input_folder, file + ".csv"))
    all_df.rename(columns={datetime_col: 'datetime', price_col: 'price'}, inplace=True)
    all_df['datetime'] = pd.to_datetime(all_df['datetime'], format=datetime_format)
    for region in all_df['REGIONID'].unique():
        df = all_df[['datetime', 'price', 'REGIONID']].copy()
        df = df[df['REGIONID'] == region]  # Filter for NEM region if needed

        if years_mode == 'auto':
            years = sorted(df['datetime'].dt.year.unique().tolist())
        else:
            years = select_years

        for hours in hours_list:
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
central_results_df.to_csv(os.path.join(results_folder, "arbitrage_results_nem.csv"), index=False)

print("Processing complete.")
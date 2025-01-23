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

# Parameters for storage
rte = 0.8  # Round-trip efficiency
max_charge_rate = 1  # MW
max_discharge_rate = 1 # MW
hrs = 4  # hours of storage duration
battery_capacity = max_discharge_rate * hrs  # MWh energy capacity
initial_soc = 0.5  # Initial state-of-charge (proportion of energy capacity)
min_soc = 0  # Minimum SOC (proportion of energy capacity)
max_soc = 1  # Maximum SOC (proportion of energy capacity)

# Loop information
files = ['Poland', 'United Kingdom'] # loop through these files within input_folder
years_mode = ""  # Set to 'auto' to use all years in the data (will loop through)
select_years = list(range(2023, 2025))  # Specify the range of years to process
rte_list = [x/100 for x in range(75,86)]

# Format of input price data
datetime_col = "Datetime (Local)" # the column heading containing time data
datetime_format = "%Y-%m-%d %H:%M:%S" # the format of the time data
price_col = "Price (EUR/MWhe)" # the column for price data

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
def spread(df, rte):
    df['date'] = pd.to_datetime(df['datetime']).dt.date
    top_hours = df.groupby('date', group_keys=False).apply(lambda x: x.nlargest(hrs, 'price')).reset_index(drop=True)
    bottom_hours = df.groupby('date', group_keys=False).apply(lambda x: x.nsmallest(hrs, 'price')).reset_index(drop=True)

    top_avg = top_hours.groupby('date')['price'].mean()
    bottom_avg = bottom_hours.groupby('date')['price'].mean()

    daily_spread = pd.DataFrame({
        'date': top_avg.index,
        'top_avg': top_avg.values,
        'bottom_avg': bottom_avg.values
    })
    daily_spread['daily_spread'] = daily_spread['top_avg'] - daily_spread['bottom_avg']
    return daily_spread

def calculate_arbitrage_revenue(df, rte):
    battery_capacity = max_discharge_rate * hrs
    time_steps = len(df)
    solver = pywraplp.Solver.CreateSolver("CBC")
    inf = solver.infinity()

    charge = [solver.NumVar(0, max_charge_rate, f"charge_{t}") for t in range(time_steps)]
    discharge = [solver.NumVar(0, max_discharge_rate, f"discharge_{t}") for t in range(time_steps)]
    soc = [solver.NumVar(min_soc, max_soc, f"soc_{t}") for t in range(time_steps)]

    for t in range(time_steps):
        if t == 0:
            solver.Add(
                soc[t] == initial_soc + (charge[t] / battery_capacity) * rte - (discharge[t] / battery_capacity)
            )
        else:
            solver.Add(
                soc[t] == soc[t - 1] + (charge[t] / battery_capacity) * rte - (discharge[t] / battery_capacity)
            )

    objective = solver.Objective()
    for t in range(time_steps):
        objective.SetCoefficient(discharge[t], df.iloc[t]['price'])
        objective.SetCoefficient(charge[t], -df.iloc[t]['price'])
    objective.SetMaximization()

    status = solver.Solve()

    if status == solver.OPTIMAL:
        results = pd.DataFrame({
            "charge": [charge[t].solution_value() for t in range(time_steps)],
            "discharge": [discharge[t].solution_value() for t in range(time_steps)],
            "soc": [soc[t].solution_value() for t in range(time_steps)],
            "price": df['price'].values
        }, index=df.index)

        results['revenue'] = results['discharge'] * results['price']
        results['cost'] = -results['charge'] * results['price']
        results['profit'] = results['revenue'] + results['cost']

        total_profit = results['profit'].sum() # £
        total_discharge = results['discharge'].sum() # MWh
        total_charge = results['charge'].sum() # MWh

        cycles = total_discharge / battery_capacity if battery_capacity > 0 else 0
        avg_sell_price = results['revenue'].sum() / total_discharge if total_discharge > 0 else 0
        avg_buy_price = results['cost'].sum() / total_charge if total_charge > 0 else 0

        print(f"Total Arbitrage Profit {year}: {total_profit:.2f} EUR")

        return results, total_profit, cycles, avg_sell_price, avg_buy_price
    else:
        print(f"No optimal solution found for {file} in {year}.")
        return None, 0, 0, 0, 0

# Main loop
for file in files:
    df = pd.read_csv(os.path.join(input_folder, file + ".csv"))
    df.rename(columns={datetime_col: 'datetime', price_col: 'price'}, inplace=True)
    df['datetime'] = pd.to_datetime(df['datetime'], format=datetime_format)
    df = df[['datetime', 'price']]

    if years_mode == 'auto':
        years = df['datetime'].dt.year.unique().tolist()
    else:
        years = select_years

    for efficiency in rte_list:
        print(f"Processing {file} for {efficiency} % RTE...")

        for year in years:
            yearly_df = df[df['datetime'].dt.year == year]
            if yearly_df.empty:
                print(f"No data for {year} in {file}.")
                continue

            # Calculate spread for the specific year and hours
            daily_spread = spread(yearly_df, efficiency)
            results, total_profit, cycles, avg_sell_price, avg_buy_price = calculate_arbitrage_revenue(yearly_df, efficiency)
            if results is not None:
                """Use the line below to save operational (hour by hour) data for an optimisation run"""
               # results.to_csv(os.path.join(results_folder, f"{file}_{year}_{hours}_arbitrage_results.csv")) 

                central_results.append({
                    "Country": file,
                    "Year": year,
                    "System duration (hrs)": hrs,
                    "RTE": efficiency,
                    "daily_spread_avg": round(daily_spread['daily_spread'].mean(), 2),
                    "Total arbitrage profit": round(total_profit, 2),
                    "Cycles (full cycle equivalents)": round(cycles, 2),
                    "Avg sell price (/MWh)": round(avg_sell_price, 2),
                    "Avg purchase price (/MWh)": round(-avg_buy_price, 2),
                    "Cost €/MW": round(cost_per_mw.get(hrs, 0), 2)
                })

# Save central results to a CSV
central_results_df = pd.DataFrame(central_results)
central_results_df.to_csv(os.path.join(results_folder, "arbitrage_results_efficiency.csv"), index=False)

print("Processing complete.")
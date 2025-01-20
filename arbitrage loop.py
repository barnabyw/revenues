import pandas as pd
import os
from ortools.linear_solver import pywraplp
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

# Folder paths
input_folder = "/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Data bank/Market Data/Europe 17.01.25/"
results_folder = "/Users/barnabywinser/Documents/poland revenues/"

# Parameters
files = ['Poland', 'United Kingdom']
datetime_col = "Datetime (Local)"
price_col = "Price (EUR/MWhe)"
datetime_format = "%Y-%m-%d %H:%M:%S"
hours_list = list(range(1,17))
rte = 0.8  # Round-trip efficiency
max_charge_rate = 1  # MW
max_discharge_rate = 1  # MW
hrs = 4  # hours
battery_capacity = max_discharge_rate * hrs  # MWh
initial_soc = 0.5  # Initial state-of-charge
min_soc = 0  # Minimum SOC
max_soc = 1  # Maximum SOC
years_mode = ""  # Set to 'auto' to use all years in the data
select_years = list(range(2019, 2025))  # Specify the range of years to process

# Cost €/MW values for each hour
cost_per_mw = {
    1: 1550000,
    2: 1732000,
    3: 1891000,
    4: 2039000,
    5: 2180000,
    6: 2315000,
    7: 2447000,
    8: 2575000,
    9: 2701000,
    10: 2825000
}

# Central results list
central_results = []

# Helper functions
def spread(df, hrs):
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

def calculate_arbitrage_revenue(df, hrs):
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
        print("No optimal solution found.")
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

    for hours in hours_list:
        print(f"Processing {file} for {hours} hours...")

        for year in years:
            yearly_df = df[df['datetime'].dt.year == year]
            if yearly_df.empty:
                print(f"No data for {year} in {file}.")
                continue

            # Calculate spread for the specific year and hours
            daily_spread = spread(yearly_df, hours)
            results, total_profit, cycles, avg_sell_price, avg_buy_price = calculate_arbitrage_revenue(yearly_df, hours)
            if results is not None:
                results.to_csv(os.path.join(results_folder, f"{file}_{year}_{hours}_arbitrage_results.csv"))

                central_results.append({
                    "country": file,
                    "year": year,
                    "hours": hours,
                    "daily_spread_avg": daily_spread['daily_spread'].mean(),
                    "total_arbitrage_profit": total_profit,
                    "cycles": cycles,
                    "avg_sell_price": avg_sell_price,
                    "avg_buy_price": avg_buy_price,
                    "Cost €/MW": cost_per_mw.get(hours, 0)
                })

# Save central results to a CSV
central_results_df = pd.DataFrame(central_results)
central_results_df.to_csv(os.path.join(results_folder, "central_results_2.csv"), index=False)

print("Processing complete.")

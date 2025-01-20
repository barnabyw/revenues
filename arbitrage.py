import pandas as pd
from ortools.linear_solver import pywraplp

#folders
input_folder = "/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Data bank/Market Data/Europe 21.09/"
results_folder = "/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Arbitrage/Arbitrage revenues/"
#column names and formats
datetime_col = "Datetime (Local)"
price_col = "Price (EUR/MWhe)"
datetime_format = "%d/%m/%Y %H:%M"
file_name = "UK.csv"

# Inputs
rte = 0.8  # Round-trip efficiency
max_charge_rate = 5  # MW
max_discharge_rate = 5  # MW
duration = 4  # hours
battery_capacity = max_discharge_rate * duration  # MWh
initial_soc = 0.5  # Initial state-of-charge (percentage)
min_soc = 0.1  # Minimum SOC (percentage)
max_soc = 0.9  # Maximum SOC (percentage)

# Load Market Data
marketDF = pd.read_csv(input_folder+file_name)
marketDF["Datetime"] = pd.to_datetime(marketDF[datetime_col], format=datetime_format)
marketDF = marketDF.set_index("Datetime")
marketDF = marketDF[[price_col]].rename(columns={"Price (EUR/MWhe)": "price"})

# Define time steps
time_steps = len(marketDF)
dt = 1  # Assume hourly time intervals

# Solver
solver = pywraplp.Solver.CreateSolver("CBC")
inf = solver.infinity()

# Decision variables
charge = [solver.NumVar(0, max_charge_rate, f"charge_{t}") for t in range(time_steps)]
discharge = [solver.NumVar(0, max_discharge_rate, f"discharge_{t}") for t in range(time_steps)]
soc = [solver.NumVar(min_soc, max_soc, f"soc_{t}") for t in range(time_steps)]

# Constraints
for t in range(time_steps):
    # SOC balance constraint
    if t == 0:
        solver.Add(
            soc[t] == initial_soc + (charge[t] * dt / battery_capacity) * rte - (discharge[t] * dt / battery_capacity) / rte
        )
    else:
        solver.Add(
            soc[t]
            == soc[t - 1] + (charge[t] * dt / battery_capacity) * rte - (discharge[t] * dt / battery_capacity) / rte
        )

# Objective: Maximize revenue (price * discharge - price * charge)
objective = solver.Objective()
for t in range(time_steps):
    objective.SetCoefficient(discharge[t], marketDF.iloc[t]["price"])
    objective.SetCoefficient(charge[t], -marketDF.iloc[t]["price"])
objective.SetMaximization()

# Solve the model
status = solver.Solve()

if status == solver.OPTIMAL:
    print("Optimal solution found.")
    # Extract results
    results = pd.DataFrame({
        "charge": [charge[t].solution_value() for t in range(time_steps)],
        "discharge": [discharge[t].solution_value() for t in range(time_steps)],
        "soc": [soc[t].solution_value() for t in range(time_steps)],
        "price": marketDF["price"].values,
    }, index=marketDF.index)

    # Calculate profit
    results['revenue'] = results['discharge'] * results['price']
    results['cost'] = - results['charge'] * results['price']
    results['profit'] = results['revenue'] + results['cost']

    total_revenue = results["revenue"].sum()
    print(f"Total Arbitrage Revenue: {total_revenue:.2f} EUR")

    total_cost = results["cost"].sum()
    print(f"Total Arbitrage Cost: {total_cost:.2f} EUR")

    total_profit = results["profit"].sum()
    print(f"Total Arbitrage Profit: {total_profit:.2f} EUR")

    # Calculate number of cycles
    cycles = results["discharge"].sum() / battery_capacity
    print(f"Number of cycles: {cycles:.2f}")

    # Save results to Excel
    results.to_csv(results_folder + file_name + "arbitrage_results.csv")
else:
    print("No optimal solution found.")

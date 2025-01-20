# Energy Storage Arbitrage Revenue Optimization

## Description
This script calculates the arbitrage revenue potential for energy storage systems using market price data. It allows the calculation of optimal arbitrage profit, no. of cycles, avg. buy and sell prices, subject to different storage parameters. It employs the OR-Tools optimization library to simulate optimal charging and discharging behavior based on specified storage parameters.

## Features
- Processes market price data from multiple countries.
- Computes daily price spreads.
- Optimizes energy storage operations for maximum revenue.
- Supports custom storage configurations including efficiency, capacity, and state of charge limits.
- Outputs results to CSV files for visualisation/further analysis.

## Requirements
- Python 3.x
- Required Python libraries:
  - pandas
  - ortools

## Installation
1. Install Python 3.x if not already installed.
2. Install required Python libraries using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Place input CSV files containing market price data in the specified input folder.
2. Modify the script parameters (e.g., storage configurations, file paths) as needed.
3. Run the script:
   ```bash
   python arbitrage_loop.py
   ```
4. Results will be saved in the specified results folder.

## Input Data Format
- CSV files with the following columns:
  - `Datetime`: a column containing time intervals. The format can be specified using the `datetime_format` parameter and the column header by the `datetime_col` parameter.
  - `Price`: Market price data. The column header can be specified with `price_col`.

## Input Data Sources
- The `input_data` folder comes with German, Polish and United Kingdom hourly day-ahead electricity prices from 2016 to the start of 2025 as default.
- These were downloaded from Ember https://ember-energy.org/data/european-wholesale-electricity-price-data/, which provides a user friendly, cleaned dataset of European day-ahead market prices.
- For prices from the USA, gridstatus is a good tool.
- For other juristictions, price data is often available from the energy system operator. E.g. Chile: https://www.coordinador.cl/costos-marginales/

## Output
- CSV files with daily price spreads and arbitrage revenue results.
- Summary of results across all files and configurations saved in `central_results_2.csv`.

## Configuration
- Adjust the following parameters in the script as needed:
  - Storage properties (e.g., round-trip efficiency, capacity).
  - Input and results folder paths.
  - List of files and years to process.
  - Hourly storage durations to evaluate.

# Full startup intructions

---

## Use the following commands

## 1. Clone the Repository
```bash
git clone https://github.com/barnabyw/revenues/
cd <your-repo-folder>
```

## 2. Set Up a Virtual Environment
Create a new Python virtual environment:
```bash
python3 -m venv venv
```
Activate the virtual environment:
On Mac/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

## 3. Install Dependencies
Ensure you have a requirements.txt file in the repository. Install the dependencies:

```bash
pip install -r requirements.txt
```

## 4. Run the script
Run the script:
```bash
python script_name.py
```

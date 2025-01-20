# Energy Storage Arbitrage Revenue Optimization

## Description
This script calculates the arbitrage revenue potential for energy storage systems using market price data. It allows the calculation of optimal arbitrage profit, no. of cycles, avg. buy and sell prices, subject to different storage parameters. It employs the OR-Tools optimization library to simulate optimal charging and discharging behavior based on specified storage parameters.

## Features
- Processes market price data from multiple countries.
- Computes daily price spreads.
- Optimizes energy storage operations for maximum revenue.
- Supports custom storage configurations including efficiency, capacity, and state of charge limits.
- Outputs results to CSV files for further analysis.

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
   python script_name.py
   ```
4. Results will be saved in the specified results folder.

## Input Data Format
- CSV files with the following columns:
  - `Datetime`: a column containing time intervals. The format can be specified using the datetime_format parameter and the column header by the datetime_col parameter.
  - `Price`: Market price data. The column header can be specified with price_col.

## Output
- CSV files with daily price spreads and arbitrage revenue results.
- Summary of results across all files and configurations saved in `central_results_2.csv`.

## Configuration
- Adjust the following parameters in the script as needed:
  - Storage properties (e.g., round-trip efficiency, capacity).
  - Input and results folder paths.
  - List of files and years to process.
  - Hourly storage durations to evaluate.

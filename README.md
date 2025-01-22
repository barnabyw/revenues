# Energy Storage Arbitrage Revenue Optimization

# Context

## Energy arbitrage
Energy arbitrage is buying power at low prices and selling at high prices, to generate a profit. It is the primary way energy storage systems make their money. This code for analysing how much profit can be generated in different countries from energy arbitrage.
![image](https://github.com/user-attachments/assets/c81d2631-2bae-439e-8ac4-ea18729c4e45)

### Sources of data
Europe (inc. UK): https://ember-energy.org/data/european-wholesale-electricity-price-data/
USA: https://www.gridstatus.io/
Chile: https://www.coordinador.cl/costos-marginales/
For other regions, data is generally available on the website of the energy system operator. Day-ahead prices are the most available, with others usually paid.

## Electricity market 101

### Marginal cost pricing
Electricity, in the vast majority of countries, is priced according to 'marginal cost pricing' which means the price is set by the bid of the final unit of generation (supply) that is required to meet electricity demand. In the example below, this is a coal unit. The bids of all generators are ordered in price, then their power capacities are added together until demand is met. The price is the the most expensive generator once bids are ordered.
![image](https://github.com/user-attachments/assets/b794b76a-1b7b-4df7-a59e-263a2bde774a)

### Multiple markets
There are several markets, within countries, where power is bought and sold (wholesale markets). They mostly work with marginal cost pricing, but operate over different timeframes and have different objectives. [Modo](https://modoenergy.com/research/wholesale-trading-markets-explainer-gb-n2ex-epex-dayahead-intraday) have a helpful explainer for these different markets in terms of wholesale trading.

Day-ahead markets are where the majority of energy is traded, and where data is most widely available. However, it is important to note that day-ahead markets usually have the least volatile shapes and therefore trading across multiple markets will increase revenue. In GB, [Modo](https://modoenergy.com/research/jan-24-forecast-update-bess-revenues-intraday-prices-dispatch-battery-energy-storage-model?&utm_source=linkedin&utm_medium=main&utm_campaign=15_01_2025) estimated that there is a 30-35% uplift in revenues when trading in the intraday and day-ahead markets vs. just the day-ahead. This could be an appropriate uplift for revenues derived using this script.

### Other revenue streams

There are other mechanisms that reward energy storage assets outside of energy trading. These include th balancing mechanism, a major source in the UK. Capacity markets operate in most countries and pay a fixed price for power capacity, which is reduced for short durations. (Australia is an [exception](https://www.gridcog.com/blog/capacity-markets-vs-energy-only-markets#:~:text=Capacity%20markets%20give%20more%20direct,of%20revenue%20certainty%20for%20investors.)), which

Further reading on the fundamentals of energy storage revenues: [Monetizing Energy Storage](https://global.oup.com/academic/product/monetizing-energy-storage-9780192888174?cc=gb&lang=en&#)

# Script setup and features
This script calculates the arbitrage revenue potential for energy storage systems using market price data. It allows the calculation of optimal arbitrage profit, no. of cycles, avg. buy and sell prices, subject to different storage parameters. It employs the OR-Tools optimization library to simulate optimal charging and discharging behavior based on specified storage parameters.

## Features
- Processes market price data from multiple countries.
- Computes daily price spreads.
- Optimizes energy storage operations for maximum revenue.
- Supports custom storage configurations including efficiency, capacity, and state of charge limits.
- Outputs results to CSV files for visualisation/further analysis.

## Requirements
- Python 3.x (tested with versions up to 3.11)
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
python arbitrage_loop.py
```

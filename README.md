# Energy Storage Arbitrage Revenue Optimization

## Table of Contents

1. [Example Output](#example-output)
2. [Context](#context)
    - [Energy Arbitrage]
    - [Sources of Data]
3. [Electricity Market 101](#electricity-market)
    - [Marginal Cost Pricing]
    - [Multiple Markets]
    - [Other Revenue Streams]
4. [Script Setup and Features](#script-setup-and-features)
    - [Features]
    - [Requirements]
    - [Installation]
    - [Usage]
    - [Input Data Format]
    - [Output]
    - [Configuration]
5. [Next Steps](#next-steps)
6. [Full Startup Instructions](#full-startup-instructions)

## <a name="example-output"></a>Example Output

![image](https://github.com/user-attachments/assets/f8d65a8c-4398-4b39-941c-a1782c29278e)

Results from `arbitrage_loop.py`, visualised with Tableau

![image](https://github.com/user-attachments/assets/37fd6032-230b-4377-ba02-829cf6f023cd)

Results from `arbitrage_loop_effiency.py`, visualised with Tableau

## <a name="context"></a>Context

### Energy Arbitrage
Energy arbitrage is buying power at low prices and selling at high prices to generate a profit. It is the primary way energy storage systems make their money. This code is for analysing how much profit can be generated in different countries from energy arbitrage.

![image](https://github.com/user-attachments/assets/c81d2631-2bae-439e-8ac4-ea18729c4e45)

### Sources of Data
- Europe (including the UK): [Ember](https://ember-energy.org/data/european-wholesale-electricity-price-data/)
- USA: [GridStatus](https://www.gridstatus.io/)
- Chile: [Coordinador Electrico Nacional](https://www.coordinador.cl/costos-marginales/)
- For other regions, data is generally available on the website of the energy system operator. Day-ahead prices are the most available, with others usually paid.

## <a name="electricity-market"></a>Electricity market 101

### Marginal Cost Pricing
Electricity, in the vast majority of countries, is priced according to 'marginal cost pricing' which means the price is set by the bid of the final unit of generation (supply) that is required to meet electricity demand. In the example below, this is a coal unit. The bids of all generators are ordered in price, then their power capacities are added together until demand is met. The price is the most expensive generator once bids are ordered.

![image](https://github.com/user-attachments/assets/b794b76a-1b7b-4df7-a59e-263a2bde774a)

### Multiple Markets
There are several markets, within countries, where power is bought and sold (wholesale markets). They mostly work with marginal cost pricing, but operate over different timeframes and have different objectives. [Modo](https://modoenergy.com/research/wholesale-trading-markets-explainer-gb-n2ex-epex-dayahead-intraday) have a helpful explainer for these different markets in terms of wholesale trading.

Day-ahead markets are where the majority of energy is traded, and where data is most widely available. However, it is important to note that day-ahead markets usually have the least volatile shapes and therefore trading 

Day-ahead markets are where the majority of energy is traded, and where data is most widely available. However, it is important to note that day-ahead markets usually have the least volatile shapes and therefore trading across multiple markets will increase revenue. In GB, [Modo](https://modoenergy.com/research/jan-24-forecast-update-bess-revenues-intraday-prices-dispatch-battery-energy-storage-model?&utm_source=linkedin&utm_medium=main&utm_campaign=15_01_2025) estimated that there is a 30-35% uplift in revenues when trading in the intraday and day-ahead markets vs. just the day-ahead. This could be an appropriate uplift for revenues derived using this script.

### Other revenue streams

There are other mechanisms that reward energy storage assets outside of energy trading. These include th balancing mechanism, a major source in the UK. Capacity markets operate in most countries and pay a fixed price for power capacity, which is reduced for short durations. (Australia is an [exception](https://www.gridcog.com/blog/capacity-markets-vs-energy-only-markets#:~:text=Capacity%20markets%20give%20more%20direct,of%20revenue%20certainty%20for%20investors.)), which

Further reading on the fundamentals of energy storage revenues: [Monetizing Energy Storage](https://global.oup.com/academic/product/monetizing-energy-storage-9780192888174?cc=gb&lang=en&#)

# <a name="script-setup-and-features"></a>Script Setup and Features
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
   which by default loops through different durations of storage.
   or
   ```bash
   python arbitrage_loop_efficiency.py
   ```
   which by default loops through different round trip efficiencies.
5. Results will be saved in the specified results folder.

## Input Data Format
- CSV files with the following columns:
  - `Datetime`: a column containing time intervals. The format can be specified using the `datetime_format` parameter and the column header by the `datetime_col` parameter.
  - `Price`: Electricity price data. The column header can be specified with `price_col`.
- The `input_data` folder comes with German, Polish and United Kingdom hourly day-ahead electricity prices from 2016 to the start of 2025 as default.
- These were downloaded from Ember https://ember-energy.org/data/european-wholesale-electricity-price-data/, which provides a user friendly, cleaned dataset of European day-ahead market prices. See above for other sources.

## Output
- CSV files with daily price spreads and arbitrage revenue results.
- Summary of results across all files and configurations saved in `arbitrage_results.csv`.

## Configuration
- Adjust the following parameters in the script as needed:
  - Storage properties (e.g., round-trip efficiency, capacity).
  - Input and results folder paths.
  - List of files and years to process.
  - Hourly storage durations to evaluate.
 
## Next steps
- An improvement could be to save new results centrally to a database that contains previous runs, without them having to be repeated each time. The
    ```bash
    years x countries.py
   ```
  did this, but using a suboptimal spread function rather than optimised arbitrage. It shows how this could be approached.
   


# <a name="full-startup-instructions"></a>Full startup intructions

---

## Use the following commands

### 1. Clone the Repository
```bash
git clone https://github.com/barnabyw/revenues/
cd <your-repo-folder>
```

### 2. Set Up a Virtual Environment
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

### 3. Navigate back to the repo directory
Ensure you have a requirements.txt file in the repository. Install the dependencies:

```bash
cd <your-repo-folder>
```

### 4. Install Dependencies
Ensure you have a requirements.txt file in the repository. Install the dependencies:

```bash
pip install -r requirements.txt
```

### 5. Run the script
Run the script:
```bash
python arbitrage_loop.py
```

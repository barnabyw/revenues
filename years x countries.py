import pandas as pd
import os
import matplotlib.pyplot as plt
import json
from datetime import datetime
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

folder = "/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Data bank/Market Data/Europe 21.09/"
files = ['Chile']  # Add your country files here
#'Hungary.csv', 'Romania.csv',, 'Netherlands.csv', 'Poland.csv'

""" problematic files: Ireland, """

datetime = 'Datetime (Local)'
price = 'Price (EUR/MWhe)'
hrs = [4,6,8]
years_mode = '' # Set to 'auto' to use all years in the data
max_cf_de = 0.8
select = list(range(2019,2025))
rte = 0.80

# File paths
monthly_csv = '/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Arbitrage/monthly_data.csv'
yearly_csv = '/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Arbitrage/yearly_data.csv'


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
    daily_spread['low'] = daily_spread['bottom_avg']
    daily_spread['high'] = daily_spread['top_avg']
    daily_spread['date'] = pd.to_datetime(daily_spread['date'])
    daily_spread['year'] = daily_spread['date'].dt.year
    daily_spread['month'] = daily_spread['date'].dt.month
    
    # Group by both year and month, and calculate the mean for each
    avg_spread_for_month = daily_spread.groupby(['year', 'month'], as_index=False).agg({
        'daily_spread': 'mean',
        'high': 'mean',
        'low': 'mean'
    })

    avg_spread_for_month.rename(columns={
        'daily_spread': 'average_monthly_spread', 
        'high': 'average_top_hours', 
        'low': 'average_bottom_hours'
    }, inplace=True)

    # Round the results
    avg_spread_for_month = avg_spread_for_month.round(2)
    
    # Calculate yearly average spread
    avg_spread_for_year = daily_spread.groupby('year', as_index=False).agg({
        'daily_spread': 'mean',
        'high': 'mean',
        'low': 'mean'
    }).rename(columns={
        'daily_spread': 'average_yearly_spread',
        'high': 'average_top_hours_yearly',
        'low': 'average_bottom_hours_yearly'
    })
    
    # Round the yearly results
    avg_spread_for_year = avg_spread_for_year.round(2)

    return avg_spread_for_month, avg_spread_for_year

def find_missing_hours(df, year):
    """
    Function to find missing hours in a given year of data.
    
    Parameters:
        df (DataFrame): The DataFrame containing 'datetime' column.
        year (int): The year to check for missing hours.
    
    Returns:
        tuple: (number of missing hours, list of missing hours)
    """
    current_year = 2024
    
    if year == current_year:
        # Use the min and max datetime in the current year for the range
        min_datetime = df['datetime'].min()
        max_datetime = df['datetime'].max()
        full_range = pd.date_range(start=min_datetime, end=max_datetime, freq='H')
    else:
        # Use the full year range for other years
        full_range = pd.date_range(start=f'{year}-01-01 00:00:00', end=f'{year}-12-31 23:00:00', freq='H')
    
    # Extract the actual hours present in the dataframe
    actual_hours = df['datetime']
    
    # Find the missing hours
    missing_hours = full_range.difference(actual_hours)
    
    return len(missing_hours), missing_hours

yearly_results = []
monthly_results = []

# Main loop
for file in files:
    df = pd.read_csv(os.path.join(folder, file + ".csv"))
    df.rename(columns={datetime: 'datetime', price: 'price'}, inplace=True)
    df['datetime'] = pd.to_datetime(df['datetime']) #modified
    df = df[['datetime', 'price']]
    df['year'] = df['datetime'].dt.year

    if years_mode == 'auto':
        years = df['year'].unique().tolist()
    else:
        years = select

    for year in years:
        df_year = df[df['year'] == year]

        # Only process if df_year is not empty
        if not df_year.empty:
            # Check for missing hours
            num_missing, missing_hours = find_missing_hours(df_year, year)
            
            if num_missing > -1:
                print(f"{num_missing} hours missing in {year} for {file.split('.')[0]}.")
                if num_missing > 2:
                    print("Missing hours:")
                    print(missing_hours)

            for hour in hrs:
                avg_spread_month, avg_spread_year = spread(df_year, hour)
                if not avg_spread_year.empty:
                    avg_spread_year = avg_spread_year.copy()  # Ensure it's not a view
                    avg_spread_year.loc[:, 'country'] = file.split('.')[0]  # Set country name using .loc
                    avg_spread_year.loc[:, 'hrs'] = hour  # Use 'hour' not 'hrs' (since it's the current hour)
                    yearly_results.append(avg_spread_year)

                # Process avg_spread_month if it's not empty
                if not avg_spread_month.empty:
                    avg_spread_month = avg_spread_month.copy()  # Ensure it's not a view
                    avg_spread_month.loc[:, 'country'] = file.split('.')[0]  # Set country name using .loc
                    avg_spread_month.loc[:, 'hrs'] = hour  # Add the current hour as 'hrs' column
                    monthly_results.append(avg_spread_month)

monthly_df = pd.concat(monthly_results, ignore_index=True)
yearly_df = pd.concat(yearly_results, ignore_index=True)

# Apply transformations to yearly_df
yearly_df['arbitrage (€k/MWh)'] = (yearly_df['average_top_hours_yearly'] - yearly_df['average_bottom_hours_yearly'] / rte) * 365 / 1000

# Apply transformations to monthly_df
monthly_df['arbitrage (€k/MWh)'] = (monthly_df['average_top_hours'] - monthly_df['average_bottom_hours'] / rte) * 365 / 1000

# Load existing data from CSVs if they exist, then concatenate with new data
if os.path.exists(monthly_csv):
    monthly_existing_df = pd.read_csv(monthly_csv)
    monthly_df = pd.concat([monthly_existing_df, monthly_df], ignore_index=True).drop_duplicates()
else:
    print('Error adding to monthly_df')

if os.path.exists(yearly_csv):
    yearly_existing_df = pd.read_csv(yearly_csv)
    yearly_df = pd.concat([yearly_existing_df, yearly_df], ignore_index=True).drop_duplicates()
else:
    print('Error adding to yearly_df')
    
monthly_df = monthly_df.drop_duplicates().reset_index(drop=True)
yearly_df = yearly_df.drop_duplicates().reset_index(drop=True)
    
print(yearly_df.columns)

monthly_df['Date'] = pd.to_datetime(monthly_df['year'].astype(str) + '-' + monthly_df['month'].astype(str).str.zfill(2), format='%Y-%m').dt.to_period('M')

# Save updated DataFrames back to CSV
monthly_df.to_csv(monthly_csv, index=False)
yearly_df.to_csv(yearly_csv, index=False)


# Load the second dataset (gas price data)
gas_data = pd.read_csv("/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Arbitrage/Arbitrage revenues/PNGASEUUSDM.csv")
gas_data['DATE'] = pd.to_datetime(gas_data['DATE'])

# Format as YYYY-MM by converting to a period
gas_data['Date'] = gas_data['DATE'].dt.to_period('M')


gas_data.rename(columns={'PNGASEUUSDM': 'average_gas_price'}, inplace=True)

# Merge with yearly_df on the year column
merged_mnth_df = monthly_df.merge(gas_data, on='Date', how='left')

merged_mnth_df = merged_mnth_df.drop(['DATE', 'arbitrage (€k/MWh)', 'revenues (€k/MWh)'], axis=1)

# 1. Remove any values related to the month of 2024-09 from all countries
merged_mnth_df = merged_mnth_df[~(merged_mnth_df['Date']=='2024-09')]

# 2. Remove year=2021 values for UK
merged_mnth_df = merged_mnth_df[~((merged_mnth_df['country'] == 'UK') & (merged_mnth_df['Date']=='2021-12'))]

# 3. Create a new DataFrame that averages certain columns by half-year
# Create a new column for half-year by using conditions on the month
merged_mnth_df['half_year'] = merged_mnth_df['Date'].apply(lambda x: f"{x.year}-H1" if x.month <= 6 else f"{x.year}-H2")

# List of columns to average by half-year
columns_to_average = ['average_monthly_spread', 'average_top_hours', 'average_bottom_hours', 'average_gas_price']  # replace with actual column names

# Group by 'country' and 'half_year', then calculate the mean for specified columns
half_year_df = merged_mnth_df.groupby(['country', 'half_year', 'hrs'])[columns_to_average].mean().reset_index()

# Extract the year from the 'half_year' column and add it as a new column
half_year_df['year'] = half_year_df['half_year'].str[:4]

half_year_df.to_csv('/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Arbitrage/Arbitrage revenues/half year.csv', index=False)

# Save to a CSV file for Tableau
merged_mnth_df.to_csv('/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Arbitrage/Arbitrage revenues/revs_gas_price_mth.csv', index=False)

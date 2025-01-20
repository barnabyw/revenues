#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 14:19:45 2024

@author: barnabywinser
"""

import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timedelta

# Replace with your actual API key
API_KEY = '52ffc519-ffbd-4a56-b988-5b3df166ea36'
# EIC code for the United Kingdom
EIC_CODE = '10YPL-AREA-----S'
# Define the time interval

start = '2024-01-01-00:00' #yyyyMMddHHmm
end = '2024-12-31-23:00'

period_start = start.replace("-","").replace(":","")  # UTC yyyyMMddHHmm
period_end = end.replace("-","").replace(":","")    # UTC yyyyMMddHHmm

# API endpoint
url = 'https://web-api.tp.entsoe.eu/api?'

# Parameters
params = {
    'documentType': 'A44',
    'in_Domain': EIC_CODE,
    'out_Domain': EIC_CODE,
    'periodStart': period_start,
    'periodEnd': period_end,
    'securityToken': API_KEY
}

# Send the request
response = requests.get(url, params=params)

print(response)

# Parse the XML response
root = ET.fromstring(response.content)

# Namespace dictionary for parsing
ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3'}

# Initialize an empty list to collect data
data = []

# Extract TimeSeries information
for time_series in root.findall('ns:TimeSeries', ns):
    currency = time_series.find('ns:currency_Unit.name', ns).text
    unit = time_series.find('ns:price_Measure_Unit.name', ns).text
    
    # Extract periods
    for period in time_series.findall('ns:Period', ns):
        start_time = period.find('ns:timeInterval/ns:start', ns).text
        resolution = period.find('ns:resolution', ns).text

        # Parse start time to datetime object
        start_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%MZ')

        # Extract price points and adjust the timestamp for each position
        for point in period.findall('ns:Point', ns):
            position = int(point.find('ns:position', ns).text)
            price = float(point.find('ns:price.amount', ns).text)
            # Calculate the time for each point based on the start time and position
            point_time = start_dt + timedelta(hours=position - 1)
            # Append data to list
            data.append([point_time, position, price, currency, unit])

# Convert to DataFrame
df = pd.DataFrame(data, columns=['Date', 'Position', 'Price', 'Currency', 'Unit'])

# Convert start and end to datetime objects
start_datetime = datetime.strptime(start, '%Y-%m-%d-%H:%M')
end_datetime = datetime.strptime(end, '%Y-%m-%d-%H:%M')

# Generate all hourly datetimes within the range
all_hourly_datetimes = pd.date_range(start=start_datetime, end=end_datetime, freq='h')

df = df.sort_values(by='Date').reset_index(drop=True)

# Check for missing hourly datetimes in the DataFrame
df_dates = pd.to_datetime(df['Date'])
missing_dates = all_hourly_datetimes.difference(df_dates)

# Display results
print("missing dates", missing_dates, df.head())

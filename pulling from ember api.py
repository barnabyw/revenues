#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 09:24:10 2024

@author: barnabywinser
"""

import requests
import pandas as pd

my_api_key = ""
base_url = "https://api.ember-climate.org"

query_url = (
  f"{base_url}/v1/electricity-generation/yearly"
  + f"?entity_code=DEU&is_aggregate_series=false&start_date=2000&api_key={my_api_key}"
)

response = requests.get(query_url)

if response.status_code == 200:
    data = response.json()
    # Assuming the data you want is in a list format or dictionary structure
    # Adjust the key if needed based on the structure of the response.
    df = pd.DataFrame(data['data'])  # 'data' should be replaced by the correct key in the JSON response
    
    # Display or print the dataframe to verify
    print(df)
else:
    print(f"Error: {response.status_code}")
    
print(df.columns)

filtered_df = df[df['date'] == '2023']

print(filtered_df[['entity','series','date','generation_twh']])


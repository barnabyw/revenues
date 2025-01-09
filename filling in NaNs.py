#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 12:48:50 2024

@author: barnabywinser
"""

import pandas as pd
import numpy as np
import os

market_data = '/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Data bank/Market Data/'
folder = 'UK/'
import_file = 'UK_NaNs_filled.csv'
export_file = 'UK_2023_clean'

import_path = os.path.join(market_data, folder, import_file)
export_path = os.path.join(market_data, folder, export_file)

df = pd.read_csv(import_path)

# Function to fill NaN with the average of the nearest preceding and nearest proceeding value
def fill_na_with_avg_of_neighbors(df, column_name):
    for i in range(len(df)):
        if pd.isna(df.loc[i, column_name]):
            # Get the nearest preceding value (if exists)
            if i - 1 >= 0:
                preceding_value = df.loc[i-1, column_name]
            else:
                preceding_value = np.nan
            
            # Get the nearest proceeding value (if exists)
            if i + 1 < len(df):
                proceeding_value = df.loc[i+1, column_name]
            else:
                proceeding_value = np.nan

            # If both neighbors are available, fill with their average
            if not np.isnan(preceding_value) and not np.isnan(proceeding_value):
                df.loc[i, column_name] = round((preceding_value + proceeding_value) / 2,2)
            # If only one neighbor exists, fill with that value
            elif not np.isnan(preceding_value):
                df.loc[i, column_name] = preceding_value
            elif not np.isnan(proceeding_value):
                df.loc[i, column_name] = proceeding_value

    return df

df_filled = fill_na_with_avg_of_neighbors(df, 'Price EUR')

df_filled.to_csv(export_path, index = False)

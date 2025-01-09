#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 13:04:02 2024

@author: barnabywinser
"""

import gridstatus
import pandas as pd
import datetime

region = caiso

caiso = gridstatus.CAISO()

start = pd.Timestamp("April 10, 2024").normalize()
end = pd.Timestamp.now().normalize()
mix_df = caiso.get_fuel_mix(start, end=end, verbose=False)





mix_df.to_csv(")
            
string = start.str

x = datetime.datetime.now()              

print(f"{start.date()}")

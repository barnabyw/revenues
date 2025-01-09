from matplotlib.lines import Line2D


folder = "/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Overall revenue/"
from matplotlib.ticker import FuncFormatter

# Application parameters
Cap_p_nom = 10  # Power in MW
Cyc_pa = 365  # Cycles per annum
P_el = 20 * 1.2439  # Electricity purchase price $/MWh
el_g = 0  # Electricity price escalator % p.a.

graph = 'b'
ya = 0
yb = 250
lcos_scenario = 'lcos w rep'

import pandas as pd
import math
import matplotlib.pyplot as plt

file_path = '/Users/barnabywinser/Library/CloudStorage/OneDrive-SharedLibraries-Rheenergise/Commercial - Documents/Market data & analysis/Overall revenue/arbitrage_cm.xlsx'

# Define technology parameters as df
df = pd.read_excel(file_path, sheet_name='tech cost', index_col=0, header=0)
df2 = pd.read_excel(file_path, sheet_name='charging costs', index_col=0)

# Define function for LCOS
def calculate_lcos(t, technology_params, util_params):
    C_p_inv = df.loc['Power CAPEX', country]
    C_e_inv = df.loc['Energy CAPEX', country]
    C_p_om = df.loc['Power OPEX', country]
    C_e_om = df.loc['Energy OPEX', country]
    C_p_eol = df.loc['Power EoL cost', country]
    C_e_eol = df.loc['Energy EoL cost', country]
    C_p_rep = df.loc['Replacement Power', country]
    C_e_rep = df.loc['Replacement Energy', country]
    r = (df.loc['WACC', country]) / 100
    rt = (df.loc['Round-trip efficiency', country]) / 100
    DoD = (df.loc['DoD', country]) / 100
    n_self = (df.loc['Self-discharge', country]) / 100
    Life_cyc = df.loc['Lifetime 100% DoD', country]
    Cyc_rep = df.loc['Replacement interval', country]
    Deg_t = (df.loc['Temporal degradation', country]) / 100
    EoL = (df.loc['EoL threshold', country]) / 100
    T_con = int(df.loc['Pre-dev + construction', country])
    N_op1 = df.loc['Economic Life', country]

    # Intermediate calculations
    Cap_e_nom = Cap_p_nom * t  # Energy capacity MWh
    Deg_c = 1 - EoL ** (1 / Life_cyc)  # Cycle degradation
    N_op = min(math.log(EoL) / (math.log(1 - Deg_t) + Cyc_pa * math.log(1 - Deg_c)), N_op1)  # Operational lifetime
    T_rep = Cyc_rep / Cyc_pa  # Years per replacement
    R = N_op / T_rep if T_rep > 0 else 0  # Replacements in lifetime

    # Project lifetime
    N_project = N_op + T_con  # Project lifetime

    # Calculate Total CAPEX (unchanged)
    Total_CAPEX = sum(1000 * (C_p_inv * Cap_p_nom + C_e_inv * Cap_e_nom) / (T_con * (1 + r) ** (n - 1)) for n in range(1, T_con + 1))

    # Function to calculate annual charged electricity
    def Ein(n):
        return (Cap_e_nom * DoD * Cyc_pa / rt) * ((1 - Deg_c) ** ((n - T_con - 1) * Cyc_pa)) * ((1 - Deg_t) ** (n - T_con - 1))

    # Charging costs incurred after construction (from year T_con + 1)
    total_charge_cost = sum(P_el * Ein(n) / (1 + r) ** (n - 1) for n in range(T_con + 1, int(N_op) + T_con + 1))

    # Add fractional year for charging cost
    fraction_yr = N_op - int(N_op)
    if fraction_yr > 0:
        n = int(N_op) + T_con + 1
        fractional_energy_input = Ein(n) * fraction_yr
        total_charge_cost += fractional_energy_input * P_el / (1 + r) ** (n - 1)

    # Calculate replacement costs (unchanged)
    Rep_disc = 0
    if C_p_rep + C_e_rep > 0:
        Rep_disc = sum((1000 * C_p_rep * Cap_p_nom + C_e_rep * Cap_e_nom) / (1 + r) ** (T_con + k * T_rep) for k in range(1, int(R) + 1))
        fractional_R = R - int(R)
        if fractional_R > 0:
            Rep_disc += fractional_R * (1000 * C_p_rep * Cap_p_nom + C_e_rep * Cap_e_nom) / (1 + r) ** (T_con + (int(R) + 1) * T_rep)

    # Function to calculate discharged energy (Eout)
    def Eout(n):
        return Ein(n) * rt * (1 - n_self)

    total_eout = sum(Eout(n) / (1 + r) ** (n - 1) for n in range(T_con + 1, int(N_op) + T_con + 1))

    # Total O&M costs
    total_om_cost = sum((C_p_om * Cap_p_nom * 1000 + C_e_om * Ein(n)) / (1 + r) ** (n - 1) for n in range(T_con + 1, int(N_op) + T_con + 1))

    # End-of-life costs
    Total_EoL = (C_p_eol * 1000 * Cap_p_nom + C_e_eol * 1000 * Cap_e_nom) / (1 + r) ** (N_project + 1)

    # Calculate LCOS
    numerator = Total_CAPEX + Rep_disc + total_charge_cost + total_om_cost + Total_EoL
    LCOS = numerator / total_eout if total_eout > 0 else None

    # Return a dictionary with all values
    return {
        'CAPEX': Total_CAPEX/total_eout,
        'Replacement': Rep_disc/total_eout,
        'Charging': total_charge_cost/total_eout,
        'Energy discharged': total_eout,
        'O&M': total_om_cost/total_eout,
        'End of life': Total_EoL/total_eout,
        'LCOS': LCOS
    }

# Collect technologies from df and df2
countries = df.columns

# Generate time_values for the LCOS/LCOE calculations
#time_values = [t / 10 for t in range(1, 121)]
time_values = list(range(1,11))

# Results list
results = []

# Run calculations for storage techs using calculate_lcos
for country in countries:
    technology_params = df[country]
    util_params = df2[df2['country'] == country]
    util_params.set_index('hrs', inplace = True)
    for t in time_values:
        P_el = util_params.loc[t,'Charging cost']
        # Calculate LCOS and other components for storage technologies
        result_values = calculate_lcos(t, technology_params, util_params)
        
        arbitrage = util_params.loc[t,'Arbitrage rev/MWh']
        cm = util_params.loc[t, 'CM rev/MWh discharged']
        
        # Append results, including intermediate values
        results.append({
            'Country': country,
            't': t,
            'LCOS': result_values['LCOS'],
            'CAPEX': result_values['CAPEX'],
            'Replacement': result_values['Replacement'],
            'Charging': result_values['Charging'],
            'Energy discharged': result_values['Energy discharged'],
            'O&M': result_values['O&M'],
            'End of life': result_values['End of life'],
            'Arbitrage': arbitrage,
            'Capacity Market': cm
        })


results_df = pd.DataFrame(results)

results_df.to_csv(folder + 'lcos and rev.csv', index = False)

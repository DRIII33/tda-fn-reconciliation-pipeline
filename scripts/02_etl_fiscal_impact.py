import pandas as pd
import numpy as np

# Load foundational data
df_claims = pd.read_csv('synthetic_tans_claims.csv')
df_crosswalk = pd.read_csv('tx_unps_crosswalk.csv')

# 1. Data Sanitization: Standardize TANS_Org_ID (Remove trailing hyphens)
df_claims['TANS_Org_ID'] = df_claims['TANS_Org_ID'].str.rstrip('-')
df_crosswalk['TANS_Org_ID'] = df_crosswalk['TANS_Org_ID'].str.rstrip('-')

# 2. Map Legacy IDs (Integrity Crosswalk)
df_mapped = pd.merge(df_claims, df_crosswalk, on='TANS_Org_ID', how='left')

# 3. Anomaly Detection: Flag ADP Violations
df_mapped['ADP_Violation'] = df_mapped['Total_Meals_Claimed'] > df_mapped['Approved_ADP']

# 4. FISCAL IMPACT ANALYSIS (The Step 4 Update)
# Rationale: Quantifies fiscal exposure for federal grant monitoring.
rates = {'NSLP': 4.25, 'SBP': 2.50, 'CACFP': 2.50, 'SFSP': 3.75}

def calculate_disallowed(row):
    if row['ADP_Violation']:
        excess_meals = row['Total_Meals_Claimed'] - row['Approved_ADP']
        return round(excess_meals * rates.get(row['Program_Type'], 0), 2)
    return 0.0

def calculate_cash_lag(row):
    return row['Reimbursement_Requested'] if row['Status'] == 'Pending Review' else 0.0

df_mapped['Potential_Disallowed_Cost'] = df_mapped.apply(calculate_disallowed, axis=1)
df_mapped['Pending_Cash_Flow_Impact'] = df_mapped.apply(calculate_cash_lag, axis=1)

# Export for BigQuery Ingestion
df_mapped.to_csv('cleansed_tans_claims.csv', index=False)

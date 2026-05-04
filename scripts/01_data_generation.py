import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# 1. Generate TX-UNPS to TANS Crosswalk Data
# Rationale: TDA uses a "clean start" philosophy. We must map new TANS IDs to legacy TX-UNPS IDs.
np.random.seed(42)
num_entities = 100

crosswalk_data = {
    'TANS_Org_ID': [f"ORG-{1000 + i}" for i in range(num_entities)],
    'TX_UNPS_CE_ID': [f"CE-{9000 + i}" for i in range(num_entities)],
    'Entity_Name': [f"Texas School District {i}" for i in range(num_entities)],
    'Program_Type': np.random.choice(['NSLP', 'SBP', 'CACFP', 'SFSP'], num_entities)
}
df_crosswalk = pd.DataFrame(crosswalk_data)

# 2. Generate TANS Claims Data (2026 Program Year)
# Rationale: Captures monthly meal counts, reimbursement requested, and Average Daily Participation (ADP) limits.
claims_data = []
statuses = ['Approved', 'Pending Review', 'Denied']

for idx, row in df_crosswalk.iterrows():
    # Simulate an Average Daily Participation limit per entity
    adp_limit = random.randint(500, 5000) 
    
    # Simulate meal counts (Introduce intentional anomalies where meals > ADP for validation testing)
    is_anomaly = random.random() < 0.05 # 5% chance of anomaly
    meals_claimed = adp_limit + random.randint(100, 500) if is_anomaly else int(adp_limit * random.uniform(0.7, 0.9))
    
    # Simulate reimbursement logic (Simplified federal rate applied)
    reimbursement_rate = 4.25 if row['Program_Type'] == 'NSLP' else 2.50
    reimbursement_req = meals_claimed * reimbursement_rate
    
    claims_data.append({
        'Claim_ID': f"CLM-2026-{random.randint(10000, 99999)}",
        'TANS_Org_ID': row['TANS_Org_ID'],
        'Claim_Month': '2026-04-01',
        'Total_Meals_Claimed': meals_claimed,
        'Approved_ADP': adp_limit,
        'Reimbursement_Requested': round(reimbursement_req, 2),
        'Status': np.random.choice(statuses, p=[0.7, 0.25, 0.05])
    })

df_claims = pd.DataFrame(claims_data)

# 3. Generate CAPPS Payment Disbursement Data
# Rationale: CAPPS is the statewide accounting system. Payments may slightly vary from requested amounts due to adjustments.
capps_data = []
for idx, row in df_claims.iterrows():
    if row['Status'] == 'Approved':
        # Simulate authorized payment, occasionally with a slight variance
        variance = random.uniform(0.98, 1.0) 
        authorized_payment = row['Reimbursement_Requested'] * variance
        
        capps_data.append({
            'Payment_ID': f"PAY-{random.randint(100000, 999999)}",
            'TANS_Org_ID': row['TANS_Org_ID'],
            'Payment_Date': '2026-05-15',
            'Authorized_Payment_Amount': round(authorized_payment, 2)
        })

df_capps = pd.DataFrame(capps_data)

# Export synthetic data to CSV
df_crosswalk.to_csv('tx_unps_crosswalk.csv', index=False)
df_claims.to_csv('synthetic_tans_claims.csv', index=False)
df_capps.to_csv('synthetic_capps_payments.csv', index=False)

print("Synthetic TDA Data Generated Successfully.")

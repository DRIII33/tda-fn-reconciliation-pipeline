### **1. The Business Scenario**

**Context:** The Texas Department of Agriculture (TDA) Food and Nutrition (F&N) Division administers over \$2.5 billion in federal funding annually across 12 nutrition programs[cite: 3]. The Business Management section serves as the financial nerve center responsible for reconciling these federal grant awards and ensuring reimbursement claims are processed accurately[cite: 3].

**The Challenge:** For the 2026 program year, the TDA is undergoing a massive digital transformation, migrating from the legacy Texas Unified Nutrition Programs System (TX-UNPS) to the modern Texas Automated Nutrition System (TANS)[cite: 3]. This transition utilizes a "clean start" philosophy, requiring sponsors to repopulate data, which introduces high risks of "data rot" and gaps in longitudinal reporting[cite: 3]. Furthermore, the financial reconciliation process between TANS (application/claim data) and CAPPS (the state accounting system for final payment authorization) currently relies on manual spreadsheet manipulation, creating a 15-day bottleneck and increasing the risk of Single Audit findings[cite: 3]. 

**The Solution:** This project demonstrates a fully automated data pipeline that:
1.  **Implements a Site ID Crosswalk:** Maps new 2026 TANS Organization/Site IDs back to legacy TX-UNPS IDs to preserve historical context[cite: 3].
2.  **Automates Data Quality Audits:** Uses Python to profile data and flag anomalies where site meal counts exceed their approved "Average Daily Participation" (ADP)[cite: 3].
3.  **Executes Real-Time Fiscal Reconciliation:** Utilizes Google BigQuery (SQL) to link TANS claims to CAPPS disbursements, calculating real-time budget variances and flagging "Pending Review" claims for executive escalation[cite: 3].

---

### **2. Python: Synthetic Data Generation (Google Colab)**

*This script generates the foundational data modeled strictly after the TDA parameters provided in the pre-research documentation.*

```python
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
```

---

### **3. Python: ETL & Data Quality Auditing (Google Colab)**

*This script executes the "Data Quality Auditing" procedure, fulfilling the requirement to run anomaly detection on meal counts exceeding Average Daily Participation (ADP)[cite: 3].*

```python
import pandas as pd

# Load the generated data
df_claims = pd.read_csv('synthetic_tans_claims.csv')
df_crosswalk = pd.read_csv('tx_unps_crosswalk.csv')

print("--- Data Profiling & ETL Process Initiated ---")

# 1. Map Legacy IDs (The Site ID Crosswalk logic)
df_mapped = pd.merge(df_claims, df_crosswalk, on='TANS_Org_ID', how='left')
print(f"Successfully mapped {len(df_mapped)} records to legacy TX-UNPS CE IDs.")

# 2. Anomaly Detection: Flag claims exceeding Approved Average Daily Participation (ADP)
# Rationale: TDA SOP requires root-cause analysis on data entry errors and compliance breaches.
df_mapped['ADP_Violation'] = df_mapped['Total_Meals_Claimed'] > df_mapped['Approved_ADP']

anomalies = df_mapped[df_mapped['ADP_Violation'] == True]

print(f"\nCRITICAL ALERT: Identified {len(anomalies)} Contracting Entities exceeding ADP limits.")
print("These entities will be flagged for immediate ESC desk reviews.")
print(anomalies[['TANS_Org_ID', 'TX_UNPS_CE_ID', 'Total_Meals_Claimed', 'Approved_ADP']])

# Export cleansed and flagged data for BigQuery ingestion
df_mapped.to_csv('cleansed_tans_claims.csv', index=False)
```

---

### **4. SQL: Monthly Grant Reconciliation (Google BigQuery)**

*This script answers the core business challenge: replacing the 15-day manual reconciliation cycle. It links TANS claims to CAPPS payments, calculates variances, and flags bottlenecks for the Assistant Director[cite: 3]. Ensure this is run in the `driiiportfolio` BigQuery project.*

```sql
/*
  Project: TDA F&N Division - Monthly Grant Reconciliation 
  Platform: Google BigQuery (Project ID: driiiportfolio)
  Objective: Execute reconciliation workflow linking TANS claim records to CAPPS payment records.
  Calculates variance between requested reimbursement and actual authorized payments.
*/

WITH ClaimsData AS (
  SELECT 
    c.TANS_Org_ID,
    cw.TX_UNPS_CE_ID,
    cw.Entity_Name,
    cw.Program_Type,
    c.Claim_Month,
    SUM(c.Total_Meals_Claimed) AS Total_Meals,
    SUM(c.Reimbursement_Requested) AS Total_Requested,
    c.Status
  FROM 
    `driiiportfolio.tda_fn_data.cleansed_tans_claims` c
  LEFT JOIN 
    `driiiportfolio.tda_fn_data.tx_unps_crosswalk` cw 
    ON c.TANS_Org_ID = cw.TANS_Org_ID
  GROUP BY 
    1, 2, 3, 4, 5, 8
),

PaymentData AS (
  SELECT
    TANS_Org_ID,
    SUM(Authorized_Payment_Amount) AS Total_Paid
  FROM
    `driiiportfolio.tda_fn_data.synthetic_capps_payments`
  GROUP BY
    1
)

SELECT 
  cd.Entity_Name,
  cd.Program_Type,
  cd.TX_UNPS_CE_ID AS Legacy_ID,
  cd.TANS_Org_ID AS Modern_ID,
  cd.Status AS Claim_Status,
  cd.Total_Meals,
  cd.Total_Requested,
  COALESCE(pd.Total_Paid, 0) AS Actual_CAPPS_Disbursement,
  -- Calculate Variance: Flag differences between requested amounts and actual payments
  (cd.Total_Requested - COALESCE(pd.Total_Paid, 0)) AS Budget_Variance,
  
  -- Logic to flag "Claims in Pending Review" for leadership escalation
  CASE 
    WHEN cd.Status = 'Pending Review' THEN 'ESCALATE: Pending Review Bottleneck'
    WHEN (cd.Total_Requested - COALESCE(pd.Total_Paid, 0)) > 0 AND cd.Status = 'Approved' THEN 'FLAG: Payment Shortfall Variance'
    ELSE 'Reconciled'
  END AS Reconciliation_Action

FROM 
  ClaimsData cd
LEFT JOIN 
  PaymentData pd 
  ON cd.TANS_Org_ID = pd.TANS_Org_ID
ORDER BY 
  Budget_Variance DESC;
```

---

### **5. Looker Studio & Google Sheets Integration**

**Looker Studio (Power BI Equivalent):**
*   Connect Looker Studio directly to the BigQuery View created from the SQL query above.
*   **Visualizations to build:** 
    1. A KPI Scorecard showing "Total Unreconciled Variance" (The gap between TANS and CAPPS).
    2. A Bar Chart visualizing "Pending Review" claims segmented by `Program_Type` (NSLP, SBP, etc.) to identify programmatic bottlenecks[cite: 3].
    3. A dynamic table using "Drill-Through" concepts[cite: 3] allowing the user to click a region/program and see the specific `TANS_Org_ID`s missing payments.

**Google Sheets (Microsoft Excel Equivalent):**
*   Export the anomaly detection CSV from Python into Google Sheets.
*   Use Google Sheets to build a "Financial Modeling Sandbox" mimicking the "Analyze in Excel" feature requested by TDA[cite: 3]. Create pivot tables to project future school district debt based on the `Budget_Variance` calculated in the SQL script.

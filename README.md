# **Executive Financial Data Analyst Portfolio Project**

**Project Title:** TDA F&N Monthly Grant Reconciliation & Fiscal Monitoring Command Center  
**Author:** Daniel Rodriguez III - Financial Data Analyst
**Scenario:** 2026 Program Year Transition (Legacy TX-UNPS to Modern TANS)

---

## **1. GitHub Repository Structure**
**Repository Name:** `tda-fn-fiscal-reconciliation-pipeline`  
**Description:** An automated ETL and fiscal risk assessment pipeline designed to solve the 15-day reconciliation bottleneck and quantify financial exposure during the TDA’s TANS system migration[cite: 3, 5].

**📁 data/**
*   `synthetic_tans_claims.csv`: 2026 application/claim data featuring intentional ADP violations.
*   `synthetic_capps_payments.csv`: Disbursement logs for state accounting reconciliation.
*   `tx_unps_crosswalk.csv`: Foundational mapping for legacy-to-modern Site ID integrity.

**📁 scripts/**
*   `01_data_generation.ipynb`: Generates realistic, compliant synthetic data using federal reimbursement rates[cite: 3].
*   `02_etl_fiscal_impact.ipynb`: Executes data profiling, sanitization (trailing hyphen removal), and Step 4 Fiscal Impact Analysis[cite: 3].

**📁 sql/**
*   `monthly_grant_reconciliation_view.sql`: BigQuery SQL script surface-reconciling TANS/CAPPS with automated risk flagging[cite: 3, 5].

**📁 dashboards/**
*   `Executive_Oversight_Guide.md`: Documentation for the Looker Studio Command Center featuring the $217.29K Variance KPI[cite: 6].

---

## **2. The Business Scenario (README.md)**
**The Challenge:** The Texas Department of Agriculture (TDA) Food and Nutrition (F&N) Division administers $2.5B+ in federal funding[cite: 3]. For the 2026 program year, a "clean start" migration from legacy TX-UNPS to the modern TANS system has introduced high risks of "data rot" and a 15-day manual reconciliation bottleneck between TANS (claims) and CAPPS (accounting)[cite: 3, 5].

**The Solution:** This project demonstrates an automated pipeline that:
1.  **Eliminates Bottlenecks:** Replaces manual spreadsheets with a real-time BigQuery reconciliation engine[cite: 5].
2.  **Quantifies Fiscal Risk:** Identifies **$6,442.25** in potential disallowed costs from Average Daily Participation (ADP) violations[cite: 3, 6].
3.  **Monitors Cash Flow:** Tracks **$186,164.75** in pending reimbursements currently stalled due to system migration reviews[cite: 6].

---

## **3. Python: Comprehensive ETL & Fiscal Impact Pipeline**
This script performs data sanitization and executes the **Step 4: Fiscal Impact Analysis** to quantify financial exposure[cite: 3].

```python
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
```

---

## **4. SQL: Monthly Grant Reconciliation View**
This BigQuery script creates the "Strategic Source of Truth" for the dashboard[cite: 3, 5, 6].

```sql
CREATE OR REPLACE VIEW `driiiportfolio.tda_fn_data.monthly_grant_reconciliation_view` AS
WITH ClaimsSummary AS (
  SELECT 
    TANS_Org_ID, TX_UNPS_CE_ID, Entity_Name, Program_Type, Claim_Month, Status,
    SUM(Total_Meals_Claimed) AS Total_Meals,
    SUM(Reimbursement_Requested) AS Total_Requested,
    SUM(Potential_Disallowed_Cost) AS Total_Disallowed_Risk,
    SUM(Pending_Cash_Flow_Impact) AS Total_Cash_Flow_Lag
  FROM `driiiportfolio.tda_fn_data.cleansed_tans_claims`
  GROUP BY 1, 2, 3, 4, 5, 6
),
PaymentSummary AS (
  SELECT TANS_Org_ID, SUM(Authorized_Payment_Amount) AS Total_Paid
  FROM `driiiportfolio.tda_fn_data.synthetic_capps_payments`
  GROUP BY 1
)
SELECT 
  c.Entity_Name, c.Program_Type, c.TX_UNPS_CE_ID AS Legacy_ID, c.TANS_Org_ID AS Modern_ID,
  c.Status AS Claim_Status, c.Total_Meals, c.Total_Requested,
  c.Total_Disallowed_Risk AS Projected_Audit_Risk,
  c.Total_Cash_Flow_Lag AS Pending_Payment_Value,
  COALESCE(p.Total_Paid, 0) AS Actual_CAPPS_Disbursement,
  (c.Total_Requested - COALESCE(p.Total_Paid, 0)) AS Budget_Variance,
  CASE 
    WHEN c.Status = 'Pending Review' THEN 'ESCALATE: Review Bottleneck'
    WHEN (c.Total_Requested - COALESCE(p.Total_Paid, 0)) > 0 AND c.Status = 'Approved' THEN 'FLAG: Payment Shortfall'
    WHEN c.TX_UNPS_CE_ID IS NULL THEN 'ALERT: System Migration Orphan'
    ELSE 'Reconciled'
  END AS Reconciliation_Status
FROM ClaimsSummary AS c
LEFT JOIN PaymentSummary AS p ON c.TANS_Org_ID = p.TANS_Org_ID;
```

---

## **5. Looker Studio Command Center (Visual Summary)**
**Introduction Paragraph:**  
The **Executive Fiscal Oversight & Audit Command Center** provides a unified data bridge between TANS claim submissions and CAPPS financial disbursements, specifically engineered to eliminate the 15-day reconciliation bottleneck and ensure seamless data integrity[cite: 3, 5]. By centralizing **$217.29K in unreconciled variance**, **$186.16K in cash flow lag**, and **$6.44K in audit risk**, this dashboard empowers TDA leadership with the actionable intelligence required to prioritize operational reviews[cite: 6].

**Validated KPIs & Visuals:**
*   **Total Unreconciled Variance:** $217,293.26[cite: 6].
*   **Total Potential Disallowed Costs:** $6,442.25[cite: 6].
*   **Pending Cash Flow Lag:** $186,164.75[cite: 6].
*   **Fiscal Risk Heatmap:** Bar chart showing **Projected Audit Risk** by Program Type (NSLP as primary driver)[cite: 6].
*   **Top 10 Entities:** Identifies **Texas School District 31** as the highest risk entity[cite: 6].

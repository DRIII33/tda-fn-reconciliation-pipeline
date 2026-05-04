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

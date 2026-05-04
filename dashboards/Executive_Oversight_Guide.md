# Executive_Oversight_Guide.md

## **Executive Fiscal Oversight & Audit Command Center**
### **Operational Guide for Monthly Grant Reconciliation & Fiscal Monitoring**

**Author:** Daniel Rodriguez III - Financial Data Analyst

---

## **1. Introduction & Strategic Purpose**
The **Executive Fiscal Oversight & Audit Command Center** provides a unified data bridge between TANS claim submissions and CAPPS financial disbursements, specifically engineered to eliminate the 15-day reconciliation bottleneck and ensure seamless data integrity during the division’s system transition[cite: 3, 5]. By centralizing high-impact metrics—including **$217.29K in unreconciled variance**, **$186.16K in migration-driven cash flow lag**, and **$6.44K in potential disallowed costs**—this dashboard empowers TDA Food & Nutrition leadership with the actionable intelligence required to proactively mitigate federal audit exposure and prioritize operational review efforts[cite: 3, 6].

---

## **2. Executive KPI Scorecards (Zone 1)**
*Objective: Real-time visibility into total financial exposure.*

| KPI Name | Current Value | Business Logic |
| :--- | :--- | :--- |
| **Total Unreconciled Variance** | **$217,293.26** | Sum of the gap between TANS requested funds and CAPPS disbursements[cite: 5, 6]. |
| **Total Potential Disallowed Costs** | **$6,442.25** | Quantifies federal audit risk from claims exceeding approved participation (ADP) limits[cite: 3, 6]. |
| **Pending Cash Flow Lag** | **$186,164.75** | Total reimbursement value currently "stuck" in the TANS migration review workflow[cite: 3, 6]. |
| **System Integrity Alert** | **0** | Counts records missing a legacy ID crosswalk; 0 indicates 100% migration mapping[cite: 3, 6]. |

---

## **3. Fiscal Risk & Compliance Visuals (Zone 2)**
*Objective: Tactical oversight of compliance breaches and budget shortfalls.*

### **Projected Audit Risk by Program (Treemap)**
*   **Caption:** The treemap highlights NSLP as the primary risk driver, accounting for over half of the total potential disallowed costs ($3,812.25)[cite: 6].
*   **Action:** Direct Education Service Center (ESC) resources toward NSLP desk reviews to mitigate program-wide findings[cite: 3].

### **Top 10 Entities by Disallowed Cost (Bar Chart)**
*   **Caption:** Texas School District 31 leads the risk profile ($1,712.75), signaling a need for a targeted fiscal intervention[cite: 6].
*   **Action:** Investigate the root cause of ADP violations for these specific high-exposure districts[cite: 3].

### **Reconciliation Status Breakdown (Donut Chart)**
*   **Caption:** While 4% of claims are fully reconciled, the 66% "Payment Shortfall" rate indicates a widespread systemic variance issue requiring policy review[cite: 6].

---

## **4. Migration & System Integrity (Zone 3)**
*Objective: Monitoring the technical health of the TANS "Clean Start" migration.*

### **Pending Review Claims by Program Type**
*   **Caption:** SFSP faces the heaviest administrative burden with 11 claims currently stalled in the TANS review workflow[cite: 3, 6].
*   **Action:** Reallocate Business Management staff to SFSP queues to clear the $186.16K cash flow lag[cite: 3].

### **Migration Orphan Tracker**
*   **Caption:** This table serves as an automated "clean start" audit, ensuring every new TANS ID is successfully mapped to its legacy historical data[cite: 3, 6].
*   **Current State:** 0 records (Success); indicates all modern sites are correctly mapped to legacy CE IDs[cite: 6].

---

## **5. Master Audit Details (Zone 4)**
*Objective: Granular evidence for final payment authorization.*

### **Drill-Through Table**
*   **Usage:** Provides the line-item evidence needed for the Assistant Director to authorize payments or deny non-compliant claims[cite: 5, 6].
*   **Example Outlier:** **Texas School District 30** shows a **$16.08K shortfall** and remains in **"Pending Review"** status, making it the top priority for reconciliation staff[cite: 6].

---

## **6. Technical Configuration Notes**
*   **Data Source:** BigQuery View `monthly_grant_reconciliation_view`[cite: 5].
*   **Calculated Fields:** 
    *   `Projected_Audit_Risk`: Calculated in SQL via ADP breach logic[cite: 3, 5].
    *   `Pending_Payment_Value`: Filtered where `Claim_Status` = 'Pending Review'[cite: 5, 6].
*   **Conditional Formatting:**
    *   **Red:** Applied to `Budget_Variance` > 0 to highlight shortfalls[cite: 6].
    *   **Orange:** Applied to `Projected_Audit_Risk` > 0 to highlight compliance risk[cite: 6].

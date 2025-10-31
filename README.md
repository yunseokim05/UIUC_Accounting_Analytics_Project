# 🧾 UIUC Accounting Analytics Project  
**Automated Financial Audit & Anomaly Detection using Python**

---

## 📘 Overview  
This project automates the **financial audit process** by analyzing transaction data to detect potential accounting anomalies such as:  
- Duplicate invoices  
- Negative or missing entries  
- Weekend transactions  
- Statistically unusual or high-value transactions  

Developed as part of a **data-driven accounting analytics portfolio** at the University of Illinois Urbana-Champaign (UIUC),  
this project demonstrates how **Python-based audit automation** can enhance accuracy and internal controls in financial reporting.

---

## 📊 Key Features  
✅ Automated anomaly detection (duplicate, missing, negative, outlier, high-value)  
✅ Statistical analysis using Z-score and IQR  
✅ Weekend & vendor-based anomaly tagging  
✅ Automated PDF report generation (`Accounting_Audit_Report_UIUC_Portfolio.pdf`)  
✅ Clear executive summary + visual insights (bar charts & histograms)

---

## 🧠 Tech Stack  
| Category | Tools / Libraries |
|-----------|-------------------|
| Language | Python 3.9 |
| Data Analysis | pandas, numpy |
| Visualization | matplotlib |
| Reporting | reportlab |
| Version Control | Git, GitHub |

---

## 📂 Folder Structure  
```
UIUC_Accounting_Analytics_Project/
│
├── 📁 data/ # Input transaction data
│ └── transaction.csv
│
├── 📁 src/ # Core analysis & reporting scripts
│ ├── main.py
│ ├── make_report.py
│ ├── make_report_full.py
│ └── make_report_portfolio.py
│
├── 📁 reports/ # Generated PDF reports
│ ├── Accounting_Audit_Report.pdf
│ ├── Accounting_Audit_Report_FULL.pdf
│ └── Accounting_Audit_Report_UIUC_Portfolio.pdf
│
├── 📁 artifacts/ # Intermediate outputs
│ ├── audit_summary.txt
│ └── audit_summary.xlsx
│
└── 📄 README.md
```

## 📈 Example Output  
The generated PDF report includes:
- **Executive Summary** (detected anomalies overview)  
- **Executive Insights** (weekend, high-value, and duplicate analysis)  
- **Visual Insights** (distribution histograms & vendor analysis charts)

📄 Example:  
`reports/Accounting_Audit_Report_UIUC_Portfolio.pdf`

---

## 🚀 How to Run  
1. Clone the repository  
   ```bash
   git clone https://github.com/yunseokim05/UIUC_Accounting_Analytics_Project.git
   cd UIUC_Accounting_Analytics_Project

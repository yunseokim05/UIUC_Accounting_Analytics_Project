# make_report_full.py — Full 6-page English audit report with visuals
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import date
from textwrap import fill

# 1️⃣ Load data
xls = pd.ExcelFile("audit_summary.xlsx")
sheets = {name: xls.parse(name) for name in xls.sheet_names}

def get(name):
    return sheets.get(name, pd.DataFrame())

raw = get("raw_data")
dup = get("duplicate_invoice")
neg = get("negative_amounts")
miss = get("missing_values")
out_z = get("outliers_z3")
out_iqr = get("outliers_iqr")
over_th = get("over_threshold")
weekend = get("weekend")
empty_vendor = get("empty_vendor")

# 2️⃣ Metrics
metrics = {
    "Duplicate Invoices": len(dup),
    "Negative Amounts": len(neg),
    "Missing Values": len(miss),
    "Outliers (z-score ≥ 3)": len(out_z),
    "Outliers (IQR)": len(out_iqr),
    "Over Threshold (|Amount|>1000)": len(over_th),
    "Weekend Transactions": len(weekend),
    "Empty Vendor": len(empty_vendor)
}

# 3️⃣ Generate PDF
pdf = PdfPages("Accounting_Audit_Report_FULL.pdf")

# ---- PAGE 1: COVER ----
plt.figure(figsize=(8.5,11))
plt.axis("off")

# Title block with better font rendering and spacing
plt.text(0.5,0.8,"ACCOUNTING AUDIT REPORT",ha="center",
         fontsize=28,fontweight="bold",fontname="Helvetica")

plt.text(0.5,0.75,"Automated Anomaly Detection Summary",ha="center",
         fontsize=16,fontname="Helvetica")

# Horizontal line for cleaner layout
plt.hlines(0.72,0.2,0.8,colors="gray",linestyles="dashed",linewidth=0.5)

# Author and metadata
plt.text(0.5,0.66,"Prepared by: Yunseo Kim",ha="center",
         fontsize=12,fontname="Helvetica")
plt.text(0.5,0.63,f"Date: {date.today().strftime('%B %d, %Y')}",ha="center",
         fontsize=12,fontname="Helvetica")
plt.text(0.5,0.6,"University of Illinois Urbana-Champaign",ha="center",
         fontsize=11,fontname="Helvetica")
plt.text(0.5,0.56,"Dataset: transaction.csv (Sample of Accounting Transactions)",ha="center",
         fontsize=10,fontname="Helvetica")

# Add UIUC-style blue line at the bottom
plt.hlines(0.12,0.1,0.9,colors="#13294B",linewidth=4)
plt.text(0.5,0.09,"Gies College of Business | Accountancy + Data Science",ha="center",
         fontsize=10,color="#13294B",fontname="Helvetica")

pdf.savefig(); plt.close()

# ---- PAGE 2: EXECUTIVE SUMMARY ----
plt.figure(figsize=(8.5,11))
plt.axis("off")

# 1) 제목 — 한 번만, 헬베티카로
plt.text(0.1, 0.92, "EXECUTIVE SUMMARY",
         fontsize=18, fontweight="bold", fontname="Helvetica")

# 2) 본문 — textwrap으로 수동 줄바꿈 (wrap=True 사용 안함)
summary = (
    "This automated audit analyzes financial transaction data to detect potential anomalies "
    "such as duplicate invoices, negative amounts, missing fields, outliers, weekend transactions, "
    "and unusually high-value entries. The purpose is to assist accounting teams in quickly identifying "
    "data integrity risks and operational irregularities."
)
plt.text(0.1, 0.86, fill(summary, 100),
         fontsize=11, fontname="Helvetica", va="top")

# 3) 메트릭 섹션
plt.text(0.1, 0.70, "Detected Anomalies Summary:",
         fontsize=12, fontweight="bold", fontname="Helvetica")

y = 0.66
for k, v in metrics.items():
    plt.text(0.12, y, f"- {k}: {v}",
             fontsize=11, fontname="Helvetica")
    y -= 0.035

pdf.savefig(); plt.close()

# ---- PAGE 3: VISUAL INSIGHTS ----
plt.figure(figsize=(11,8.5))
plt.suptitle("Visual Insights",fontsize=18,fontweight="bold")

# Left: Histogram of Amounts
plt.subplot(1,2,1)
raw["Amount"].hist(bins=10)
plt.title("Transaction Amount Distribution")
plt.xlabel("Amount"); plt.ylabel("Frequency")

# Right: Total Amount by Vendor
if "Vendor" in raw.columns and "Amount" in raw.columns:
    vendor_sum = raw.groupby("Vendor")["Amount"].sum().sort_values(ascending=False).head(5)
    vendor_sum.plot(kind="bar",ax=plt.subplot(1,2,2))
    plt.title("Top 5 Vendors by Total Amount")
    plt.ylabel("Total Amount")
pdf.savefig(); plt.close()

# ---- PAGE 4: TOP 3 ANOMALIES ----
plt.figure(figsize=(8.5,11))
plt.axis("off")
plt.text(0.1,0.9,"Top 3 Anomalies",fontsize=18,fontweight="bold")
plt.text(0.1,0.85,"These represent transactions requiring immediate review or confirmation.",fontsize=11)

# Combine anomalies & pick top rows
combined = pd.concat([dup,neg,miss,out_iqr,over_th,weekend,empty_vendor], ignore_index=True)
if not combined.empty:
    top3 = combined.head(3).astype(str)
    start_y = 0.78
    for i,row in top3.iterrows():
        plt.text(0.1,start_y - i*0.15,
                 f"Invoice_ID: {row.get('Invoice_ID','N/A')}\n"
                 f"Vendor: {row.get('Vendor','N/A')} | Amount: {row.get('Amount','N/A')}\n"
                 f"Category: {row.get('Category','N/A')} | Date: {row.get('Date','N/A')}",
                 fontsize=10,bbox=dict(facecolor='whitesmoke',edgecolor='grey',boxstyle='round,pad=0.5'))
else:
    plt.text(0.1,0.75,"(No anomalies detected in dataset)",fontsize=11)
pdf.savefig(); plt.close()

# ---- PAGE 5: RECOMMENDATIONS ----
plt.figure(figsize=(8.5,11))
plt.axis("off")
plt.text(0.1,0.9,"Recommendations",fontsize=18,fontweight="bold")
reco = [
    "1) Enforce mandatory Vendor field validation.",
    "2) Check for duplicate invoice IDs before posting transactions.",
    "3) Review and approve all weekend or high-value transactions.",
    "4) Investigate missing fields for data entry issues.",
    "5) Implement automated alerts for statistical outliers."
]
for i,txt in enumerate(reco):
    plt.text(0.1,0.82 - i*0.05,txt,fontsize=11)
pdf.savefig(); plt.close()

# ---- PAGE 6: APPENDIX ----
plt.figure(figsize=(11,8.5))
plt.axis("off")
plt.text(0.1,0.9,"Appendix: Anomaly Tables (First 10 Rows Each)",fontsize=16,fontweight="bold")

start_y = 0.82
tables = [("Duplicate Invoices",dup),("Negative Amounts",neg),
          ("Missing Values",miss),("Outliers (IQR)",out_iqr),
          ("Weekend Transactions",weekend)]
y = start_y
for title,df in tables:
    plt.text(0.1,y,title,fontsize=12,fontweight="bold")
    y -= 0.03
    if not df.empty:
        for _,r in df.head(2).iterrows():
            plt.text(0.12,y,f"{r.to_dict()}",fontsize=9)
            y -= 0.03
    else:
        plt.text(0.12,y,"(none)",fontsize=9)
        y -= 0.03
    y -= 0.03
pdf.savefig(); plt.close()

pdf.close()
print("✅ Full English PDF generated: Accounting_Audit_Report_FULL.pdf")
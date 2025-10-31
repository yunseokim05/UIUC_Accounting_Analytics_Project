# make_report_portfolio.py — UIUC Portfolio Edition (stable layout)

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import date
from textwrap import fill
import matplotlib as mpl

# ---- Global font/render settings (선명/안정) ----
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype']  = 42
mpl.rcParams['font.family']  = 'Helvetica'   # mac 기본 내장, 없으면 'DejaVu Sans'로 바꿔도 됨
mpl.rcParams['figure.dpi']   = 300

UIUC_BLUE   = "#13294B"
UIUC_ORANGE = "#E84A27"

# ---------- Load Excel produced by main.py ----------
xls = pd.ExcelFile("audit_summary.xlsx")
sheets = {name: xls.parse(name) for name in xls.sheet_names}

def get(name): return sheets.get(name, pd.DataFrame())

raw         = get("raw_data")
dup         = get("duplicate_invoice")
neg         = get("negative_amounts")
miss        = get("missing_values")
out_z       = get("outliers_z3")
out_iqr     = get("outliers_iqr")
over_th     = get("over_threshold")
weekend     = get("weekend")
empty_vendor= get("empty_vendor")

# ---------- Metrics ----------
metrics = [
    ("Total Records", len(raw) if isinstance(raw, pd.DataFrame) else 0),
    ("Duplicate Invoices", len(dup)),
    ("Negative Amounts", len(neg)),
    ("Missing Values", len(miss)),
    ("Outliers (z-score ≥ 3)", len(out_z)),
    ("Outliers (IQR)", len(out_iqr)),
    ("Over Threshold (|Amount| > 1000)", len(over_th)),
    ("Weekend Transactions", len(weekend)),
    ("Empty Vendor", len(empty_vendor)),
]
total_anoms = sum(v for k, v in metrics if k != "Total Records")
wknd_rate   = (len(weekend)/total_anoms*100) if total_anoms else 0
high_rate   = (len(over_th)/total_anoms*100) if total_anoms else 0
dup_top_vendors = (
    dup.groupby("Vendor")["Invoice_ID"].count().sort_values(ascending=False).head(3)
    if isinstance(dup, pd.DataFrame) and not dup.empty else pd.Series(dtype=int)
)

def bullet_list(ax, x, y, items, step=0.055, fs=11):
    for i, txt in enumerate(items):
        ax.text(x, y - i*step, f"- {txt}", fontsize=fs)

# =============== Build PDF ===============
pdf = PdfPages("Accounting_Audit_Report_UIUC_Portfolio.pdf")

# ---- PAGE 1: COVER ----
fig = plt.figure(figsize=(8.5, 11)); ax = plt.gca(); ax.axis("off")
ax.add_patch(plt.Rectangle((0, 0.92), 1, 0.08, color=UIUC_BLUE, transform=ax.transAxes))
ax.add_patch(plt.Rectangle((0, 0.915), 1, 0.005, color=UIUC_ORANGE, transform=ax.transAxes))
ax.text(0.5, 0.86, "ACCOUNTING AUDIT REPORT", ha="center", fontsize=28, fontweight="bold", color="white")
ax.text(0.5, 0.82, "Automated Anomaly Detection (Python, pandas)", ha="center", fontsize=13, color="white")
ax.text(0.5, 0.68, "Prepared by: Yunseo Kim", ha="center", fontsize=12)
ax.text(0.5, 0.65, f"Date: {date.today().strftime('%B %d, %Y')}", ha="center", fontsize=12)
ax.text(0.5, 0.62, "University of Illinois Urbana-Champaign | Gies College of Business", ha="center", fontsize=11)
ax.text(0.5, 0.56, "Dataset: transaction.csv (Sample of Accounting Transactions)", ha="center", fontsize=10)
ax.add_patch(plt.Rectangle((0.1, 0.09), 0.8, 0.01, color=UIUC_BLUE, transform=ax.transAxes))
ax.text(0.5, 0.06, "Accountancy + Data Science", ha="center", fontsize=10, color=UIUC_BLUE)
pdf.savefig(); plt.close()


# ---- PAGE 2: EXECUTIVE SUMMARY ----
import numpy as np

fig = plt.figure(figsize=(8.5, 11))
ax = fig.add_axes([0, 0, 1, 1])  # figure 좌표계 (0~1)
ax.axis("off")

# 1) 제목
fig.text(0.10, 0.92, "EXECUTIVE SUMMARY", fontsize=18, fontweight="bold")

# 2) 요약 문단 (고정 위치)
summary = (
    "This automated audit analyzes financial transaction data to detect potential anomalies "
    "such as duplicate invoices, negative amounts, missing fields, statistical outliers, "
    "weekend transactions, and unusually high-value entries. The goal is to help accounting teams "
    "quickly identify data integrity risks and strengthen internal controls."
)
from textwrap import fill
fig.text(0.10, 0.865, fill(summary, 95), fontsize=12, va="top")

# 3) Detected Anomalies Summary (표로 고정 렌더링)
#    -> 좌표 꼬임 없이 항상 보이도록
summary_rows = [(k, str(v)) for k, v in metrics]
summary_df = pd.DataFrame(summary_rows, columns=["Metric", "Count"])

ax_tbl = fig.add_axes([0.10, 0.58, 0.80, 0.22])  # [left, bottom, width, height]
ax_tbl.axis("off")
tbl = ax_tbl.table(
    cellText=summary_df.values,
    colLabels=summary_df.columns,
    loc="upper left",
    cellLoc="left",
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(10.5)
tbl.scale(1.0, 1.3)  # 세로 간격 약간 확대

# 4) 구분선
ax.plot([0.10, 0.90], [0.52, 0.52], transform=fig.transFigure, color="#E0E3E7", linewidth=1)
# 5) Executive Insights 박스 (항상 같은 위치)
box_left, box_bottom, box_w, box_h = 0.10, 0.25, 0.80, 0.22
fig.patches.append(plt.Rectangle((box_left, box_bottom), box_w, box_h,
                                 transform=fig.transFigure, facecolor="#F7F8FA", edgecolor="none"))
fig.text(0.12, box_bottom + box_h - 0.04, "Executive Insights",
         fontsize=12, fontweight="bold", color=UIUC_BLUE)

# 퍼센트 계산(0 division 대비)
total_anoms = sum(v for k, v in metrics if k != "Total Records")
wknd_rate = (len(weekend) / total_anoms * 100) if total_anoms else 0
high_rate = (len(over_th) / total_anoms * 100) if total_anoms else 0
dup_top_vendors = (
    dup.groupby("Vendor")["Invoice_ID"].count().sort_values(ascending=False).head(3)
    if isinstance(dup, pd.DataFrame) and not dup.empty else pd.Series(dtype=int)
)

insights = [
    f"Weekend-related anomalies: {wknd_rate:.1f}% of total detected.",
    f"High-value (|Amount| > 1000): {high_rate:.1f}% of total detected.",
    ("Top duplicate vendors: " + ", ".join([f"{idx} ({val})" for idx, val in dup_top_vendors.items()]))
        if not dup_top_vendors.empty else "No duplicate vendors with multiple occurrences.",
]
y = box_bottom + box_h - 0.085
for tip in insights:
    fig.text(0.12, y, f"- {tip}", fontsize=11)
    y -= 0.055

pdf.savefig(); plt.close()

# ---- PAGE 3: VISUAL INSIGHTS ----
plt.figure(figsize=(11, 8.5))
plt.suptitle("Visual Insights", fontsize=18, fontweight="bold")

# Left: Histogram
plt.subplot(1, 2, 1)
if isinstance(raw, pd.DataFrame) and "Amount" in raw.columns:
    raw["Amount"].hist(bins=10, color="#1f77b4", edgecolor="black")
plt.title("Transaction Amount Distribution")
plt.xlabel("Amount")
plt.ylabel("Frequency")

# Right: Bar chart of Vendor totals
plt.subplot(1, 2, 2)
if isinstance(raw, pd.DataFrame) and {"Vendor", "Amount"}.issubset(raw.columns):
    vendor_sum = (
        raw.groupby("Vendor")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    vendor_sum.plot(kind="bar", color="#1f77b4", edgecolor="black")
    plt.title("Top Vendors by Total Amount")
    plt.ylabel("Total Amount")
    plt.xlabel("Vendor")

    # ✅ 아래 추가 부분: 글자 겹침 방지 + 잘림 방지
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # 여백 확보 (특히 아래쪽)

pdf.savefig()
plt.close()

# ---- PAGE 4: TOP 3 ANOMALIES ----
plt.figure(figsize=(8.5, 11)); plt.axis("off")
plt.text(0.1, 0.92, "Top 3 Anomalies", fontsize=18, fontweight="bold")
plt.text(0.1, 0.88, "Transactions requiring immediate review.", fontsize=11)

frames = [df for df in [dup, neg, miss, out_z, out_iqr, over_th, weekend, empty_vendor] if isinstance(df, pd.DataFrame) and not df.empty]
combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
if not combined.empty:
    for i, (_, row) in enumerate(combined.head(3).astype(str).iterrows()):
        block = (
            f"Invoice_ID: {row.get('Invoice_ID','N/A')}\n"
            f"Vendor: {row.get('Vendor','N/A')}  |  Amount: {row.get('Amount','N/A')}\n"
            f"Category: {row.get('Category','N/A')}  |  Date: {row.get('Date','N/A')}"
        )
        plt.text(0.1, 0.80 - i*0.18, block, fontsize=10,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="whitesmoke", edgecolor="grey"))
else:
    plt.text(0.1, 0.78, "(No anomalies detected)", fontsize=11)
pdf.savefig(); plt.close()

# ---- PAGE 5: RECOMMENDATIONS ----
fig = plt.figure(figsize=(8.5, 11)); ax = plt.gca(); ax.axis("off")
ax.text(0.1, 0.92, "Recommendations", fontsize=18, fontweight="bold")
reco = [
    "Enforce mandatory Vendor field validation with dropdowns.",
    "Validate uniqueness of Invoice_ID before posting.",
    "Require secondary approval for high-value or weekend transactions.",
    "Block uploads with critical missing fields; provide error report.",
    "Monitor statistical outliers monthly and investigate root causes.",
]
bullet_list(ax, 0.1, 0.86, reco, step=0.06, fs=11)
pdf.savefig(); plt.close()

# ---- PAGE 6: APPENDIX ----
plt.figure(figsize=(11, 8.5)); plt.axis("off")
plt.text(0.1, 0.92, "Appendix: Anomaly Samples (First 10 Rows Each)", fontsize=16, fontweight="bold")
start_y = 0.86
sections = [("Duplicate Invoices", dup), ("Negative Amounts", neg), ("Missing Values", miss),
            ("Outliers (IQR)", out_iqr), ("Weekend Transactions", weekend)]
y = start_y
for title, df in sections:
    plt.text(0.1, y, title, fontsize=12, fontweight="bold"); y -= 0.03
    if isinstance(df, pd.DataFrame) and not df.empty:
        for _, r in df.head(2).astype(str).iterrows():
            plt.text(0.12, y, f"{r.to_dict()}", fontsize=9); y -= 0.03
    else:
        plt.text(0.12, y, "(none)", fontsize=9); y -= 0.03
    y -= 0.03
pdf.savefig(); plt.close()

pdf.close()
print("✅ UIUC Portfolio PDF generated: Accounting_Audit_Report_UIUC_Portfolio.pdf")
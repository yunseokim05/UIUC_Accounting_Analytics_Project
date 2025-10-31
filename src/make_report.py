# make_report.py — Generate an ENGLISH PDF from audit_summary.xlsx (reportlab)

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors

# -------- Load Excel (produced by main.py) --------
xls = pd.ExcelFile("audit_summary.xlsx")
sheets = {name: xls.parse(name) for name in xls.sheet_names}

def get_sheet(name):
    return sheets.get(name, pd.DataFrame())

raw = get_sheet("raw_data")
dup = get_sheet("duplicate_invoice")
neg = get_sheet("negative_amounts")
miss = get_sheet("missing_values")
out_z = get_sheet("outliers_z3")
out_iqr = get_sheet("outliers_iqr")
over_th = get_sheet("over_threshold")
weekend = get_sheet("weekend")
empty_vendor = get_sheet("empty_vendor")

# -------- Metrics --------
total_rows = len(raw) if isinstance(raw, pd.DataFrame) else 0
metrics = [
    ("Total Records", total_rows),
    ("Duplicate Invoices", len(dup)),
    ("Negative Amounts", len(neg)),
    ("Missing Values", len(miss)),
    ("Outliers (z-score ≥ 3)", len(out_z)),
    ("Outliers (IQR)", len(out_iqr)),
    ("Over Threshold (|Amount| > 1000)", len(over_th)),
    ("Weekend Transactions", len(weekend)),
    ("Empty Vendor", len(empty_vendor)),
]

# -------- PDF Styles (English only) --------
doc = SimpleDocTemplate(
    "Accounting_Audit_Report.pdf",
    pagesize=A4,
    rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36,
)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1", fontSize=18, leading=24, spaceAfter=12, alignment=1))  # centered
styles.add(ParagraphStyle(name="H2", fontSize=14, leading=20, spaceAfter=8))
styles.add(ParagraphStyle(name="Body", fontSize=11, leading=16))

story = []

# -------- Cover / Title --------
story.append(Paragraph("Accounting Audit Report", styles["H1"]))
story.append(Paragraph("Automated Anomaly Detection Summary", styles["H2"]))
story.append(Spacer(1, 6))

# -------- Executive Summary (English) --------
summary = (
    "This report summarizes automated anomaly detection over the uploaded transaction data. "
    "The system flags duplicate invoices, negative amounts, missing fields, statistical outliers "
    "(both z-score and IQR methods), high-value threshold exceptions, weekend transactions, "
    "and empty vendor entries. Use these flags to prioritize review, validate approvals, and "
    "improve input controls."
)
story.append(Paragraph(summary, styles["Body"]))
story.append(Spacer(1, 12))

# -------- Metrics Table --------
tbl_data = [["Category", "Count"]] + [[k, str(v)] for k, v in metrics]
tbl = Table(tbl_data, colWidths=[260, 100])
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#333333")),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
]))
story.append(tbl)
story.append(Spacer(1, 18))

# -------- Recommendations (English) --------
reco = (
    "<b>Recommendations</b><br/>"
    "1) Enforce mandatory vendor input and standardized dropdowns.<br/>"
    "2) Validate unique invoice IDs to prevent duplicates.<br/>"
    "3) Add threshold-based alerts and second-level approvals for high-value transactions.<br/>"
    "4) Review weekend/off-hours approvals with audit logs.<br/>"
    "5) Auto-flag and block uploads with critical missing fields."
)
story.append(Paragraph(reco, styles["Body"]))
story.append(PageBreak())

# -------- Helper: render small table for each anomaly sheet --------
def add_table_for(df: pd.DataFrame, title: str):
    story.append(Paragraph(title, styles["H2"]))
    if isinstance(df, pd.DataFrame) and not df.empty:
        df_show = df.copy().head(20).astype(str)  # limit & stringify
        table_data = [list(df_show.columns)] + df_show.values.tolist()
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("(none)", styles["Body"]))
    story.append(Spacer(1, 16))

# -------- Detail sections (English titles) --------
add_table_for(dup, "Duplicate Invoices")
add_table_for(neg, "Negative Amounts")
add_table_for(miss, "Missing Values")
add_table_for(out_z, "Outliers (z-score ≥ 3)")
add_table_for(out_iqr, "Outliers (IQR)")
add_table_for(over_th, "Over Threshold (|Amount| > 1000)")
add_table_for(weekend, "Weekend Transactions")
add_table_for(empty_vendor, "Empty Vendor")

# -------- Build PDF --------
doc.build(story)
print("✅ PDF generated: Accounting_Audit_Report.pdf")
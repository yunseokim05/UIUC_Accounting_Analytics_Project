import pandas as pd
import numpy as np

# 0) 데이터 로드
df = pd.read_csv("transaction.csv")

# 1) 기본 오류 탐지
duplicates = df[df.duplicated(subset=["Invoice_ID"], keep=False)]
negative_amounts = df[df["Amount"] < 0]
missing_values = df[df.isnull().any(axis=1)]

# 2) 이상치 탐지 — Z-score와 IQR 2가지 방식
amt = df["Amount"]
std0 = amt.std(ddof=0) if amt.std(ddof=0) != 0 else 1
z = (amt - amt.mean()) / std0
outliers_z3 = df[np.abs(z) >= 3]

Q1, Q3 = amt.quantile(0.25), amt.quantile(0.75)
IQR = Q3 - Q1
lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
outliers_iqr = df[(amt < lower) | (amt > upper)]

# 3) 규칙 기반 플래그(업무 룰 예시)
threshold_flag = df[np.abs(df["Amount"]) > 1000]     # 금액 임계치(|Amount|>1000)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
weekend_flag = df[df["Date"].dt.dayofweek.isin([5, 6])]  # 주말 거래(토=5, 일=6)
empty_vendor_flag = df[df["Vendor"].isnull() | (df["Vendor"].astype(str).str.strip() == "")]

# 4) 콘솔 요약 출력
print("📌 중복 송장:\n", duplicates, "\n")
print("📌 음수 금액 거래:\n", negative_amounts, "\n")
print("📌 누락된 값:\n", missing_values, "\n")
print("📌 이상치(z>=3):\n", outliers_z3, "\n")
print("📌 이상치(IQR):\n", outliers_iqr, "\n")
print("📌 금액 임계치(>|1000|):\n", threshold_flag, "\n")
print("📌 주말 거래:\n", weekend_flag, "\n")
print("📌 Vendor 미기재:\n", empty_vendor_flag, "\n")

# 5) 파일 저장 (엑셀 + 텍스트)
with pd.ExcelWriter("audit_summary.xlsx", engine="xlsxwriter") as xw:
    df.to_excel(xw, sheet_name="raw_data", index=False)
    duplicates.to_excel(xw, sheet_name="duplicate_invoice", index=False)
    negative_amounts.to_excel(xw, sheet_name="negative_amounts", index=False)
    missing_values.to_excel(xw, sheet_name="missing_values", index=False)
    outliers_z3.to_excel(xw, sheet_name="outliers_z3", index=False)
    outliers_iqr.to_excel(xw, sheet_name="outliers_iqr", index=False)
    threshold_flag.to_excel(xw, sheet_name="over_threshold", index=False)
    weekend_flag.to_excel(xw, sheet_name="weekend", index=False)
    empty_vendor_flag.to_excel(xw, sheet_name="empty_vendor", index=False)

with open("audit_summary.txt", "w", encoding="utf-8") as f:
    def write_block(name, df_):
        f.write(f"\n--- {name} ({len(df_)}) ---\n")
        f.write(df_.to_string(index=False) if not df_.empty else "(none)")
        f.write("\n")

    f.write("Accounting Error Detection Summary\n")
    write_block("duplicate_invoice", duplicates)
    write_block("negative_amounts", negative_amounts)
    write_block("missing_values", missing_values)
    write_block("outliers_z3", outliers_z3)
    write_block("outliers_iqr", outliers_iqr)
    write_block("over_threshold(|Amount|>1000)", threshold_flag)
    write_block("weekend", weekend_flag)
    write_block("empty_vendor", empty_vendor_flag)
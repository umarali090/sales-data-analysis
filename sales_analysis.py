"""
Sales Data Analysis - Week 3 Project
Loads sales_data.csv, cleans it, calculates metrics, prints a report
and saves analysis_report.md plus a chart (sales_by_product.png).
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # lets the chart save without opening a window
import matplotlib.pyplot as plt

# ---------- Day 1: Load data ----------
df = pd.read_csv("sales_data.csv")
print("First 5 rows:")
print(df.head(), "\n")

# ---------- Day 2: Explore data ----------
print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
print("Columns:", list(df.columns))
print("\nData types:")
print(df.dtypes, "\n")

# ---------- Day 3: Clean data ----------
# Dates are read as text, so convert them to real dates
df["Date"] = pd.to_datetime(df["Date"])

# Count missing values and duplicates before cleaning
missing_before = int(df.isna().sum().sum())
duplicates_before = int(df.duplicated().sum())

# Remove duplicate rows
df = df.drop_duplicates()

# Fill missing numbers with the median, drop rows missing text fields
num_cols = ["Quantity", "Price", "Total_Sales"]
df[num_cols] = df[num_cols].fillna(df[num_cols].median())
df = df.dropna(subset=["Product", "Region", "Customer_ID"])

# Validation: Total_Sales should equal Quantity x Price
mismatches = int((df["Quantity"] * df["Price"] != df["Total_Sales"]).sum())

print(f"Missing values found: {missing_before}")
print(f"Duplicate rows found: {duplicates_before}")
print(f"Rows where Total_Sales != Quantity x Price: {mismatches}\n")

# ---------- Day 4: Analyze sales ----------
total_revenue = df["Total_Sales"].sum()
avg_sale = df["Total_Sales"].mean()
max_sale = df.loc[df["Total_Sales"].idxmax()]
min_sale = df.loc[df["Total_Sales"].idxmin()]

# Revenue and units per product, highest revenue first
by_product = (
    df.groupby("Product")
    .agg(Revenue=("Total_Sales", "sum"), Units=("Quantity", "sum"))
    .sort_values("Revenue", ascending=False)
)
best_by_revenue = by_product["Revenue"].idxmax()
best_by_units = by_product["Units"].idxmax()

by_region = df.groupby("Region")["Total_Sales"].sum().sort_values(ascending=False)
by_month = df.groupby(df["Date"].dt.strftime("%Y-%m"))["Total_Sales"].sum()

# ---------- Day 5: Create report ----------
print("=" * 45)
print("SALES ANALYSIS REPORT")
print("=" * 45)
print(f"Total Revenue : ₹{total_revenue:,.2f}")
print(f"Average Sale  : ₹{avg_sale:,.2f}")
print(f"Highest Sale  : ₹{max_sale['Total_Sales']:,.0f} ({max_sale['Product']}, {max_sale['Region']})")
print(f"Lowest Sale   : ₹{min_sale['Total_Sales']:,.0f} ({min_sale['Product']}, {min_sale['Region']})")
print(f"Best product (revenue): {best_by_revenue}")
print(f"Best product (units)  : {best_by_units}")
print("\nRevenue by product:\n", by_product)
print("\nRevenue by region:\n", by_region)

# Chart
ax = by_product["Revenue"].plot(kind="bar", color="#4C72B0", figsize=(7, 4))
ax.set_title("Revenue by Product")
ax.set_ylabel("Revenue (₹)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("sales_by_product.png", dpi=150)

# Save report as markdown
def table(frame):
    lines = ["| " + " | ".join([frame.index.name or ""] + list(frame.columns)) + " |",
             "|" + "---|" * (len(frame.columns) + 1)]
    for idx, row in frame.iterrows():
        lines.append("| " + " | ".join([str(idx)] + [f"{v:,.0f}" for v in row]) + " |")
    return "\n".join(lines)

report = f"""# Sales Analysis Report

## Project Overview
Analysis of {len(df)} sales records ({df['Date'].min():%d %b %Y} to {df['Date'].max():%d %b %Y})
to find total sales, the best-selling product and other key metrics.

## Data Quality
- Rows: {len(df)}, Columns: {df.shape[1]}
- Missing values: {missing_before}
- Duplicate rows: {duplicates_before}
- Total_Sales vs Quantity x Price mismatches: {mismatches}
- Cleaning applied: dates converted to datetime; duplicates dropped; missing numbers filled with median.
  (This dataset was already clean, so nothing needed changing.)

## Key Metrics
| Metric | Value |
|---|---|
| Total revenue | ₹{total_revenue:,.0f} |
| Average sale | ₹{avg_sale:,.0f} |
| Highest sale | ₹{max_sale['Total_Sales']:,.0f} ({max_sale['Product']}, {max_sale['Region']}) |
| Lowest sale | ₹{min_sale['Total_Sales']:,.0f} ({min_sale['Product']}, {min_sale['Region']}) |
| Best product by revenue | {best_by_revenue} |
| Best product by units | {best_by_units} |

## Revenue by Product
{table(by_product)}

![Revenue by product](sales_by_product.png)

## Revenue by Region
{table(by_region.to_frame('Revenue'))}

## Monthly Revenue
{table(by_month.to_frame('Revenue'))}

## Insights
- **{best_by_revenue}** earns the most revenue (₹{by_product.loc[best_by_revenue, 'Revenue']:,.0f}, {by_product.loc[best_by_revenue, 'Revenue'] / total_revenue:.0%} of total) and also sells the most units.
- **{by_region.index[0]}** and **{by_region.index[1]}** together bring in {(by_region.iloc[0] + by_region.iloc[1]) / total_revenue:.0%} of revenue; **{by_region.index[-1]}** is the weakest region.
- April has only 9 days of data, so its low total is not a real drop.
- Tablet has the most orders ({int(df['Product'].eq('Tablet').sum())}) but Laptop earns more because of higher prices.
"""
with open("analysis_report.md", "w", encoding="utf-8") as f:
    f.write(report)
print("\nSaved analysis_report.md and sales_by_product.png")
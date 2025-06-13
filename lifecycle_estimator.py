import streamlit as st
import altair as alt
import pandas as pd
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Lifecycle Cost Estimator", layout="centered")
st.title("🔧 Lifecycle Cost Estimator for Industrial Equipment")

st.markdown("""
This app calculates and compares lifecycle costs using Net Present Value (NPV).

- Upload a CSV with multiple machines for comparison  
- Or enter details manually to calculate and export cost reports
""")

# === Helper: NPV calculation ===
def npv(cost_per_cycle, total_cycles, cycle_years, rate_percent):
    rate = rate_percent / 100
    return sum(cost_per_cycle / ((1 + rate) ** (cycle_years * i)) for i in range(1, int(total_cycles) + 1))

# === Helper: PDF report generator ===
from fpdf import FPDF

def generate_pdf_report(df, total_cost, equipment, discount):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Lifecycle Cost Report", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Equipment: {equipment}", ln=1)
    pdf.cell(200, 10, txt=f"Discount Rate: {discount}%", ln=1)
    pdf.cell(200, 10, txt=f"NPV Total Cost: Rs. {total_cost:,.2f}", ln=1)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, "Component", border=1)
    pdf.cell(60, 10, "Amount (Rs.)", border=1, ln=1)

    pdf.set_font("Arial", size=12)
    for index, row in df.iterrows():
        component = row["Cost Component"]
        amount = f"{row['Amount']:,.2f}"
        pdf.cell(100, 10, component, border=1)
        pdf.cell(60, 10, f"Rs. {amount}", border=1, ln=1)

    return pdf.output(dest='S').encode('latin1')


# === CSV Upload for Comparison ===
st.markdown("### 📁 Upload CSV to Compare Equipment")

uploaded_file = st.file_uploader("Upload a CSV file with multiple equipment", type=["csv"])

if uploaded_file:
    compare_df = pd.read_csv(uploaded_file)
    results = []

    for _, row in compare_df.iterrows():
        name = row["Equipment"]
        initial = row["Initial Cost"]
        maint = row["Maintenance Cost"]
        maint_int = row["Maintenance Interval"]
        repl = row["Replacement Cost"]
        repl_int = row["Replacement Interval"]
        reuse = row["Reuse Rate"]
        life = row["Operating Life"]
        down = row["Downtime Cost"]
        disc = row["Discount Rate"]

        num_maintenance = (life * 12) // maint_int
        num_replacements = life // repl_int
        reuse_value = reuse / 100 * initial

        maint_npv = npv(maint, num_maintenance, maint_int / 12, disc)
        repl_npv = npv(repl, num_replacements, repl_int, disc)
        down_npv = npv(down, life, 1, disc)

        total_cost = initial + maint_npv + repl_npv + down_npv - reuse_value

        results.append({
            "Equipment": name,
            "NPV Lifecycle Cost (₹)": total_cost
        })

    result_df = pd.DataFrame(results)
    st.markdown("### 📊 Comparison of NPV Lifecycle Costs")
    st.dataframe(result_df)

    chart = alt.Chart(result_df).mark_bar().encode(
        x=alt.X("Equipment", sort="-y"),
        y="NPV Lifecycle Cost (₹)",
        color="Equipment"
    ).properties(width=600)

    st.altair_chart(chart, use_container_width=True)

st.markdown("---")

# === Manual Form Mode ===
st.markdown("### 🧮 Calculate Lifecycle Cost Manually")

st.sidebar.header("Enter Parameters")

equipment_name = st.sidebar.text_input("Equipment Name", "Diesel Generator")
initial_cost = st.sidebar.number_input("Initial Cost (₹)", min_value=0)
maintenance_cost = st.sidebar.number_input("Maintenance Cost per Cycle (₹)", min_value=0)
maintenance_interval = st.sidebar.number_input("Maintenance Interval (months)", min_value=1, value=6)
replacement_cost = st.sidebar.number_input("Replacement Cost (₹)", min_value=0)
replacement_interval = st.sidebar.number_input("Replacement Interval (years)", min_value=1, value=5)
reuse_rate = st.sidebar.slider("Reuse Rate (%)", 0, 100, 20)
operating_life = st.sidebar.number_input("Operating Life (years)", min_value=1, value=10)
downtime_cost = st.sidebar.number_input("Downtime Cost Per Year (optional ₹)", min_value=0)
discount_rate = st.sidebar.slider("Discount Rate (% per year)", 0.0, 15.0, 6.0)

num_maintenance = (operating_life * 12) // maintenance_interval
num_replacements = operating_life // replacement_interval
reuse_value = reuse_rate / 100 * initial_cost

maintenance_years = maintenance_interval / 12
maintenance_npv = npv(maintenance_cost, num_maintenance, maintenance_years, discount_rate)
replacement_npv = npv(replacement_cost, num_replacements, replacement_interval, discount_rate)
downtime_npv = npv(downtime_cost, operating_life, 1, discount_rate) if downtime_cost else 0

total_npv_cost = (
    initial_cost +
    maintenance_npv +
    replacement_npv +
    downtime_npv -
    reuse_value
)

# === Output ===
st.subheader(f"🧾 NPV-Adjusted Lifecycle Cost for {equipment_name}")
st.metric("Net Present Value (₹)", f"{total_npv_cost:,.2f}")

breakdown_df = pd.DataFrame({
    "Cost Component": [
        "Initial Cost",
        "Maintenance (NPV)",
        "Replacement (NPV)",
        "Downtime (NPV)",
        "Reuse Savings"
    ],
    "Amount": [
        initial_cost,
        maintenance_npv,
        replacement_npv,
        downtime_npv,
        -reuse_value
    ]
})

st.markdown("### 📋 Cost Breakdown")
st.dataframe(breakdown_df.set_index("Cost Component"))

# === Download Buttons ===
st.download_button(
    label="⬇️ Download Breakdown as CSV",
    data=breakdown_df.to_csv(index=False),
    file_name=f"{equipment_name.lower().replace(' ', '_')}_lifecycle_cost.csv",
    mime="text/csv"
)

pdf_data = generate_pdf_report(breakdown_df, total_npv_cost, equipment_name, discount_rate)
st.download_button(
    label="⬇️ Download Report as PDF",
    data=pdf_data,
    file_name=f"{equipment_name.lower().replace(' ', '_')}_lifecycle_cost.pdf",
    mime="application/pdf"
)

st.markdown("---")
st.caption("Built by Anoushka · Compare, calculate and export lifecycle cost reports.")

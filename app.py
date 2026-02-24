import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Provisional Natality Data Dashboard")
st.subheader("Birth Analysis by State and Gender")

try:
    df = pd.read_csv("Provisional_Natality_2025_CDC.csv")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    field_map = {}
    required = ["state_of_residence", "month", "month_code", "year_code", "sex_of_infant", "births"]
    for field in required:
        if field in df.columns:
            field_map[field] = field
        else:
            match = next((c for c in df.columns if field.replace("_", "") in c.replace("_", "")), None)
            if match:
                field_map[field] = match

    missing = [f for f in required if f not in field_map]
    if missing:
        st.error(f"Missing required fields: {missing}")
        st.write(df.columns)
        st.stop()

    if field_map != {f: f for f in required}:
        df = df.rename(columns={v: k for k, v in field_map.items()})

    df["births"] = pd.to_numeric(df["births"], errors="coerce")
    df = df.dropna(subset=["births"])

except FileNotFoundError:
    st.error("Dataset file not found in repository.")
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

states = sorted(df["state_of_residence"].dropna().unique().tolist())
months = sorted(df["month"].dropna().unique().tolist())
genders = sorted(df["sex_of_infant"].dropna().unique().tolist())

sel_states = st.sidebar.multiselect("State of Residence", ["All"] + states, default=["All"])
sel_months = st.sidebar.multiselect("Month", ["All"] + months, default=["All"])
sel_genders = st.sidebar.multiselect("Gender", ["All"] + genders, default=["All"])

filtered = df.copy()
if "All" not in sel_states and sel_states:
    filtered = filtered[filtered["state_of_residence"].isin(sel_states)]
if "All" not in sel_months and sel_months:
    filtered = filtered[filtered["month"].isin(sel_months)]
if "All" not in sel_genders and sel_genders:
    filtered = filtered[filtered["sex_of_infant"].isin(sel_genders)]

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

agg = (
    filtered.groupby(["state_of_residence", "sex_of_infant"], as_index=False)["births"]
    .sum()
    .sort_values("state_of_residence")
)

fig = px.bar(
    agg,
    x="state_of_residence",
    y="births",
    color="sex_of_infant",
    title="Total Births by State and Gender",
    labels={"state_of_residence": "State", "births": "Total Births", "sex_of_infant": "Gender"},
    template="plotly_white",
)
fig.update_layout(legend_title_text="Gender", autosize=True)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

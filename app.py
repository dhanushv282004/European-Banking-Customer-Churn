import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from analysis import (
    load_data,
    add_segments,
    segment_summary,
    calculate_kpis,
    categorical_association,
)


st.set_page_config(
    page_title="European Banking Churn Analytics",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 Customer Segmentation & Churn Pattern Analytics in European Banking")
st.caption(
    "Interactive customer segmentation, churn analysis, geographic risk, engagement and high-value customer exploration."
)


@st.cache_data
def get_data():
    return add_segments(load_data())


df = get_data()


# -----------------------------
# Sidebar filters
# -----------------------------
with st.sidebar:
    st.header("Filters")

    geography = st.multiselect(
        "Geography",
        sorted(df["Geography"].unique()),
        default=sorted(df["Geography"].unique()),
    )

    gender = st.multiselect(
        "Gender",
        sorted(df["Gender"].unique()),
        default=sorted(df["Gender"].unique()),
    )

    age_segment = st.multiselect(
        "Age segment",
        list(df["Age_Segment"].cat.categories),
        default=list(df["Age_Segment"].cat.categories),
    )

    credit_band = st.multiselect(
        "Credit score band",
        list(df["Credit_Score_Band"].cat.categories),
        default=list(df["Credit_Score_Band"].cat.categories),
    )

    tenure_group = st.multiselect(
        "Tenure group",
        list(df["Tenure_Group"].cat.categories),
        default=list(df["Tenure_Group"].cat.categories),
    )

    balance_segment = st.multiselect(
        "Balance segment",
        sorted(df["Balance_Segment"].unique()),
        default=sorted(df["Balance_Segment"].unique()),
    )

    activity = st.multiselect(
        "Membership activity",
        ["Active member", "Inactive member"],
        default=["Active member", "Inactive member"],
    )

    activity_values = [1 if x == "Active member" else 0 for x in activity]


# -----------------------------
# Apply filters
# -----------------------------
filtered = df[
    df["Geography"].isin(geography)
    & df["Gender"].isin(gender)
    & df["Age_Segment"].isin(age_segment)
    & df["Credit_Score_Band"].isin(credit_band)
    & df["Tenure_Group"].isin(tenure_group)
    & df["Balance_Segment"].isin(balance_segment)
    & df["IsActiveMember"].isin(activity_values)
].copy()


if len(filtered) == 0:
    st.warning("No customers match the selected filters. Please broaden your selection.")
    st.stop()


# -----------------------------
# KPI row
# -----------------------------
kpi = calculate_kpis(filtered)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Customers", f"{len(filtered):,}")
c2.metric("Overall churn rate", f"{kpi['overall_churn_rate_pct']:.2f}%")
c3.metric("High-value churn ratio", f"{kpi['high_value_churn_ratio_pct']:.2f}%")
c4.metric("Engagement drop", f"{kpi['engagement_drop_indicator_pp']:.2f} pp")


# -----------------------------
# Core modules
# -----------------------------
st.subheader("1. Overall Churn Summary")

col1, col2 = st.columns(2)

with col1:
    exit_counts = (
        filtered["Exited"]
        .map({0: "Retained", 1: "Churned"})
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Customers")
    )
    fig = px.pie(
        exit_counts,
        names="Status",
        values="Customers",
        title="Retained vs Churned Customers",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    high_value = filtered[filtered["High_Value"]]
    high_value_churn = high_value["Exited"].mean() * 100 if len(high_value) else np.nan
    st.metric(
        "High-value churn ratio",
        "N/A" if np.isnan(high_value_churn) else f"{high_value_churn:.2f}%",
    )
    st.write(
        "High-value customers are defined here as customers whose positive balance "
        "is at or above the median positive balance in the selected data."
    )


st.subheader("2. Geography-wise Churn")

geo = segment_summary(filtered, "Geography")
overall_filtered = filtered["Exited"].mean()
geo["Geographic_Risk_Index"] = geo["Churn_Rate"] / overall_filtered * 100

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        geo,
        x="Geography",
        y="Churn_Rate_Pct",
        text="Churn_Rate_Pct",
        title="Churn Rate by Geography",
        labels={"Churn_Rate_Pct": "Churn rate (%)"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.dataframe(
        geo[
            [
                "Geography",
                "Customers",
                "Churners",
                "Churn_Rate_Pct",
                "Churn_Contribution_Pct",
                "Geographic_Risk_Index",
            ]
        ].round(3),
        use_container_width=True,
    )


st.subheader("3. Age & Tenure Churn Comparison")

col1, col2 = st.columns(2)

with col1:
    age = segment_summary(filtered, "Age_Segment")
    fig = px.bar(
        age,
        x="Age_Segment",
        y="Churn_Rate_Pct",
        text="Churn_Rate_Pct",
        title="Churn Rate by Age Segment",
        labels={"Churn_Rate_Pct": "Churn rate (%)"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    tenure = segment_summary(filtered, "Tenure_Group")
    fig = px.bar(
        tenure,
        x="Tenure_Group",
        y="Churn_Rate_Pct",
        text="Churn_Rate_Pct",
        title="Churn Rate by Tenure Group",
        labels={"Churn_Rate_Pct": "Churn rate (%)"},
    )
    st.plotly_chart(fig, use_container_width=True)


st.subheader("4. High-Value Customer Churn Explorer")

high = filtered[filtered["High_Value"]].copy()

if len(high):
    col1, col2, col3 = st.columns(3)

    col1.metric("High-value customers", f"{len(high):,}")
    col2.metric("High-value churners", f"{int(high['Exited'].sum()):,}")
    col3.metric("Churned balance exposure", f"{high.loc[high['Exited'] == 1, 'Balance'].sum():,.2f}")

    fig = px.scatter(
        high,
        x="Balance",
        y="EstimatedSalary",
        color="Exited",
        hover_data=["Geography", "Age", "NumOfProducts", "IsActiveMember"],
        title="High-Value Customers: Balance vs Estimated Salary",
        labels={"Exited": "Exited (1=Yes)"},
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No high-value customers are present under the current filters.")


st.subheader("5. Demographic & Financial Drill-Down")

dimension = st.selectbox(
    "Choose segmentation dimension",
    [
        "Gender",
        "Credit_Score_Band",
        "Balance_Segment",
        "NumOfProducts",
        "Geography",
    ],
)

detail = segment_summary(filtered, dimension)
st.dataframe(detail.round(3), use_container_width=True)

fig = px.bar(
    detail,
    x=dimension,
    y="Churn_Rate_Pct",
    title=f"Churn Rate by {dimension}",
    labels={"Churn_Rate_Pct": "Churn rate (%)"},
)
st.plotly_chart(fig, use_container_width=True)


st.subheader("6. Engagement & Statistical Diagnostics")

active = filtered.loc[filtered["IsActiveMember"] == 1, "Exited"].mean() * 100
inactive = filtered.loc[filtered["IsActiveMember"] == 0, "Exited"].mean() * 100

col1, col2, col3 = st.columns(3)
col1.metric("Active-member churn", f"{active:.2f}%" if not np.isnan(active) else "N/A")
col2.metric("Inactive-member churn", f"{inactive:.2f}%" if not np.isnan(inactive) else "N/A")
col3.metric(
    "Engagement drop indicator",
    f"{(inactive - active):.2f} pp" if not (np.isnan(active) or np.isnan(inactive)) else "N/A",
)

assoc = categorical_association(filtered, "Geography")

st.write(
    f"Geography vs churn: χ² = {assoc['chi_square']:.3f}, "
    f"p = {assoc['p_value']:.5g}, "
    f"Cramér's V = {assoc['cramers_v']:.3f}."
)

st.info(
    "Interpretation note: statistical association does not prove causation. "
    "Use effect size, customer counts, operational context and business validation together."
)


st.download_button(
    "Download filtered customer data",
    filtered.to_csv(index=False).encode("utf-8"),
    "filtered_european_banking_churn.csv",
    "text/csv",
)

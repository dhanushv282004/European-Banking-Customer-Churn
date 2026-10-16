import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from analysis import (
    load_data, add_segments, data_quality_report, segment_summary,
    calculate_kpis, categorical_association, numeric_churn_correlations,
    multivariable_churn_model,
)

st.set_page_config(page_title="European Banking Churn Analytics", page_icon="🏦", layout="wide")
st.title("🏦 European Banking Customer Segmentation & Churn")
st.caption("Explore churn patterns across demographics, geography, balance, products and engagement. Observational analysis; associations are not proof of cause.")

@st.cache_data
def get_data():
    raw = load_data("data/European_Bank.csv")
    return add_segments(raw)

try:
    df = get_data()
except Exception as exc:
    st.error(f"Could not load/validate data: {exc}")
    st.stop()

with st.expander("Data-quality checks"):
    quality = data_quality_report(df)
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.caption("Checks flag potential issues; rows are not automatically deleted. Review data-quality flags before interpreting results.")

threshold = df.attrs.get("positive_balance_median_full_data", np.nan)
st.caption(
    f"Balance-based high-value proxy: positive balance at/above full-dataset median "
    f"({threshold:,.2f} if available). This is not customer profitability or lifetime value."
    if pd.notna(threshold) else "Balance-based high-value proxy unavailable because no positive balances were found."
)

with st.sidebar:
    st.header("Filters")
    geography = st.multiselect("Geography", sorted(df["Geography"].dropna().unique()), default=sorted(df["Geography"].dropna().unique()))
    gender = st.multiselect("Gender", sorted(df["Gender"].dropna().unique()), default=sorted(df["Gender"].dropna().unique()))
    age_options = list(df["Age_Segment"].cat.categories)
    age_segment = st.multiselect("Age segment", age_options, default=age_options)
    credit_options = list(df["Credit_Score_Band"].cat.categories)
    credit_band = st.multiselect("Credit score band", credit_options, default=credit_options)
    tenure_options = list(df["Tenure_Group"].cat.categories)
    tenure_group = st.multiselect("Tenure group", tenure_options, default=tenure_options)
    balance_options = sorted(df["Balance_Segment"].dropna().unique())
    balance_segment = st.multiselect("Balance segment", balance_options, default=balance_options)
    activity = st.multiselect("Membership activity", ["Active member", "Inactive member"], default=["Active member", "Inactive member"])
    activity_values = [1 if x == "Active member" else 0 for x in activity]

filtered = df[
    df["Geography"].isin(geography) & df["Gender"].isin(gender) &
    df["Age_Segment"].isin(age_segment) & df["Credit_Score_Band"].isin(credit_band) &
    df["Tenure_Group"].isin(tenure_group) & df["Balance_Segment"].isin(balance_segment) &
    df["IsActiveMember"].isin(activity_values)
].copy()

if filtered.empty:
    st.warning("No customers match the selected filters. Broaden your selections.")
    st.stop()

kpi = calculate_kpis(filtered)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers in filtered view", f"{len(filtered):,}")
c2.metric("Churn rate", f"{kpi['overall_churn_rate_pct']:.2f}%")
c3.metric("Balance-proxy segment churn", f"{kpi['high_value_churn_ratio_pct']:.2f}%" if pd.notna(kpi["high_value_churn_ratio_pct"]) else "N/A")
c4.metric("Inactive vs active churn gap", f"{kpi['engagement_drop_indicator_pp']:.2f} pp" if pd.notna(kpi["engagement_drop_indicator_pp"]) else "N/A")

st.subheader("1. Overall churn")
counts = filtered["Exited"].map({0: "Retained", 1: "Churned"}).value_counts().rename_axis("Status").reset_index(name="Customers")
st.plotly_chart(px.pie(counts, names="Status", values="Customers", title="Retained vs churned"), use_container_width=True)

st.subheader("2. Geography churn")
geo = segment_summary(filtered, "Geography")
overall = filtered["Exited"].mean()
geo["Geographic_Risk_Index"] = 100*geo["Churn_Rate"]/overall if overall > 0 else np.nan
geo["Geographic_Risk_Index"] = geo["Geographic_Risk_Index"].round(1)
st.plotly_chart(px.bar(geo, x="Geography", y="Churn_Rate_Pct", error_y=geo["CI_95_Upper_Pct"]-geo["Churn_Rate_Pct"],
                       error_y_minus=geo["Churn_Rate_Pct"]-geo["CI_95_Lower_Pct"],
                       hover_data=["Customers", "Churners", "Churn_Contribution_Pct", "Geographic_Risk_Index"],
                       title="Churn rate by geography (Wilson 95% CI)"), use_container_width=True)
st.dataframe(geo.round(3), use_container_width=True, hide_index=True)
st.caption("Churn rate = churners / customers in that segment. Churn contribution = segment churners / all churners in this filtered view. Geographic risk index = segment churn rate relative to the filtered overall rate (100 = equal).")

st.subheader("3. Age and tenure")
col1, col2 = st.columns(2)
age = segment_summary(filtered, "Age_Segment")
tenure = segment_summary(filtered, "Tenure_Group")
with col1:
    st.plotly_chart(px.bar(age, x="Age_Segment", y="Churn_Rate_Pct", error_y=age["CI_95_Upper_Pct"]-age["Churn_Rate_Pct"],
                           error_y_minus=age["Churn_Rate_Pct"]-age["CI_95_Lower_Pct"],
                           hover_data=["Customers", "Churners"], title="Churn by age (95% CI)"), use_container_width=True)
with col2:
    st.plotly_chart(px.bar(tenure, x="Tenure_Group", y="Churn_Rate_Pct", error_y=tenure["CI_95_Upper_Pct"]-tenure["Churn_Rate_Pct"],
                           error_y_minus=tenure["Churn_Rate_Pct"]-tenure["CI_95_Lower_Pct"],
                           hover_data=["Customers", "Churners"], title="Churn by tenure (95% CI)"), use_container_width=True)
st.dataframe(pd.concat([age.assign(Segment_Type="Age"), tenure.assign(Segment_Type="Tenure")], ignore_index=True).round(3), use_container_width=True, hide_index=True)

st.subheader("4. Balance-based customer segment")
high = filtered[filtered["High_Value_Balance_Based"]]
if len(high):
    a, b, c = st.columns(3)
    a.metric("Customers in balance-proxy group", f"{len(high):,}")
    b.metric("Churners in group", f"{int(high['Exited'].sum()):,}")
    c.metric("Churned balance exposure", f"{high.loc[high['Exited'].eq(1), 'Balance'].sum():,.2f}")
    st.plotly_chart(px.scatter(high.sample(min(3000, len(high)), random_state=42), x="Balance", y="EstimatedSalary",
                               color="Exited", hover_data=["Geography", "Age", "NumOfProducts", "IsActiveMember"],
                               title="Balance-proxy customers: balance vs estimated salary (sampled up to 3,000)"), use_container_width=True)
else:
    st.info("No customers in the balance-based proxy segment for these filters.")

st.subheader("5. Demographic and product drill-down")
dimension = st.selectbox("Segmentation dimension", ["Gender", "Credit_Score_Band", "Balance_Segment", "NumOfProducts", "Geography"])
detail = segment_summary(filtered, dimension)
st.dataframe(detail.round(3), use_container_width=True, hide_index=True)
st.plotly_chart(px.bar(detail, x=dimension, y="Churn_Rate_Pct",
                       error_y=detail["CI_95_Upper_Pct"]-detail["Churn_Rate_Pct"],
                       error_y_minus=detail["Churn_Rate_Pct"]-detail["CI_95_Lower_Pct"],
                       hover_data=["Customers", "Churners"], title=f"Churn by {dimension} (Wilson 95% CI)"), use_container_width=True)

st.subheader("6. Engagement and bivariate diagnostics")
active = filtered.loc[filtered["IsActiveMember"].eq(1), "Exited"].mean()*100
inactive = filtered.loc[filtered["IsActiveMember"].eq(0), "Exited"].mean()*100
x, y, z = st.columns(3)
x.metric("Active-member churn", f"{active:.2f}%" if pd.notna(active) else "N/A")
y.metric("Inactive-member churn", f"{inactive:.2f}%" if pd.notna(inactive) else "N/A")
z.metric("Inactive-active gap", f"{inactive-active:.2f} pp" if pd.notna(active) and pd.notna(inactive) else "N/A")
assoc = categorical_association(filtered, "Geography")
if pd.notna(assoc["p_value"]):
    st.write(f"Geography vs churn: χ²={assoc['chi_square']:.3f}, p={assoc['p_value']:.5g}, Cramér's V={assoc['cramers_v']:.3f}.")
else:
    st.write(assoc["note"])
st.dataframe(numeric_churn_correlations(filtered).round(4), use_container_width=True, hide_index=True)
st.caption("With large samples, small effects may produce low p-values. Interpret effect sizes, confidence intervals and practical context; these are associations, not causal effects.")

st.subheader("7. Exploratory multivariable churn model")
st.caption("Logistic regression uses customer demographics, balance, products, credit-card/activity indicators, geography and gender. A stratified holdout evaluates predictive performance. It is not a causal model.")
if st.button("Run / refresh holdout model"):
    with st.spinner("Training and evaluating logistic regression..."):
        result = multivariable_churn_model(filtered)
    st.session_state["bank_churn_model_result"] = result
result = st.session_state.get("bank_churn_model_result")
if result:
    if "error" in result:
        st.warning(result["error"])
    else:
        st.dataframe(pd.DataFrame([result["metrics"]]).round(3), use_container_width=True, hide_index=True)
        st.write("Confusion matrix (holdout set)")
        st.dataframe(result["confusion_matrix"], use_container_width=True)
        st.caption(result["model_note"] + " Check recall and precision alongside accuracy, especially because churn is the minority class.")

st.subheader("8. Export")
st.download_button("Download filtered customer records", filtered.to_csv(index=False).encode("utf-8"),
                   "filtered_european_banking_churn.csv", "text/csv")
st.download_button("Download segment summaries", pd.concat([
    geo.assign(Segment="Geography"), age.assign(Segment="Age"), tenure.assign(Segment="Tenure"), detail.assign(Segment=dimension)
], ignore_index=True).to_csv(index=False).encode("utf-8"), "banking_churn_segment_summaries.csv", "text/csv")

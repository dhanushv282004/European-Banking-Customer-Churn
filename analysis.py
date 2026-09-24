"""Core analytics for the European Banking Customer Segmentation & Churn project."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


REQUIRED_COLUMNS = [
    "Year", "CustomerId", "Surname", "CreditScore", "Geography", "Gender",
    "Age", "Tenure", "Balance", "NumOfProducts", "HasCrCard",
    "IsActiveMember", "EstimatedSalary", "Exited"
]


def load_data(path: str = "data/European_Bank.csv") -> pd.DataFrame:
    """Load and validate the banking churn dataset."""
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def add_segments(df: pd.DataFrame) -> pd.DataFrame:
    """Create reproducible demographic, tenure, credit and balance segments.

    Note: the project brief specifies labels but does not specify all numeric
    boundaries, so these rules are documented here for reproducibility:
    - Age: <30, 30–45, 46–60, 60+
    - Credit score: <600, 600–699, 700+
    - Tenure: 0–3, 4–6, 7–10 years
    - Balance: zero, below the median positive balance, at/above median positive balance
    """
    out = df.copy()

    out["Age_Segment"] = pd.cut(
        out["Age"],
        bins=[-np.inf, 29, 45, 60, np.inf],
        labels=["<30", "30–45", "46–60", "60+"],
        include_lowest=True,
    )

    out["Credit_Score_Band"] = pd.cut(
        out["CreditScore"],
        bins=[-np.inf, 599, 699, np.inf],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    )

    out["Tenure_Group"] = pd.cut(
        out["Tenure"],
        bins=[-np.inf, 3, 6, np.inf],
        labels=["New", "Mid-term", "Long-term"],
        include_lowest=True,
    )

    positive_median = out.loc[out["Balance"] > 0, "Balance"].median()

    out["Balance_Segment"] = np.select(
        [
            out["Balance"].eq(0),
            (out["Balance"] > 0) & (out["Balance"] < positive_median),
        ],
        ["Zero-balance", "Low-balance"],
        default="High-balance",
    )

    out["High_Value"] = out["Balance_Segment"].eq("High-balance")

    return out


def segment_summary(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return customer count, churner count, churn rate and churn contribution."""
    out = (
        df.groupby(column, observed=False)
        .agg(
            Customers=("Exited", "size"),
            Churners=("Exited", "sum"),
            Churn_Rate=("Exited", "mean"),
        )
        .reset_index()
    )

    total_churners = df["Exited"].sum()
    out["Churn_Rate_Pct"] = out["Churn_Rate"] * 100
    out["Churn_Contribution_Pct"] = np.where(
        total_churners > 0,
        out["Churners"] / total_churners * 100,
        np.nan,
    )
    return out


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate the project KPIs."""
    overall = df["Exited"].mean()
    high_value = df.loc[df["High_Value"]]

    geo = segment_summary(df, "Geography").copy()
    geo["Geographic_Risk_Index"] = geo["Churn_Rate"] / overall * 100

    active = df.loc[df["IsActiveMember"] == 1, "Exited"].mean()
    inactive = df.loc[df["IsActiveMember"] == 0, "Exited"].mean()

    return {
        "overall_churn_rate_pct": overall * 100,
        "high_value_churn_ratio_pct": high_value["Exited"].mean() * 100,
        "engagement_drop_indicator_pp": (inactive - active) * 100,
        "active_churn_rate_pct": active * 100,
        "inactive_churn_rate_pct": inactive * 100,
        "geographic_risk_index": geo.set_index("Geography")["Geographic_Risk_Index"].to_dict(),
        "total_customers": len(df),
        "total_churners": int(df["Exited"].sum()),
    }


def categorical_association(df: pd.DataFrame, column: str) -> dict:
    """Chi-square and Cramér's V for a categorical variable vs Exited."""
    table = pd.crosstab(df[column], df["Exited"])
    chi2, p, dof, expected = stats.chi2_contingency(table)
    n = table.values.sum()
    v = np.sqrt((chi2 / n) / min(table.shape[0] - 1, table.shape[1] - 1))
    return {
        "chi_square": float(chi2),
        "p_value": float(p),
        "degrees_of_freedom": int(dof),
        "cramers_v": float(v),
        "table": table,
    }


def numeric_churn_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlations between numeric variables and Exited."""
    cols = [
        "CreditScore", "Age", "Tenure", "Balance", "NumOfProducts",
        "HasCrCard", "IsActiveMember", "EstimatedSalary"
    ]
    out = (
        df[cols + ["Exited"]]
        .corr(numeric_only=True)["Exited"]
        .drop("Exited")
        .sort_values(ascending=False)
        .reset_index()
    )
    out.columns = ["Variable", "Pearson_Correlation_with_Exited"]
    return out

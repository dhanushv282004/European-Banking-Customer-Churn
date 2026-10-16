"""Analytics helpers for European Banking Customer Segmentation & Churn."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

REQUIRED_COLUMNS = [
    "Year", "CustomerId", "Surname", "CreditScore", "Geography", "Gender",
    "Age", "Tenure", "Balance", "NumOfProducts", "HasCrCard",
    "IsActiveMember", "EstimatedSalary", "Exited",
]
NUMERIC_COLUMNS = [
    "Year", "CreditScore", "Age", "Tenure", "Balance", "NumOfProducts",
    "HasCrCard", "IsActiveMember", "EstimatedSalary", "Exited",
]


def load_data(path: str = "data/European_Bank.csv") -> pd.DataFrame:
    """Read data and validate required fields/types without silently dropping rows."""
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize common quality issues; does not automatically remove records."""
    checks = []
    checks.append(("Rows in loaded data", len(df)))
    checks.append(("Duplicate customer IDs", int(df["CustomerId"].duplicated().sum())))
    checks.append(("Rows with any missing required value",
                   int(df[REQUIRED_COLUMNS].isna().any(axis=1).sum())))
    for col in NUMERIC_COLUMNS:
        checks.append((f"Missing/non-numeric: {col}", int(df[col].isna().sum())))
    checks.extend([
        ("Age outside plausible 18–100 range", int((~df["Age"].between(18, 100)).fillna(True).sum())),
        ("Tenure outside 0–10 range", int((~df["Tenure"].between(0, 10)).fillna(True).sum())),
        ("Negative balance", int((df["Balance"] < 0).fillna(False).sum())),
        ("Exited not 0/1", int((~df["Exited"].isin([0, 1])).fillna(True).sum())),
        ("Invalid activity flag (not 0/1)", int((~df["IsActiveMember"].isin([0, 1])).fillna(True).sum())),
    ])
    return pd.DataFrame(checks, columns=["Check", "Count"])


def add_segments(df: pd.DataFrame) -> pd.DataFrame:
    """Add documented segments; high-balance threshold is based on full loaded data."""
    out = df.copy()
    out["Age_Segment"] = pd.cut(
        out["Age"], [-np.inf, 29, 45, 60, np.inf],
        labels=["<30", "30–45", "46–60", "60+"], include_lowest=True
    )
    out["Credit_Score_Band"] = pd.cut(
        out["CreditScore"], [-np.inf, 599, 699, np.inf],
        labels=["Low", "Medium", "High"], include_lowest=True
    )
    out["Tenure_Group"] = pd.cut(
        out["Tenure"], [-np.inf, 3, 6, np.inf],
        labels=["New (0–3)", "Mid-term (4–6)", "Long-term (7–10)"], include_lowest=True
    )
    positive = out.loc[out["Balance"] > 0, "Balance"]
    threshold = float(positive.median()) if len(positive) else np.nan
    out["Balance_Segment"] = np.select(
        [out["Balance"].eq(0), (out["Balance"] > 0) & (out["Balance"] < threshold)],
        ["Zero-balance", "Below median positive balance"],
        default="At/above median positive balance",
    )
    out["High_Value_Balance_Based"] = out["Balance_Segment"].eq("At/above median positive balance")
    out.attrs["positive_balance_median_full_data"] = threshold
    return out


def wilson_interval(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score confidence interval for a binomial proportion, returned as 0–100%."""
    if n <= 0:
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - alpha / 2)
    p = successes / n
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    half = z * np.sqrt((p*(1-p)/n) + z*z/(4*n*n)) / denom
    return (100*(center-half), 100*(center+half))


def segment_summary(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Segment churn rates with denominators, churn contribution and Wilson 95% CI."""
    work = df.dropna(subset=[column, "Exited"])
    out = work.groupby(column, observed=False).agg(
        Customers=("Exited", "size"), Churners=("Exited", "sum"),
        Churn_Rate=("Exited", "mean")
    ).reset_index()
    total_churners = int(work["Exited"].sum())
    out["Churn_Rate_Pct"] = 100*out["Churn_Rate"]
    intervals = [wilson_interval(int(row.Churners), int(row.Customers)) for row in out.itertuples()]
    out["CI_95_Lower_Pct"] = [x[0] for x in intervals]
    out["CI_95_Upper_Pct"] = [x[1] for x in intervals]
    out["Churn_Contribution_Pct"] = np.where(
        total_churners > 0, 100*out["Churners"]/total_churners, np.nan
    )
    return out


def calculate_kpis(df: pd.DataFrame) -> dict:
    overall = df["Exited"].mean()
    high = df.loc[df["High_Value_Balance_Based"]]
    active = df.loc[df["IsActiveMember"].eq(1), "Exited"].mean()
    inactive = df.loc[df["IsActiveMember"].eq(0), "Exited"].mean()
    geo = segment_summary(df, "Geography")
    geo["Geographic_Risk_Index"] = np.where(
        overall > 0, 100*geo["Churn_Rate"]/overall, np.nan
    )
    return {
        "overall_churn_rate_pct": 100*overall,
        "high_value_churn_ratio_pct": 100*high["Exited"].mean() if len(high) else np.nan,
        "engagement_drop_indicator_pp": 100*(inactive-active) if pd.notna(active) and pd.notna(inactive) else np.nan,
        "active_churn_rate_pct": 100*active if pd.notna(active) else np.nan,
        "inactive_churn_rate_pct": 100*inactive if pd.notna(inactive) else np.nan,
        "geographic_risk_index": geo.set_index("Geography")["Geographic_Risk_Index"].to_dict(),
        "total_customers": len(df), "total_churners": int(df["Exited"].sum()),
    }


def categorical_association(df: pd.DataFrame, column: str) -> dict:
    """Chi-square and Cramér's V; return safe N/A values for degenerate tables."""
    table = pd.crosstab(df[column], df["Exited"]).reindex(columns=[0, 1], fill_value=0)
    if table.shape[0] < 2 or table.shape[1] < 2 or table.values.sum() == 0:
        return {"chi_square": np.nan, "p_value": np.nan, "degrees_of_freedom": 0,
                "cramers_v": np.nan, "table": table, "note": "Not enough category/outcome variation."}
    chi2, p, dof, expected = stats.chi2_contingency(table)
    n = table.values.sum()
    denom = min(table.shape[0]-1, table.shape[1]-1)
    v = np.sqrt(chi2/n/denom) if denom > 0 else np.nan
    return {"chi_square": float(chi2), "p_value": float(p), "degrees_of_freedom": int(dof),
            "cramers_v": float(v), "table": table, "note": ""}


def numeric_churn_correlations(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["CreditScore", "Age", "Tenure", "Balance", "NumOfProducts",
            "HasCrCard", "IsActiveMember", "EstimatedSalary"]
    rows = []
    for col in cols:
        pair = df[[col, "Exited"]].dropna()
        r = pair[col].corr(pair["Exited"]) if len(pair) > 1 and pair[col].nunique() > 1 else np.nan
        rows.append({"Variable": col, "N": len(pair), "Pearson_Correlation_with_Exited": r})
    return pd.DataFrame(rows).sort_values("Pearson_Correlation_with_Exited", ascending=False)


def multivariable_churn_model(df: pd.DataFrame, test_size: float = 0.25, random_state: int = 42) -> dict:
    """Exploratory logistic model with holdout evaluation; coefficients are associations."""
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                 f1_score, roc_auc_score, confusion_matrix)

    numeric = ["CreditScore", "Age", "Tenure", "Balance", "NumOfProducts",
               "HasCrCard", "IsActiveMember", "EstimatedSalary"]
    categorical = ["Geography", "Gender"]
    use = df[numeric + categorical + ["Exited"]].dropna(subset=["Exited"]).copy()
    use = use[use["Exited"].isin([0, 1])]
    if len(use) < 30 or use["Exited"].nunique() < 2 or use["Exited"].value_counts().min() < 2:
        return {"error": "Not enough valid rows or both churn outcomes to train/evaluate a holdout model."}
    X, y = use[numeric + categorical], use["Exited"].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    prep = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")),
                          ("scale", StandardScaler())]), numeric),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    model = Pipeline([("prep", prep), ("logit", LogisticRegression(max_iter=1000, class_weight="balanced"))])
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)[:, 1]
    metrics = {
        "Test rows": len(y_test),
        "Accuracy": accuracy_score(y_test, pred),
        "Precision": precision_score(y_test, pred, zero_division=0),
        "Recall (churn)": recall_score(y_test, pred, zero_division=0),
        "F1": f1_score(y_test, pred, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, prob) if y_test.nunique() == 2 else np.nan,
    }
    cm = pd.DataFrame(confusion_matrix(y_test, pred, labels=[0, 1]),
                      index=["Actual retained", "Actual churned"],
                      columns=["Predicted retained", "Predicted churned"])
    return {"metrics": metrics, "confusion_matrix": cm,
            "model_note": "Logistic regression; stratified holdout; class-balanced. Exploratory prediction, not causal explanation."}

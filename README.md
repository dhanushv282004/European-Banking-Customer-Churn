# Customer Segmentation & Churn Pattern Analytics in European Banking

## Project objective

This project analyzes customer churn in a European retail-banking dataset using segmentation-driven analytics. The goal is to measure churn, identify high-risk customer groups, compare regions and demographics, examine engagement and tenure patterns, and explore churn among high-value customers.

> **Important research note:** association does not prove causation. The project reports descriptive patterns and statistical associations and should not be used as causal evidence without additional validation.

## Dataset

`data/European_Bank.csv` contains 10,000 customer observations and 14 columns:

- Year
- CustomerId
- Surname
- CreditScore
- Geography
- Gender
- Age
- Tenure
- Balance
- NumOfProducts
- HasCrCard
- IsActiveMember
- EstimatedSalary
- Exited

## Segmentation rules

The project brief gives the segment labels but does not specify every numeric boundary. For reproducibility, this implementation uses:

- Age: `<30`, `30–45`, `46–60`, `60+`
- Credit score: `<600` Low, `600–699` Medium, `700+` High
- Tenure: `0–3` New, `4–6` Mid-term, `7–10` Long-term
- Balance: Zero-balance, Low-balance (positive and below median positive balance), High-balance (at/above median positive balance)

The median positive balance is calculated from the dataset at runtime.

## Analytical methodology

1. Data ingestion and validation
2. Data cleaning and derived segmentation fields
3. Overall churn-rate analysis
4. Geography-wise churn comparison
5. Age and tenure churn analysis
6. Credit-score and balance segmentation
7. High-value customer churn analysis
8. Gender and geography-age comparison
9. Engagement analysis using active vs inactive members
10. Chi-square and Cramér's V association tests
11. Interactive Streamlit drill-down dashboard

## KPI definitions

- **Overall Churn Rate:** percentage of customers with `Exited = 1`.
- **Segment Churn Rate:** churn percentage within a selected customer segment.
- **High-Value Churn Ratio:** churn percentage among the High-balance segment.
- **Geographic Risk Index:** `(regional churn rate / overall churn rate) × 100`, where 100 represents the overall churn rate.
- **Engagement Drop Indicator:** inactive-member churn rate minus active-member churn rate, measured in percentage points.

## Key observed results from the provided dataset

- 10,000 customers
- Overall churn rate: 20.37%
- Germany churn rate: 32.44%
- France churn rate: 16.16%
- Spain churn rate: 16.67%
- High-value churn ratio: 24.19%
- Inactive-member churn rate: 26.85%
- Active-member churn rate: 14.27%
- Engagement drop indicator: 12.58 percentage points
- Age 46–60 churn rate: 51.12%
- Geography vs churn: Cramér's V ≈ 0.174
- Age segment vs churn: Cramér's V ≈ 0.351

These are descriptive/statistical results from this dataset and should not be generalized without validation.

## Google Colab

Open the notebook:

`notebooks/European_Banking_Churn_Analysis.ipynb`

The notebook uses direct CSV upload through Google Colab.

## Run Streamlit locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Suggested GitHub structure

```text
European_Banking_Customer_Churn_Project/
├── app.py
├── analysis.py
├── requirements.txt
├── README.md
├── research_report.md
├── .gitignore
├── data/
│   └── European_Bank.csv
├── notebooks/
│   └── European_Banking_Churn_Analysis.ipynb
└── results/
    ├── kpi_summary.csv
    ├── geography_churn.csv
    ├── age_churn.csv
    ├── tenure_churn.csv
    ├── balance_churn.csv
    ├── gender_churn.csv
    ├── product_churn.csv
    └── association_tests.csv
```

## Submission links

Add the final GitHub, research paper, Streamlit and feedback-video links after deployment.

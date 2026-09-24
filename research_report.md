# Research Report
## Customer Segmentation & Churn Pattern Analytics in European Banking

### Abstract

Customer churn can reduce customer lifetime value, increase acquisition costs and create revenue instability for retail banks. This study uses a 10,000-customer European banking dataset to examine churn patterns across geography, demographics, credit profile, tenure, balance, product usage and engagement.

The analysis measured an overall churn rate of **20.37%**. Churn varied across customer segments, with Germany showing a churn rate of **32.44%**, customers aged 46–60 showing **51.12%**, and inactive members showing **26.85%** compared with **14.27%** among active members. The high-value churn ratio was **24.19%** under the project’s High-balance definition. Statistical association tests showed non-negligible relationships for age segment (Cramér's V ≈ **0.351**), geography (≈ **0.174**) and activity status (≈ **0.156**), while credit-score bands and tenure groups showed much smaller associations. These findings are descriptive and do not establish causality.

### 1. Background and Context

Customer churn represents an important business challenge in retail banking. When customers leave, banks can lose future revenue, customer lifetime value and opportunities to cross-sell additional products. Churn analysis can become more useful when it identifies the customer segments in which churn is concentrated rather than reporting only an overall churn percentage.

This project applies segmentation-driven analytics to answer which customer groups show higher churn, how churn differs across European regions and demographic profiles, and whether churn is concentrated among high-value customers.

### 2. Problem Statement

Despite having customer-level data, banks may struggle to identify high-risk customer segments and quantify the financial profile of customers who exit. Without structured segmentation, retention strategies may remain broad and reactive.

The objective of this study is to quantify churn, identify segment-level patterns, compare European regions, examine engagement and tenure effects, and assess churn among high-value customers.

### 3. Dataset Description

The dataset `European_Bank.csv` contains **10,000 observations and 14 columns**:

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
- Year

The target variable is `Exited`, where 1 indicates churn and 0 indicates retention.

Data-quality checks found **0 missing values** and **0 duplicate rows** in the provided dataset.

### 4. Methodology

#### 4.1 Data ingestion and validation

The dataset was loaded into Python using Pandas. Dimensions, data types, missing values, duplicates and category distributions were inspected.

#### 4.2 Segmentation design

The project brief specifies segmentation labels but does not specify all numeric cutoffs. For reproducibility, this implementation uses:

- **Age:** <30, 30–45, 46–60, 60+
- **Credit score:** Low <600, Medium 600–699, High ≥700
- **Tenure:** New 0–3 years, Mid-term 4–6 years, Long-term 7–10 years
- **Balance:** Zero-balance; Low-balance for positive balances below the dataset's median positive balance; High-balance for positive balances at or above that median

The median positive balance in this dataset was **119,839.69 balance units**.

#### 4.3 Churn distribution analysis

Overall churn rate, segment churn rates, churn counts and churn contribution were calculated for geography, age, tenure, gender, credit-score bands, balance segments and number of products.

#### 4.4 High-value customer analysis

High-value customers were operationalized as customers in the High-balance segment. Their churn rate, churn count and churned balance exposure were quantified.

#### 4.5 Engagement analysis

Churn rates were compared between active and inactive members. The Engagement Drop Indicator was defined as inactive-member churn rate minus active-member churn rate in percentage points.

#### 4.6 Statistical association

Chi-square tests and Cramér's V were used to measure associations between categorical segmentation variables and `Exited`. These tests quantify association and do not establish causation.

### 5. Key Performance Indicators (KPIs)

**Overall Churn Rate** = `Exited=1 / Total Customers × 100`

**Segment Churn Rate** = `Churned Customers in Segment / Total Customers in Segment × 100`

**High-Value Churn Ratio** = `Churned High-Value Customers / Total High-Value Customers × 100`

**Geographic Risk Index** = `(Regional Churn Rate / Overall Churn Rate) × 100`

**Engagement Drop Indicator** = `Inactive-Member Churn Rate − Active-Member Churn Rate`, in percentage points.

### 6. Results

#### 6.1 Overall churn

The dataset contains **10,000 customers**, of whom **2,037 exited**, giving an overall churn rate of **20.37%**.

| Status | Customers | Share |
|---|---:|---:|
| Retained | 7,963 | 79.63% |
| Churned | 2,037 | 20.37% |
| Total | 10,000 | 100.00% |

#### 6.2 Geographic churn

| Geography | Customers | Churners | Churn Rate | Geographic Risk Index |
|---|---:|---:|---:|---:|
| France | 5,014 | 810 | 16.16% | 79.31 |
| Germany | 2,509 | 814 | 32.44% | 159.27 |
| Spain | 2,477 | 413 | 16.67% | 81.85 |

Germany had the highest observed churn rate in the dataset. Its Geographic Risk Index of **159.27** means its churn rate was about 1.59 times the overall dataset churn rate. France and Spain were below the overall rate.

The geography-vs-churn chi-square test produced **χ² = 301.255, p < 0.001**, with **Cramér's V = 0.174**.

#### 6.3 Age segmentation

| Age Segment | Customers | Churners | Churn Rate |
|---|---:|---:|---:|
| <30 | 1,641 | 124 | 7.56% |
| 30–45 | 6,248 | 956 | 15.30% |
| 46–60 | 1,647 | 842 | 51.12% |
| 60+ | 464 | 115 | 24.78% |

The 46–60 age segment had the highest observed churn rate at **51.12%** and contributed approximately **41.34% of all churners** in the dataset.

The association between age segment and churn was comparatively stronger than several other segmentation variables: **Cramér's V = 0.351, p < 0.001**.

#### 6.4 Tenure segmentation

| Tenure Group | Customers | Churners | Churn Rate |
|---|---:|---:|---:|
| New (0–3 years) | 3,505 | 741 | 21.14% |
| Mid-term (4–6 years) | 2,968 | 608 | 20.49% |
| Long-term (7–10 years) | 3,527 | 688 | 19.51% |

Tenure churn rates were relatively close across the three groups. The chi-square test produced **p = 0.231** and **Cramér's V = 0.017**, indicating a very small categorical association in this dataset.

#### 6.5 Credit-score segmentation

| Credit Score Band | Customers | Churners | Churn Rate |
|---|---:|---:|---:|
| Low | 3,034 | 660 | 21.75% |
| Medium | 3,818 | 753 | 19.72% |
| High | 3,148 | 624 | 19.82% |

Credit-score bands showed relatively small differences. The chi-square test yielded **p = 0.076** and **Cramér's V = 0.023**.

#### 6.6 Balance and high-value customers

| Balance Segment | Customers | Churners | Churn Rate |
|---|---:|---:|---:|
| Zero-balance | 3,617 | 500 | 13.82% |
| Low-balance | 3,191 | 765 | 23.97% |
| High-balance | 3,192 | 772 | 24.19% |

The project's high-value churn ratio was therefore **24.19%**.

High-value customers accounted for **772 of 2,037 churners (37.90%)**. The total balance held by churned customers was approximately **185.59 million balance units**, equal to about **24.26% of total balance**. Within the high-value segment, churned balance exposure was approximately **110.92 million balance units**.

The balance-segment association with churn had **Cramér's V = 0.122** with **p < 0.001**.

#### 6.7 Engagement pattern

| Membership Status | Customers | Churners | Churn Rate |
|---|---:|---:|---:|
| Active | 5,151 | 735 | 14.27% |
| Inactive | 4,849 | 1,302 | 26.85% |

The Engagement Drop Indicator was **12.58 percentage points**, calculated as 26.85% − 14.27%.

The association between activity status and churn had **χ² = 242.985, p < 0.001, Cramér's V = 0.156**.

#### 6.8 Number of products

| Products | Customers | Churners | Churn Rate |
|---|---:|---:|---:|
| 1 | 5,084 | 1,409 | 27.71% |
| 2 | 4,590 | 348 | 7.58% |
| 3 | 266 | 220 | 82.71% |
| 4 | 60 | 60 | 100.00% |

The number-of-products variable showed a relatively strong association with churn (**Cramér's V ≈ 0.388, p < 0.001**). However, the 3-product and 4-product groups are small, especially the 4-product group with only 60 customers, so their extreme churn rates should be interpreted cautiously.

#### 6.9 Gender and geography-age interaction

Female customers had a churn rate of **25.07%**, compared with **16.46%** for male customers. The gender-vs-churn association had **Cramér's V = 0.106, p < 0.001**.

A geography-age breakdown showed that the highest observed subgroup was **Germany, age 46–60**, where churn was approximately **67.33%** among 502 customers. This subgroup should be interpreted together with its sample size and should not be treated as a causal finding.

### 7. Discussion

The analysis shows that churn is not evenly distributed across the customer base. Several segmentation dimensions display materially different churn rates.

Age shows one of the clearest differences: the 46–60 group has a churn rate above 50%. Geography also differs substantially, with Germany at 32.44% versus approximately 16%–17% in France and Spain. Engagement status is another meaningful descriptive signal, with inactive members showing a 12.58-percentage-point higher churn rate than active members.

The analysis also indicates that high-value customers require attention because the High-balance segment has a churn rate of 24.19% and contributed approximately 37.90% of observed churners. This does not by itself establish the financial value of retention because the dataset does not contain realized customer lifetime value or profit data.

Tenure and credit-score bands display comparatively small differences under the chosen segmentation rules. The very high churn rates among customers with three or four products are notable, but the smaller group sizes require caution before operationalizing this result.

The results are observational. Segment differences can reflect other factors not modeled here, including interactions among age, geography, activity, product usage and financial characteristics. Therefore, these findings should support hypothesis generation and targeted investigation rather than be interpreted as causal proof.

### 8. Recommendations

1. Use segmentation dashboards to monitor churn concentration by geography, age, engagement and financial profile.
2. Investigate the 46–60 age group and high-churn geographies with additional customer-level context before designing retention programs.
3. Track inactive-member status as an early engagement signal because the observed churn gap between inactive and active members is substantial.
4. Monitor high-balance customers separately because their churn rate is above the overall rate and they represent a large share of churners.
5. Treat small segments, especially 3- and 4-product groups, as exploratory signals until validated on larger samples.
6. Validate retention interventions with controlled or longitudinal analysis before attributing churn reduction to a specific action.

### 9. Limitations

- The data are observational and do not establish causality.
- The project brief does not specify all numeric cutoffs for credit score and balance segmentation; this implementation documents reproducible thresholds.
- Currency and revenue units are not explicitly identified in the provided dataset, so balance exposure is reported as dataset balance units rather than euros.
- Some customer segments are relatively small, which can make extreme churn rates unstable.
- The analysis does not include a predictive model or causal design.
- A complete customer lifetime value analysis would require revenue, costs, product profitability and retention-value data.

### 10. Conclusion

This study provides a segmentation-based view of customer churn in European banking. The overall churn rate was **20.37%**, but important differences were visible across customer groups.

The highest observed churn concentration appeared in the **46–60 age segment (51.12%)**, **Germany (32.44%)**, and **inactive members (26.85%)**. High-value customers, defined using the High-balance segment, had a churn ratio of **24.19%** and represented **37.90% of observed churners**. By contrast, tenure and credit-score bands showed relatively small associations with churn.

Overall, the results support a move from broad churn reporting toward **segmentation-driven monitoring**, with particular attention to geography, age, engagement and high-value customers. The findings are specific to the provided dataset and should be validated with additional operational and longitudinal data before being used to guide customer-retention decisions.

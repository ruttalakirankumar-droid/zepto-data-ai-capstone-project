# Module 2 — Analytics Pipeline

## Project Overview

This module implements a complete analytics and predictive-modeling workflow using the Titanic dataset. The workflow covers exploratory data analysis, data cleaning, visualization, preprocessing, classification, imbalance handling, hyperparameter tuning, regression analysis, model comparison, and deployment-ready pipeline saving.

The complete workflow is implemented in:

- `01_eda.ipynb` — Part-A: Profiling, cleaning, and data story
- `02_modeling.ipynb` — Part-B: Predictive modeling
- `titanic.csv` — Cleaned offline fallback dataset
- `best_model_pipeline.joblib` — Saved end-to-end machine-learning pipeline

---

# Part A — Profiling, Cleaning, and Data Story

## 1. Dataset Loading and Profiling

The Titanic dataset was loaded and profiled using Pandas and Seaborn. Dataset information, descriptive statistics, shape, data types, and missing-value information were inspected before further analysis.

A cleaned copy of the dataset was saved as:

`titanic.csv`

This file is stored inside the `analytics` directory and acts as the offline fallback dataset for reproducible execution.

---

## 2. Missing-Value Analysis and Handling

Missing-value percentages were calculated for the affected columns.

The missing-value handling strategy followed the specified percentage-based rule:

- Columns with very low missingness were handled without unnecessary imputation.
- Columns with moderate missingness were imputed using appropriate statistical strategies.
- Columns where direct imputation was not considered reliable were handled explicitly according to their meaning.

The modeling pipeline independently performs train-only preprocessing so that information from the test set does not leak into model training.

---

## 3. Univariate Analysis — Age and Fare

Histograms and box plots were created for both `age` and `fare`.

The IQR rule was used to identify outliers:

\[
Lower\ Bound = Q1 - 1.5 \times IQR
\]

\[
Upper\ Bound = Q3 + 1.5 \times IQR
\]

Outlier counts were calculated separately for `age` and `fare`.

The `fare` distribution is strongly right-skewed because a relatively small number of passengers paid substantially higher fares than the majority of passengers. The mean is therefore affected by the high-value observations, while the median provides a more robust description of the typical fare.

---

## 4. Bivariate Survival Analysis

Survival rates were calculated using boolean filtering for:

1. Sex
2. Passenger class (`pclass`)
3. Sex combined with passenger class

The analysis shows clear differences in survival across demographic and passenger-class groups.

Female passengers had a substantially higher survival rate than male passengers. Passenger class was also strongly associated with survival, with higher-class passengers generally having higher survival rates.

Combining sex and passenger class provided a more detailed view of the survival pattern. The interaction between these variables shows that survival was not determined by a single demographic factor.

---

## 5. Correlation Analysis

A correlation matrix was calculated using exactly the following six numerical columns:

- `survived`
- `pclass`
- `age`
- `sibsp`
- `parch`
- `fare`

The derived boolean columns `adult_male` and `alone` were excluded because they are redundant/derived variables.

A 6×6 correlation heatmap was generated to visualize the relationships.

The strongest relationships were identified by ranking the absolute values of the off-diagonal correlation coefficients.

The analysis shows that passenger class and fare have a strong inverse relationship: passengers in higher-numbered classes generally paid lower fares. Passenger class also has a meaningful relationship with passenger age, reflecting differences in the age distribution across passenger classes.

Correlation is interpreted as association rather than proof of causation.

---

## 6. Multivariate Data Story

Multiple multivariate visualizations were created to examine relationships between passenger characteristics, fares, passenger class, and survival.

The charts demonstrate that:

- Survival differs considerably between male and female passengers.
- Passenger class is associated with both fare and survival.
- Fare distributions differ substantially across passenger classes.
- Combining demographic variables gives more information about survival than examining a single variable in isolation.

Each visualization was accompanied by a written interpretation explaining the observed pattern.

---

## 7. Standardization Exploratory Check

As an exploratory EDA check, `age` and `fare` were standardized using the z-score transformation:

\[
z = \frac{x-\mu}{\sigma}
\]

After standardization, both variables have approximately:

- Mean = 0
- Standard deviation = 1

This was used only as an exploratory check. The actual machine-learning preprocessing pipeline performs its own train-only scaling to prevent data leakage.

---

# Part B — Predictive Modeling

## 8. Train/Test Split

The cleaned dataset was divided into training and testing sets before preprocessing.

A stratified split was used with `survived` as the target variable.

Stratification preserves approximately the same proportion of survived and non-survived observations in both training and testing data, which is important because the target classes are imbalanced.

---

## 9. Preprocessing Pipeline

The modeling workflow uses a scikit-learn preprocessing pipeline.

Numerical features are processed using:

- Missing-value imputation
- Standard scaling

Categorical features are processed using:

- Most-frequent-value imputation
- One-hot encoding

A `ColumnTransformer` combines the numerical and categorical transformations.

All preprocessing steps are fitted only on the training data and then applied to the test data using transform-only behavior.

This prevents test-set information from leaking into model training.

---

# 10. Classification Models

Three classification models were trained using the same train/test split:

1. Logistic Regression
2. Decision Tree
3. Random Forest

The models were evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix
- ROC Curve

## Classification Results

| Model | Accuracy | Precision | Recall | F1 Score | AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.832402 | 0.809524 | 0.739130 | 0.772727 | 0.868643 |
| Decision Tree | 0.804469 | 0.750000 | 0.739130 | 0.744526 | 0.790580 |
| Random Forest | 0.826816 | 0.787879 | 0.753623 | 0.770370 | 0.836298 |

The Decision Tree produced lower overall classification performance than the other two classifiers.

Logistic Regression achieved the highest accuracy and AUC among the three tested classifiers.

Random Forest achieved a slightly higher recall than Logistic Regression, meaning it correctly identified a slightly larger proportion of surviving passengers.

---

# 11. Class Imbalance Analysis

The overall target-class distribution was:

| Survived | Count | Percentage |
|---|---:|---:|
| 0 — Not Survived | 549 | 61.62% |
| 1 — Survived | 342 | 38.38% |

Therefore, the dataset has a moderate class imbalance.

Three Logistic Regression variants were compared.

### Baseline — No Imbalance Handling

- Precision: `0.809524`
- Recall: `0.739130`
- F1 Score: `0.772727`

### Class Weight = Balanced

- Precision: `0.767123`
- Recall: `0.811594`
- F1 Score: `0.788732`

### SMOTE Oversampling

SMOTE was applied only to the training fold to avoid data leakage.

Before SMOTE:

- Class 0: 439
- Class 1: 273

After SMOTE:

- Class 0: 439
- Class 1: 439

SMOTE results:

- Precision: `0.763158`
- Recall: `0.840580`
- F1 Score: `0.800000`

### Imbalance Conclusion

The baseline model produced the highest precision, but its recall for the minority class was lower. Both class weighting and SMOTE increased recall. SMOTE produced the highest recall (`0.840580`) and highest F1 score (`0.800000`) among the three imbalance-handling approaches. This indicates that SMOTE provided the best balance between precision and recall for this particular experiment because it improved minority-class detection while maintaining a competitive precision.

---

# 12. Random Forest Hyperparameter Tuning

`GridSearchCV` was used to tune the Random Forest hyperparameters:

- `n_estimators`
- `max_depth`
- `max_features`

The best parameter combination was:

```text
n_estimators = 100
max_depth = 5
max_features = 'sqrt'
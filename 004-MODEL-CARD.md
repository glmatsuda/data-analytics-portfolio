# Model card: next-year building EUI

**Purpose:** demonstrate interpretable temporal prediction and governance using public benchmark records. Not a retrofit recommendation, energy audit or production scoring service.

**Target:** next reporting year's positive weather-normalized site EUI (kBtu/ft²). Cohort: continuing properties marked Compliant and not demolished in both adjacent years; prior-year positive floor area, plausible age 0–250, and usable property type. Eligibility excludes missing targets and creates survivorship/selection bias.

**Features:** prior-year EUI, self-reported area, age and EPA use type. Year-built changes are treated as as-reported facts. Building IDs join prior and next years but are not predictors. Repeated IDs across time reflect the intended existing-building task; performance does not estimate generalization to unseen buildings.

**Estimator:** ordinary least squares on log1p(target), training-only rare-category pooling at 50 observations, smearing retransformation from training residuals; predictions clipped at zero. Hyperparameters fixed for demonstration; no selection on 2024 outcomes.

**Evaluation:** 2023 temporal development check; final fit target years 2021–2023; 2024 held out. Both scores use identical populations per baseline comparison. MAE, RMSE and RMSLE are exported. Lower MAE in 2024 coexists with worse RMSLE and worse validation-year MAE. Do not cherry-pick metrics.

**Known limits:** public self-reported values may include errors, revisions and extreme observations. No anomaly removal or later-year retrospective cleaning is applied. Weather normalization is a source measure; no independent weather model is fitted. No confidence/prediction intervals, causal effects, fairness study, geographic generalization or future deployment performance are claimed. Review raw extremes, subgroup error and revised reporting coverage before practical use.

**Monitoring proposal:** on any refresh, check schema/key changes, exclusion rates by use/year, target and residual distributions, baseline comparison across multiple years, and largest-error records. A human should investigate discrepancies with source documentation.

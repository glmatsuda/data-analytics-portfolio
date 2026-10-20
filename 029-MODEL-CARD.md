# Model card: Fremont Bridge daily crossings

**Purpose:** demonstrate daily data-quality controls and calendar-based count prediction for one public counter. Not a city operational forecast or estimate of unique commuters.

**Population:** 2022–2024 hourly source records; daily counts exist only with exactly 24 unique valid hour labels and reconciled sidewalk totals. Other days remain in the calendar with NULL counts. Coverage exclusions can be systematic; the model does not recover missing days.

**Target and estimator:** combined daily crossing count; quasi-Poisson GLM with log link. Features: weekday, two annual harmonic pairs and elapsed years since 1 January 2022. Training 2022–2023; held-out 2024. Separate 2023 validation fits only 2022. Baseline weekday means use training only. No post-holdout feature selection.

**Evaluation:** MAE and RMSE on identical complete-day populations. 2024 MAE improves relative to baseline; 2023 validation MAE worsens. A linear trend extrapolates without bound and calendar effects can drift. No guarantee for another year, site or population.

**Semantics:** catalogue title describes combined bicycles/scooters while columns retain Cyclist labels. Floating timestamps do not encode UTC offsets; do not claim timezone-aware elapsed intervals or infer unique people or travel direction. Four days fail completeness in this window; see daily.csv and exceptions.csv for causes.

**Limits:** no weather, holidays, closures, equipment changes or policy effects; no causal inference, prediction intervals or station-to-station generalization. The exported quasi-Poisson dispersion is a descriptive fit diagnostic, not an interval estimate. Before practical use, compare rolling time splits, inspect residual autocorrelation and metadata changes, add verified weather/holiday inputs, and define a missing-day reporting policy with the data owner.

# Seattle energy forecasting in RStudio

An interpretable study of whether last year's reported building attributes help predict next year's weather-normalized site energy intensity. Demonstrates regression, temporal evaluation, baseline comparison and model documentation.

![Actual holdout diagnostics](results/model-diagnostics.png)

## Start here

Open **results/report.html** for the completed analysis. Open **SeattleEnergy.Rproj** in RStudio, then run `source("analysis.R")` in its Console. It creates the actual metrics, predictions, chart and saved model. Run `source("tests/test_analysis.R")` to verify the results. To also rebuild the HTML report, run from a terminal:

```sh
python3 run.py
```

Or run `Rscript --vanilla analysis.R`, `Rscript --vanilla tests/test_analysis.R`, then `python3 build_report.py`. No R package installation is needed. The project does not load or save a global workspace.

## Design and results

The frozen source includes 18,124 reports from 2020–2024. Adjacent-year records are joined by the stable property ID. Predictors are strictly prior-year EUI, self-reported floor area, age and property use. Target eligibility is used to define the observed evaluation cohort, never as a predictor. Train on target years 2021–2023, use 2023 as an earlier development check fitted only on 2021–2022, and evaluate a final untouched 2024 year.

A log-linear regression uses log1p EUI, log area, age and categorical use. Rare categories are pooled based on training frequency. Training residuals estimate a smearing correction for retransformation. The baseline simply carries forward prior-year EUI.

On 3,231 eligible 2024 transitions, model MAE is **16.75 kBtu/ft²** versus **19.65** for the baseline (14.8% lower). However, the model is worse on 2023 validation MAE and 2024 RMSLE. Report every metric; do not present a universally superior model. Large reported values remain and strongly affect squared error.

## Inspect and verify

- results/row-flow.csv: source, pairing and eligibility counts.
- results/split-audit.csv: target-year chronology and population sizes.
- results/metrics.csv, predictions.csv, coefficients.csv: measured outputs.
- results/energy-model.rds: fitted model, training categories and smearing factor.
- results/session-info.txt: actual local R environment.
- tests/test_analysis.R: verifies temporal separation, one-year lags, unique evaluation keys, matched baseline populations, finite predictions and independently recalculated MAE.
- MODEL-CARD.md: limitations and appropriate interpretation.

The report and PNG are regenerated from actual R results. This is a predictive modelling example; the companion energy data platform contains the physical SQL dimensional model.

## Disclosure and provenance

Independent portfolio demonstration using **real City of Seattle public data**. This is not paid client work, a city commission, or evidence of production results. Code is MIT licensed; the source catalogue marks the data Public Domain. See DATA-LICENSE.txt and data/source-manifest.json for attribution, field projection, study window, original export row count, hashes and retrieval date (20 October 2026). The snapshots are frozen for reproducibility; source revisions may change later results.

No accounts, tokens, paid services or network access are required to reproduce the included snapshot. Paths are relative to the repository root. Run commands from that root. Python 3.10+ and, for the statistical projects, R 4.2+ are required. `requirements.txt` documents that there are no third-party Python dependencies. All R packages used ship with R.

## Refresh safely

Download **All data → CSV** from the linked official dataset page. Keep the old snapshot. Apply the field projection and year window recorded in the manifest, preserve source values as strings, then update original/included hashes and row counts. For R projects also update data/source.md5. Review schema changes, exclusions, identifier grain and metric changes before committing. Rerun every check. Do not silently replace data in a published case study while keeping its old findings.

# Seattle building energy: governed analytics platform
> **GitHub edition:** generated SQLite databases are omitted from version control. Run this project’s documented build command first to create them locally. CSV/HTML/image example outputs and frozen inputs are included.


A reproducible SQL star model and offline interactive dashboard for Seattle’s building benchmarking records. Demonstrates data governance, dimensional modelling, quality controls and honest reporting of incomplete populations.

![Dashboard preview](results/dashboard-preview.png)

## Start here

Open **results/dashboard.html** in a browser. It runs offline; choose a reporting year, property use and neighborhood. The shipped build defaults to 2024. Open **model/erd.svg** for the data model, or explore **results/seattle-energy.sqlite** with a SQLite viewer. The PNG is a generated static preview of actual metrics, not an interactive dashboard screenshot.

To rebuild and verify:

```sh
python3 pipeline.py
python3 -m unittest discover -s tests -v
node tests/test_dashboard.js
```

Node.js is optional and only used for the dashboard logic check. The repository-level GitHub Actions workflow runs the Python and dashboard checks from this project directory. Remote results should be checked in the Actions tab.

## What the model does

- Grain: one reported property × reporting year; composite key (property_id, reporting_year).
- Five conformed dimensions: property, year, use type, neighborhood, source snapshot. Each fact has exactly one related row in each dimension.
- Historical use, neighborhood and building attributes are attached to the reporting-year fact. This preserves as-reported context without claiming a type-2 slowly changing dimension implementation.
- Unknown category strings map to a named Unknown member. Missing numeric observations remain SQL NULL. Identifiers stay text.
- Source file hash, exact headers, grain uniqueness, foreign keys, join row preservation and total energy reconcile before publication. Numeric parse problems are written to exceptions.csv. No numeric parse exceptions occurred in this snapshot.
- All 38,309 source records and 3,871 property identifiers are retained. Addresses, names and coordinates are omitted from this projected snapshot. The source contains 2015–2025 records, although catalogue prose states 2015–2024. The dashboard deliberately exposes only 2015–2024.

## What the dashboard says

2024 has 3,712 reported records, 3,575 marked Compliant, and 3,425 eligible for the EUI median. The eligibility rule is Compliant, not demolished, positive nonmissing weather-normalized site EUI. Compliance rate uses all selected records; median EUI uses the eligible subset. Filters recompute medians from individual records, never from other medians. Historical cohorts change, so year bars do not demonstrate like-for-like building improvement.

## Deliverables

`model/schema.sql`, `model/erd.svg`, `model/data-dictionary.md`, `model/metric-contract.md`, `model/example_queries.sql`; runnable pipeline; frozen source and provenance manifest; relational SQLite database; importable dimension/fact CSVs; quality report and exceptions; dashboard; tests.

## Power BI and Tableau handoff

The fact and dimension CSVs can be imported into either tool. The included model and metric contract explain relationships and measures. This repository provides a working HTML dashboard and BI handoff assets; it does not contain a native .pbix or .twbx workbook. See model/bi-handoff.md.

## Disclosure and provenance

Independent portfolio demonstration using **real City of Seattle public data**. This is not paid client work, a city commission, or evidence of production results. Code is MIT licensed; the source catalogue marks the data Public Domain. See DATA-LICENSE.txt and data/source-manifest.json for attribution, field projection, study window, original export row count, hashes and retrieval date (20 October 2026). The snapshots are frozen for reproducibility; source revisions may change later results.

No accounts, tokens, paid services or network access are required to reproduce the included snapshot. Paths are relative to the repository root. Run commands from that root. Python 3.10+ and, for the statistical projects, R 4.2+ are required. `requirements.txt` documents that there are no third-party Python dependencies. All R packages used ship with R.

## Refresh safely

Download **All data → CSV** from the linked official dataset page. Keep the old snapshot. Apply the field projection and year window recorded in the manifest, preserve source values as strings, then update original/included hashes and row counts. For R projects also update data/source.md5. Review schema changes, exclusions, identifier grain and metric changes before committing. Rerun every check. Do not silently replace data in a published case study while keeping its old findings.

## Optional static preview rebuild

The PNG is a designed static preview, distinct from a browser screenshot. To regenerate it, install the optional tools/requirements-preview.txt (Pillow), then run `python3 tools/make_preview.py`. Pillow is not needed for the pipeline or dashboard. Browser visual testing could not be completed locally because the environment blocked serving/opening local HTML. The included Node check covers filter and aggregation logic, not browser layout.

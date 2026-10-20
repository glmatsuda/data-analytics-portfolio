# Seattle Building Energy — Relational Data Modeling
> **GitHub edition:** generated SQLite databases are omitted from version control. Run this project’s documented build command first to create them locally. CSV/HTML/image example outputs and frozen inputs are included.


Independent portfolio study using real City of Seattle public records. Not client work; not affiliated with the City. No synthetic records are added.

## Start here
Open `START-HERE.html` for the illustrated model and actual SQL outputs. The ready-to-query database is `results/seattle-energy.sqlite`. Open it with a SQLite browser or any tool that supports SQLite. Model diagram: `model/relational-model.svg`.

```sh
python3 build.py
python3 -m unittest discover -s tests -v
```
Python 3.10+; standard library only; offline rebuild; no packages or credentials. Rebuild overwrites the generated results database. Run from this repository directory. Tested with Python 3.10 locally; no remote CI run.

## Business questions
- How many buildings reported in each year, and which were marked compliant?
- How complete is each energy measure, with missing distinct from zero?
- Which buildings have changed reported property classifications between adjacent years?
- Can every modeled measure be traced to its public source record and field?

## Public source
[Seattle Building Energy Benchmarking Data, 2015–Present](https://data.seattle.gov/Built-Environment/Building-Energy-Benchmarking-Data-2015-Present/teqw-tu6e), catalogue ID `teqw-tu6e`. Frozen download retrieved October 20, 2026: 38,309 reports, 3,871 building identifiers, reporting years 2015–2025. The portal description previously mentioned an end year of 2024; the downloaded data contains 2025, which this model preserves. Example neighborhood analysis uses 2024 without asserting that it is the latest finalized year.

`data/source.csv` is an exact column projection of the original download, retaining all rows. The manifest records original-export and projected-file hashes and the retained fields. It was reused from the earlier Seattle dashboard project; this is a different model of the same snapshot, not another independent source. The source is not refreshed automatically and can be revised by Seattle. `source_record` is the 1-based CSV data-record ordinal (header excluded), not necessarily a physical text line.

## Three modeling layers
**Conceptual:** a building submits annual reports. A report has a neighborhood classification, a property-use classification, a source snapshot, and energy measurements. A measurement has a defined metric and unit.

**Logical:** seven related tables separate stable identity, annual observations, lookup classifications, metric definitions, and provenance. `model/relational-model.svg` shows primary and foreign keys and cardinalities. `model/data-dictionary.md` defines every column and table grain.

**Physical:** `model/schema.sql` implements SQLite primary keys, unique business keys, foreign keys, indexes, state checks, and a wide reporting view. Applications must enable `PRAGMA foreign_keys=ON` on every connection. In-memory transactional loading publishes a database only after validation.

## Why annual attributes stay on the report
Property use, neighborhood labels, floor count, construction year, and building type are source-reported observations. Even apparently stable characteristics can be corrected. Keeping these on the annual report preserves history instead of overwriting every year with a current label. This is annual observation history, not a claim to know the exact date of a real-world change. `building` stores only the source identifier; it is not a verified physical-building master or parcel model.

## Why separate measurements
Eight energy/area metrics each have a unit, a source field, a raw value, a parsed numeric value, and an explicit state. This enables completeness checks and source traceability without mixing kWh, therms, square feet, and intensities. This typed long layout suits a metric catalog; it is not a universal schema recommendation. Queries need a metric filter or pivot. `report_wide` aggregates measurements to report grain before joining, preventing report counts from multiplying by eight. The earlier dashboard project's star model is easier for direct BI aggregation; this model emphasizes relational structure, units, and provenance.

## Limits and governance
- One frozen source snapshot, one report per building/year. Source revisions are not modeled as report versions. Supporting multiple snapshots would require adding snapshot to the report business key or a deliberate version entity, with deduplication rules.
- Eight expected measurements per report are enforced by the build and verified by tests; ordinary row-level SQL constraints do not ensure that all eight exist. The saved database can be edited; rerun validation after changes.
- Source category spellings (including any empty labels) are preserved, not geographically standardized. Lookup keys are internal to this snapshot and may change after a refresh.
- Blank/NA/N/A/null become missing; unparseable/nonfinite numbers become invalid with raw values retained. No imputation, outlier removal, or inferred compliance is applied. Current snapshot has zero parse exceptions. Missing natural gas does not establish whether a building uses gas.
- `reported_year_built` and `reported_floors` retain numeric source values without asserting real-world validity or integer-only semantics. Negative or extreme source measurements are retained, not certified as accurate.
- Missing values are never zeros. Totals over records with values are partial reported totals, not estimates of all Seattle buildings. Intensities are nonadditive. Control sums across years in validation are reconciliation checks, not business KPIs.
- No personal owner or steward assignments, approval events, or invented governance records. Source metadata and quality checks provide the governance layer.

## Repository map
`build.py`: loader and reconciliation. `data/`: frozen projected public source and manifest. `model/`: executable schema, dictionary, diagram, SQL queries and metric rules. `results/`: SQLite database, actual query outputs, validation and exception records. `tests/`: meaningful integrity, mapping and aggregation tests. `PORTFOLIO-COPY.txt`: truthful reusable case description.

Code: MIT (`LICENSE`). Public data: source's Public Domain designation (`DATA-LICENSE.txt`); no additional restrictions asserted by this project. Authored with AI assistance and locally executed/validated.

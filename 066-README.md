# Retail SQL analytics
> **GitHub edition:** generated SQLite databases are omitted from version control. Run this project’s documented build command first to create them locally. CSV/HTML/image example outputs and frozen inputs are included.

**Synthetic portfolio demonstration. No client engagement or real customer data. AI-assisted code; review and understand it before presenting it as your work.**


![Synthetic demo reference preview](preview.png)

A fictional online retailer wants one consistent definition of revenue, a monthly trend, and category rankings by region. This repository demonstrates SQL joins, CTEs, window functions, relational integrity and reconciliation.

## Run
Python 3.10+ with SQLite 3.25+ (window functions). No third-party packages.
```sh
python generate_data.py
python run.py
python -m unittest discover -s tests -v
```
Run from this repository folder. `run.py --output your-folder` writes only generated results. Rerunning uses the existing CSV inputs; `generate_data.py` resets the synthetic fixture with seed 42.

## Outputs
`example-output/`: monthly revenue and contribution, regional category ranking, repeat purchaser rate, integer-cent control totals, and a local SQLite database. `preview.png` is a static visualization of actual demo results.

## Model and definitions
`orders.csv`: one order for one product, 1,800 rows, January–June 2026. `products.csv`: six products with synthetic prices and unit costs. Primary/foreign keys prevent duplicate orders and orphan products. Currency is USD; storage uses integer cents.

Net revenue = quantity × price − discount for completed orders. Returned and cancelled orders contribute zero revenue and zero cost. Contribution = completed revenue − completed product cost; it excludes shipping, labor, tax and overhead and is not accounting profit. Returns are fully reversed in their original order month; there is no separate refund ledger. Average order value uses completed orders only. Repeat purchaser rate is customers with 2+ completed orders divided by customers with 1+ completed orders in this window, not a retention metric. First-month growth is blank because there is no prior month.

## Files and lineage
`generate_data.py` → `data/*.csv` → `sql/schema.sql` and `order_metrics` → three SQL queries → `example-output/*.csv`. All identifiers and businesses are fictional. Seeds intentionally create variation, not a market forecast. SQLite SQL uses `substr` and boolean sums; adapt those expressions for another database.

## Review evidence
Tests independently reconstruct revenue from CSV, reconcile all monthly order counts, check first-month growth, exclude cancelled/returned revenue, and reject duplicate keys/orphan products. Queries are designed for clarity, not a demonstrated production-scale speedup.

## Portfolio caption
Built an AI-assisted SQL analytics demonstration using 1,800 synthetic retail orders. Defined revenue rules, wrote monthly and regional analyses, and verified totals against the raw fixture. Independent demonstration; no client results or business impact claimed.

# Physical data dictionary

Types and constraints below are implemented in schema.sql. Keys reference the as-reported snapshot, not invented business entities.

## dim_neighborhood

| Column | SQL type | Key / required |
|---|---|---|
| neighborhood_key | INTEGER | PK component 1 |
| neighborhood | TEXT |  required |

## dim_property

| Column | SQL type | Key / required |
|---|---|---|
| property_id | TEXT | PK component 1 |

## dim_source

| Column | SQL type | Key / required |
|---|---|---|
| source_key | INTEGER | PK component 1 |
| source_id | TEXT |  required |
| source_url | TEXT |  required |
| snapshot_date | TEXT |  required |
| snapshot_sha256 | TEXT |  required |

## dim_use_type

| Column | SQL type | Key / required |
|---|---|---|
| use_key | INTEGER | PK component 1 |
| property_use | TEXT |  required |

## dim_year

| Column | SQL type | Key / required |
|---|---|---|
| reporting_year | INTEGER | PK component 1 |

## fact_building_energy

| Column | SQL type | Key / required |
|---|---|---|
| property_id | TEXT | PK component 1 required |
| reporting_year | INTEGER | PK component 2 required |
| use_key | INTEGER |  required |
| neighborhood_key | INTEGER |  required |
| source_key | INTEGER |  required |
| building_type | TEXT |  |
| year_built | INTEGER |  |
| floors | REAL |  |
| property_gfa_sqft | REAL |  |
| self_report_gfa_sqft | REAL |  |
| site_eui_wn_kbtu_sqft | REAL |  |
| site_eui_kbtu_sqft | REAL |  |
| site_energy_kbtu | REAL |  |
| electricity_kwh | REAL |  |
| natural_gas_therms | REAL |  |
| ghg_metric_tons | REAL |  |
| compliance_status | TEXT |  |
| demolished | INTEGER |  required |
| source_row | INTEGER |  required |

## Measurement semantics

`property_id` is source OSEBuildingID as text; reporting_year is DataYear. use_key and neighborhood_key reflect each reporting year. Numeric source mapping is defined explicitly in pipeline.NUMBERS. Area units are square feet; EUI is kBtu/ft²; site_energy is kBtu; electricity is kWh; natural gas is therms; GHG is source TotalGHGEmissions, metric tons CO₂-equivalent per source documentation. Self-reported area and property GFA are distinct measures. EUI must not be summed. source_row is the 1-based CSV line including its header; source_key links the frozen projected snapshot. The mart retains zeros, negatives and outliers for review; the dashboard eligibility rule excludes nonpositive EUI. The SQL eligible_eui view flag is 1 exactly when Compliant, demolished=0 and weather-normalized EUI>0. Unknown category text is a dimension member, never a missing key.

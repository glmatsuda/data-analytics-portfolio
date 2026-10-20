# Data dictionary

All relationships use enforced foreign keys when SQLite foreign-key checking is enabled. One-to-many cardinality means zero or more children unless the build contract states otherwise.

| Table / grain | Columns | Rules |
|---|---|---|
| source_snapshot / frozen projected file | snapshot_id PK; catalogue_id; source_url; retrieved_date; sha256 | SHA-256 unique, length 64; manifest hash verified by loader |
| building / source building identifier | building_id TEXT PK | OSEBuildingID, preserved as text, nonempty in loader |
| neighborhood / distinct source label | neighborhood_id PK; label UNIQUE | Exact source Neighborhood label; no canonical geography claim |
| property_use / distinct source label | property_use_id PK; label UNIQUE | Exact EPAPropertyType label |
| annual_report / building × reporting year | report_id PK; building_id FK; reporting_year; neighborhood_id FK; property_use_id FK; snapshot_id FK; source_record; building_type; reported_year_built; reported_floors; compliance_status; demolished | UNIQUE(building_id, reporting_year); UNIQUE(snapshot_id, source_record); year 1900–2200; demolished boolean; year built/floors nullable REAL, all other columns required |
| metric_definition / metric | metric_code TEXT PK; source_field UNIQUE; label; unit; aggregation_note | Eight seeded definitions from source numeric energy/area fields |
| measurement / report × metric | report_id FK; metric_code FK; value nullable REAL; value_status; raw_value | Composite PK(report_id, metric_code); reported requires a numeric value; missing/invalid requires NULL; raw CSV field text retained |

`report_wide` is a view at annual_report grain, with all report columns, neighborhood and property_use labels, and eight numeric columns: property_gfa_sqft, self_report_gfa_sqft, site_eui_wn_kbtu_sqft, site_eui_kbtu_sqft, site_energy_kbtu, electricity_kwh, natural_gas_therms, ghg_metric_tons. See measurement for raw values and statuses.

Source-to-report mapping: OSEBuildingID→building_id; DataYear→reporting_year; BuildingType→building_type; YearBuilt→reported_year_built; NumberofFloors→reported_floors; ComplianceStatus→compliance_status; Demolished→boolean demolished. Neighborhood and EPAPropertyType map through their lookup tables. Numeric area and energy fields map through metric_definition.source_field. No source field is silently substituted for another.

`source_record` is the CSV data-record ordinal, starting at one. `retrieved_date` is an ISO date from the verified manifest; it is download metadata, not a revision timestamp. A report row belongs to exactly one source_snapshot in this study.

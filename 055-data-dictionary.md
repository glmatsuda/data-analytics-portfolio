# Physical data dictionary

Types and constraints below are implemented in schema.sql. Keys reference the as-reported snapshot, not invented business entities.

## dim_date

| Column | SQL type | Key / required |
|---|---|---|
| date_key | TEXT | PK component 1 |
| year | INTEGER |  required |
| month | INTEGER |  required |
| iso_weekday | INTEGER |  required |

## dim_station

| Column | SQL type | Key / required |
|---|---|---|
| station_id | TEXT | PK component 1 |
| station_name | TEXT |  required |
| source_id | TEXT |  required |

## fact_daily_crossings

| Column | SQL type | Key / required |
|---|---|---|
| station_id | TEXT | PK component 1 required |
| date_key | TEXT | PK component 2 required |
| crossings | INTEGER |  |
| source_rows | INTEGER |  required |
| valid_rows | INTEGER |  required |
| unique_hours | INTEGER |  required |
| complete_day | INTEGER |  required |

## Measurement semantics

date_key is an ISO calendar date derived from floating local source labels, not UTC. iso_weekday runs Monday=1 to Sunday=7. Station FREMONT identifies one source counter. crossings is combined daily detections, NULL unless complete_day=1. source_rows and valid_rows count hourly inputs; unique_hours counts distinct hour labels. Complete days require 24 of each. No zero fill. daily.csv additionally includes sidewalk totals and duplicate hour counts. Source-to-date-to-fact lineage is implemented in prepare.py.

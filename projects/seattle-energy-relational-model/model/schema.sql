PRAGMA foreign_keys=ON;
CREATE TABLE source_snapshot (
 snapshot_id INTEGER PRIMARY KEY, catalogue_id TEXT NOT NULL,
 source_url TEXT NOT NULL, retrieved_date TEXT NOT NULL, sha256 TEXT NOT NULL UNIQUE CHECK(length(sha256)=64)
);
-- Building identity only: reported characteristics belong to an annual report.
CREATE TABLE building (building_id TEXT PRIMARY KEY NOT NULL);
CREATE TABLE neighborhood (neighborhood_id INTEGER PRIMARY KEY, label TEXT NOT NULL UNIQUE);
CREATE TABLE property_use (property_use_id INTEGER PRIMARY KEY, label TEXT NOT NULL UNIQUE);
CREATE TABLE annual_report (
 report_id INTEGER PRIMARY KEY, building_id TEXT NOT NULL REFERENCES building,
 reporting_year INTEGER NOT NULL CHECK(reporting_year BETWEEN 1900 AND 2200),
 neighborhood_id INTEGER NOT NULL REFERENCES neighborhood,
 property_use_id INTEGER NOT NULL REFERENCES property_use,
 snapshot_id INTEGER NOT NULL REFERENCES source_snapshot,
 source_record INTEGER NOT NULL CHECK(source_record>0),
 building_type TEXT NOT NULL, reported_year_built REAL, reported_floors REAL,
 compliance_status TEXT NOT NULL, demolished INTEGER NOT NULL CHECK(demolished IN (0,1)),
 UNIQUE(building_id,reporting_year), UNIQUE(snapshot_id,source_record)
);
CREATE TABLE metric_definition (
 metric_code TEXT PRIMARY KEY NOT NULL, source_field TEXT NOT NULL UNIQUE,
 label TEXT NOT NULL, unit TEXT NOT NULL, aggregation_note TEXT NOT NULL
);
CREATE TABLE measurement (
 report_id INTEGER NOT NULL REFERENCES annual_report,
 metric_code TEXT NOT NULL REFERENCES metric_definition,
 value REAL, value_status TEXT NOT NULL CHECK(value_status IN ('reported','missing','invalid')),
 raw_value TEXT NOT NULL,
 PRIMARY KEY(report_id,metric_code),
 CHECK((value_status='reported' AND value IS NOT NULL) OR
       (value_status IN ('missing','invalid') AND value IS NULL))
);
CREATE INDEX report_year ON annual_report(reporting_year);
CREATE INDEX measurement_metric ON measurement(metric_code);
-- Pivot before joining other tables: one row per annual report, never eight rows.
CREATE VIEW report_wide AS
WITH p AS (
 SELECT report_id,
 MAX(CASE WHEN metric_code='property_gfa' THEN value END) AS property_gfa_sqft,
 MAX(CASE WHEN metric_code='self_report_gfa' THEN value END) AS self_report_gfa_sqft,
 MAX(CASE WHEN metric_code='site_eui_wn' THEN value END) AS site_eui_wn_kbtu_sqft,
 MAX(CASE WHEN metric_code='site_eui' THEN value END) AS site_eui_kbtu_sqft,
 MAX(CASE WHEN metric_code='site_energy' THEN value END) AS site_energy_kbtu,
 MAX(CASE WHEN metric_code='electricity' THEN value END) AS electricity_kwh,
 MAX(CASE WHEN metric_code='natural_gas' THEN value END) AS natural_gas_therms,
 MAX(CASE WHEN metric_code='ghg' THEN value END) AS ghg_metric_tons
 FROM measurement GROUP BY report_id
)
SELECT a.*,n.label AS neighborhood,u.label AS property_use,p.property_gfa_sqft,
p.self_report_gfa_sqft,p.site_eui_wn_kbtu_sqft,p.site_eui_kbtu_sqft,p.site_energy_kbtu,
p.electricity_kwh,p.natural_gas_therms,p.ghg_metric_tons
FROM annual_report a JOIN neighborhood n USING(neighborhood_id)
JOIN property_use u USING(property_use_id) JOIN p USING(report_id);

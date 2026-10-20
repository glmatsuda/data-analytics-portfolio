PRAGMA foreign_keys=ON;
CREATE TABLE dim_property(property_id TEXT PRIMARY KEY);
CREATE TABLE dim_year(reporting_year INTEGER PRIMARY KEY CHECK(reporting_year BETWEEN 2000 AND 2100));
CREATE TABLE dim_use_type(use_key INTEGER PRIMARY KEY,property_use TEXT NOT NULL UNIQUE);
CREATE TABLE dim_neighborhood(neighborhood_key INTEGER PRIMARY KEY,neighborhood TEXT NOT NULL UNIQUE);
CREATE TABLE dim_source(source_key INTEGER PRIMARY KEY,source_id TEXT NOT NULL,source_url TEXT NOT NULL,snapshot_date TEXT NOT NULL,snapshot_sha256 TEXT NOT NULL);
CREATE TABLE fact_building_energy(
  property_id TEXT NOT NULL REFERENCES dim_property(property_id),
  reporting_year INTEGER NOT NULL REFERENCES dim_year(reporting_year),
  use_key INTEGER NOT NULL REFERENCES dim_use_type(use_key),
  neighborhood_key INTEGER NOT NULL REFERENCES dim_neighborhood(neighborhood_key),
  source_key INTEGER NOT NULL REFERENCES dim_source(source_key),
  building_type TEXT,year_built INTEGER,floors REAL,property_gfa_sqft REAL,self_report_gfa_sqft REAL,
  site_eui_wn_kbtu_sqft REAL,site_eui_kbtu_sqft REAL,site_energy_kbtu REAL,electricity_kwh REAL,natural_gas_therms REAL,ghg_metric_tons REAL,
  compliance_status TEXT,demolished INTEGER NOT NULL CHECK(demolished IN(0,1)),source_row INTEGER NOT NULL,
  PRIMARY KEY(property_id,reporting_year)
);
CREATE INDEX ix_fact_context ON fact_building_energy(reporting_year,use_key,neighborhood_key);
CREATE VIEW analytics_energy AS SELECT f.*,u.property_use,n.neighborhood,
  CASE WHEN compliance_status='Compliant' AND demolished=0 AND site_eui_wn_kbtu_sqft>0 THEN 1 ELSE 0 END AS eligible_eui
FROM fact_building_energy f JOIN dim_use_type u USING(use_key) JOIN dim_neighborhood n USING(neighborhood_key);

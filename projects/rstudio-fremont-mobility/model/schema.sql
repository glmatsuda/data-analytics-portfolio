PRAGMA foreign_keys=ON;
CREATE TABLE dim_station(station_id TEXT PRIMARY KEY,station_name TEXT NOT NULL,source_id TEXT NOT NULL);
CREATE TABLE dim_date(date_key TEXT PRIMARY KEY,year INTEGER NOT NULL,month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),iso_weekday INTEGER NOT NULL CHECK(iso_weekday BETWEEN 1 AND 7));
CREATE TABLE fact_daily_crossings(
  station_id TEXT NOT NULL REFERENCES dim_station(station_id),
  date_key TEXT NOT NULL REFERENCES dim_date(date_key),crossings INTEGER,
  source_rows INTEGER NOT NULL,valid_rows INTEGER NOT NULL,unique_hours INTEGER NOT NULL,
  complete_day INTEGER NOT NULL CHECK(complete_day IN(0,1)),
  PRIMARY KEY(station_id,date_key),
  CHECK((complete_day=1 AND crossings IS NOT NULL AND crossings>=0 AND source_rows=24 AND valid_rows=24 AND unique_hours=24) OR (complete_day=0 AND crossings IS NULL))
);

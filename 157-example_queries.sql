-- Coverage is reported explicitly; missing metrics never become zero.
SELECT reporting_year,COUNT(*) AS reported_properties,
  SUM(compliance_status='Compliant') AS compliant_properties,
  SUM(eligible_eui) AS eligible_eui_records,
  ROUND(1.0*SUM(compliance_status='Compliant')/COUNT(*),4) AS compliance_rate
FROM analytics_energy GROUP BY reporting_year ORDER BY reporting_year;

-- Each fact is joined to one row of each dimension: no fan-out.
SELECT property_use,COUNT(*) AS properties,SUM(eligible_eui) AS eligible_eui_records,
  AVG(CASE WHEN eligible_eui=1 THEN site_eui_wn_kbtu_sqft END) AS mean_eligible_eui
FROM analytics_energy WHERE reporting_year=2024 GROUP BY property_use ORDER BY properties DESC;

# Power BI / Tableau handoff

Import results/dim_*.csv and results/fact_building_energy.csv. Set property_id to text and reporting_year to whole number. The fact primary key is (property_id, reporting_year). Create five dimension-to-fact 1:* relationships using the matching keys. In Power BI use single-direction filters from each dimension into the fact; avoid bidirectional or many-to-many relationships. No date relationship is required beyond dim_year for annual reporting.

Suggested Power BI DAX (table names match the CSV file stems):

```dax
Reported Records = COUNTROWS(fact_building_energy)
Compliant Records = CALCULATE([Reported Records], KEEPFILTERS(fact_building_energy[compliance_status] = "Compliant"))
Compliance Rate = DIVIDE([Compliant Records], [Reported Records])
Eligible EUI Records = COUNTROWS(FILTER(fact_building_energy, fact_building_energy[compliance_status] = "Compliant" && fact_building_energy[demolished] = 0 && fact_building_energy[site_eui_wn_kbtu_sqft] > 0))
Median Eligible EUI = MEDIANX(FILTER(fact_building_energy, fact_building_energy[compliance_status] = "Compliant" && fact_building_energy[demolished] = 0 && fact_building_energy[site_eui_wn_kbtu_sqft] > 0), fact_building_energy[site_eui_wn_kbtu_sqft])
```

In Tableau relate fact to dimensions on keys, preserving fact grain. For median EUI use `MEDIAN(IF [compliance_status] = "Compliant" AND [demolished] = 0 AND [site_eui_wn_kbtu_sqft] > 0 THEN [site_eui_wn_kbtu_sqft] END)`. Compare the default 2024 counts to quality-report.json before styling. Check relationship cardinality and Tableau aggregation behavior on a filtered cohort.

These are handoff instructions and suggested formulas. They were not executed inside Power BI or Tableau. The delivered working dashboard is HTML; no native PBIX or TWBX is claimed.

# Dashboard metric contract

Filters apply to reporting_year, property_use and neighborhood. Default year 2024; 2025 is retained in the mart but not dashboard options. One property-year fact contributes once to every denominator.

| Metric | Formula | Missing policy |
|---|---|---|
| Reported records | COUNT fact rows in current filters | Includes incomplete measurements |
| Compliant records | COUNT where compliance_status = Compliant | Other labels remain in denominator |
| Compliance rate | Compliant / Reported × 100 | No records → blank, not zero |
| Eligible EUI count | COUNT where Compliant AND demolished=0 AND EUI>0 | NULL and nonpositive excluded |
| Median EUI | Median individual eligible site_eui_wn_kbtu_sqft | No eligible rows → blank |
| Missing EUI | COUNT where site_eui_wn_kbtu_sqft IS NULL | Zero is distinct from NULL |
| Excluded from median | Reported − Eligible | Exclusion rules overlap; do not add individual rule failures |

Medians are unweighted building medians, not floor-area weighted intensities. The annual chart retains use/neighborhood filters but varies year intentionally. Cohorts change each year. Property-use chart shows eight largest eligible groups by record count in the selected year; each bar is a group median, not a portfolio median. Do not interpret comparison bars as savings or efficiency rankings adjusted for building use.

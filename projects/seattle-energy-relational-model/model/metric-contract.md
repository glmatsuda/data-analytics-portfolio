# Metric rules

1. Annual report count: COUNT annual_report rows after selecting one reporting year. Do not count measurement rows as reports.
2. Compliance: source label exactly `Compliant`; denominator all reports in the selected cohort. Do not infer compliance from completeness.
3. Measurement completeness: reported measurements / expected reports, for one metric and cohort. Zero is a reported value. Invalid and missing are not reported values.
4. Reported energy totals: SUM site_energy values within one reporting year. Show nonmissing reporting count beside the sum. Do not treat missing as zero or extrapolate to unrepresented buildings.
5. EUI: weather-normalized SiteEUIWN and ordinary SiteEUI are distinct. Never sum intensities. A positive weather-normalized EUI cohort excludes null and <=0 values; report excluded count. This repository does not calculate a weighted intensity because source area definitions require careful alignment.
6. GHG: source TotalGHGEmissions in metric tons CO2e; retained as reported without computing emission factors.
7. Classification change: different labels across consecutive reporting years reflect a reported classification change or correction; they do not prove a physical conversion.
8. Cross-year source-control sums in validation.json are reconciliation controls only. This repository makes no source accuracy or full-city coverage claim.

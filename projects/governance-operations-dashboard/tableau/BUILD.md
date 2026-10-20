# Tableau build and acceptance checks
**Build kit, not a finished TWB/TWBX. Calculations and actions have not been executed in Tableau here.**

1. Connect to `data/requests.csv` as a text file in Tableau. Confirm created_date and closed_date are Dates, with blank closed dates null. Flag/day columns must be whole numbers, ticket_id a string dimension. Do not join another source: each row is one unique request.
2. Create the seven fields in `calculated-fields.txt` individually. Use COUNT(ticket_id) only because IDs are unique (verified by Python tests). Format Closed SLA Rate as percentage with one decimal, and counts as integers.
3. Create four KPI worksheets, each using one aggregate on Text: Requests Count, Closed SLA Rate, Open Requests, Overdue Open. Format large text with a small descriptive title. Preserve null when there are no closed requests.
4. Create Requests by created month: continuous Created Month on Columns, Requests Count on Rows, line marks. This is a creation cohort view. Create SLA by domain: domain on Rows, Closed SLA Rate on Columns, bar marks, fixed axis 0 to 1. Add Closed Requests and SUM(on_time_flag) to the tooltip.
5. Create a domain detail crosstab with Requests Count, Closed Requests, Closed SLA Rate and Overdue Open. Create a fixed 1280 × 800 dashboard. Put the title/subtitle above a horizontal KPI container, then the two charts, then the detail table. Use teal #137E8D for data and amber #EAA044 for overdue counts. Reference `preview.png` for spacing, not as an app screenshot.
6. Add domain and priority filters. Apply to all worksheets using this data source. Optional: add a Select filter action from the domain bar to all other worksheets; clear selection shows all values. Check that the target sheet list includes all four KPIs.
7. Compare unfiltered totals to `data/expected_metrics.json`, test Supplier + High filters against the CSV, clear and confirm baseline, then test the domain action. A no-closed selection should show null SLA, not a misleading 0%. Confirm month selections are labeled as creation cohorts.
8. Save a packaged workbook as `governance-operations.twbx`, reopen it and confirm the embedded data is available without the original folder. Capture screenshots from the workbook and replace the reference image before calling this a native Tableau sample.

Official reference: [Actions and dashboards](https://help.tableau.com/current/pro/desktop/en-us/actions_dashboards.htm). Native build and testing remain required. This kit supports learning Tableau; it does not establish professional Tableau experience.

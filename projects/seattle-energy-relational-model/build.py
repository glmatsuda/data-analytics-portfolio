"""Offline, deterministic public-data model. Python standard library only."""
from pathlib import Path
import collections,csv,hashlib,json,math,sqlite3,argparse
BASE=Path(__file__).resolve().parent
METRICS=[
 ('property_gfa','PropertyGFATotal','Property gross floor area','sqft','Do not sum across years.'),
 ('self_report_gfa','SelfReportGFATotal','Self-reported gross floor area','sqft','Separate from property area; do not substitute silently.'),
 ('site_eui_wn','SiteEUIWN(kBtu/sf)','Weather-normalized site EUI','kBtu/sqft','Nonadditive intensity; positive values for median cohort.'),
 ('site_eui','SiteEUI(kBtu/sf)','Site EUI','kBtu/sqft','Nonadditive intensity; distinct from weather-normalized EUI.'),
 ('site_energy','SiteEnergyUse(kBtu)','Site energy use','kBtu','Reported total; do not infer missing values as zero.'),
 ('electricity','Electricity(kWh)','Electricity','kWh','Sum only within the same metric and reporting year.'),
 ('natural_gas','NaturalGas(therms)','Natural gas','therms','Sum only within the same metric and reporting year.'),
 ('ghg','TotalGHGEmissions','Greenhouse gas emissions','metric tons CO2e','Reported emissions; no derived emission factors.')]
def parse_number(raw):
 s=raw.strip().replace(',','')
 if s in ('','NA','N/A','null'):return None,'missing'
 try:
  v=float(s)
  if not math.isfinite(v):raise ValueError()
  return v,'reported'
 except ValueError:return None,'invalid'
def build(output=None):
 out=Path(output or BASE/'results');out.mkdir(parents=True,exist_ok=True)
 source=BASE/'data/source.csv'; manifest=json.loads((BASE/'data/source-manifest.json').read_text())
 if hashlib.sha256(source.read_bytes()).hexdigest()!=manifest['included_csv_sha256']:raise ValueError('Source hash mismatch')
 with source.open(newline='',encoding='utf-8-sig') as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=manifest['fields']:raise ValueError('Source schema mismatch')
  rows=list(reader)
 if len(rows)!=manifest['included_rows']:raise ValueError('Source row count mismatch')
 db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
 db.executescript((BASE/'model/schema.sql').read_text())
 db.execute('INSERT INTO source_snapshot VALUES(1,?,?,?,?)',(manifest['source_id'],manifest['landing_page'],manifest['retrieved_date'],manifest['included_csv_sha256']))
 db.executemany('INSERT INTO building VALUES(?)',[(b,) for b in sorted({r['OSEBuildingID'] for r in rows})])
 # Preserve source category spellings, including any empty label. No implied geographic harmonization.
 ns={s:i+1 for i,s in enumerate(sorted({r['Neighborhood'] for r in rows}))}
 us={s:i+1 for i,s in enumerate(sorted({r['EPAPropertyType'] for r in rows}))}
 db.executemany('INSERT INTO neighborhood VALUES(?,?)',[(v,k) for k,v in ns.items()])
 db.executemany('INSERT INTO property_use VALUES(?,?)',[(v,k) for k,v in us.items()])
 db.executemany('INSERT INTO metric_definition VALUES(?,?,?,?,?)',METRICS)
 exceptions=[]
 for i,r in enumerate(rows,1):
  if not r['OSEBuildingID'].strip():raise ValueError('Missing building ID')
  if r['Demolished'].lower() not in ('true','false'):raise ValueError('Unknown demolished value')
  attrs=[]
  for field in ['YearBuilt','NumberofFloors']:
   val,status=parse_number(r[field]);attrs.append(val)
   if status=='invalid':exceptions.append({'source_record':i,'field':field,'raw':r[field]})
  db.execute('INSERT INTO annual_report VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(i,r['OSEBuildingID'],int(r['DataYear']),ns[r['Neighborhood']],us[r['EPAPropertyType']],1,i,r['BuildingType'],*attrs,r['ComplianceStatus'],int(r['Demolished'].lower()=='true')))
  for code,field,*_ in METRICS:
   val,status=parse_number(r[field])
   db.execute('INSERT INTO measurement VALUES(?,?,?,?,?)',(i,code,val,status,r[field]))
   if status=='invalid':exceptions.append({'source_record':i,'field':field,'raw':r[field]})
 if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Foreign key failure')
 if db.execute('SELECT COUNT(*) FROM report_wide').fetchone()[0]!=len(rows):raise ValueError('Join changed report grain')
 controls=[]
 for code,field,*_ in METRICS:
  raw=[parse_number(r[field])[0] for r in rows];values=[v for v in raw if v is not None]
  modeled=db.execute('SELECT COUNT(value),SUM(value) FROM measurement WHERE metric_code=?',(code,)).fetchone()
  if len(values)!=modeled[0] or not math.isclose(math.fsum(values),modeled[1] or 0,rel_tol=1e-11,abs_tol=.01):raise ValueError('Metric reconciliation failed: '+code)
  controls.append({'metric':code,'reported_values':len(values),'missing_or_invalid':len(rows)-len(values),'source_control_sum':math.fsum(values),'model_control_sum':modeled[1]})
 summary={'snapshot_date':manifest['retrieved_date'],'reports':len(rows),'buildings':db.execute('SELECT COUNT(*) FROM building').fetchone()[0],
 'years':[r[0] for r in db.execute('SELECT DISTINCT reporting_year FROM annual_report ORDER BY 1')],
 'measurements':db.execute('SELECT COUNT(*) FROM measurement').fetchone()[0],
 'measurement_statuses':dict(db.execute('SELECT value_status,COUNT(*) FROM measurement GROUP BY value_status')),
 'foreign_key_violations':0,'parse_exceptions':len(exceptions),'metric_reconciliation':controls}
 queries=json.loads((BASE/'model/queries.json').read_text());examples={}
 for name,sql in queries.items():examples[name]=[dict(r) for r in db.execute(sql)]
 db.commit()
 target=out/'seattle-energy.sqlite'
 if target.exists():target.unlink()
 with sqlite3.connect(target) as dest:db.backup(dest)
 (out/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
 (out/'example-results.json').write_text(json.dumps(examples,indent=2)+'\n')
 (out/'parse-exceptions.json').write_text(json.dumps(exceptions,indent=2)+'\n')
 db.close();return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path);args=p.parse_args()
 print(json.dumps(build(args.output),indent=2))

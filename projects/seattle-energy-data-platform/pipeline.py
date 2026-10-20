"""Build a governed SQLite mart and offline dashboard from the frozen public CSV."""
from pathlib import Path
import csv,json,sqlite3,hashlib,math,collections,statistics,shutil,argparse
BASE=Path(__file__).parent
NUMBERS={'YearBuilt':'year_built','NumberofFloors':'floors','PropertyGFATotal':'property_gfa_sqft','SelfReportGFATotal':'self_report_gfa_sqft',
  'SiteEUIWN(kBtu/sf)':'site_eui_wn_kbtu_sqft','SiteEUI(kBtu/sf)':'site_eui_kbtu_sqft','SiteEnergyUse(kBtu)':'site_energy_kbtu',
  'Electricity(kWh)':'electricity_kwh','NaturalGas(therms)':'natural_gas_therms','TotalGHGEmissions':'ghg_metric_tons'}
def number(value):
    value=value.strip().replace(',','')
    if value in ('','NA','N/A','null'):return None
    result=float(value)
    if not math.isfinite(result):raise ValueError('non-finite number')
    return result
def build(source,output):
    source=Path(source);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((BASE/'data/source-manifest.json').read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest()!=manifest['included_csv_sha256']:raise ValueError('Snapshot hash differs. Update provenance intentionally before rebuilding.')
    with source.open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=manifest['fields']:raise ValueError('Source schema changed')
        rows=list(reader)
    keys=[(r['OSEBuildingID'],r['DataYear']) for r in rows]
    if len(keys)!=len(set(keys)) or any(not a or not b for a,b in keys):raise ValueError('Missing/duplicate property-year key; resolve before publication')
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row;db.executescript((BASE/'model/schema.sql').read_text())
    props=sorted({r['OSEBuildingID'] for r in rows});years=sorted({int(r['DataYear']) for r in rows})
    uses={v:i+1 for i,v in enumerate(sorted({r['EPAPropertyType'].strip() or 'Unknown' for r in rows}))}
    neighborhoods={v:i+1 for i,v in enumerate(sorted({r['Neighborhood'].strip() or 'Unknown' for r in rows}))}
    db.executemany('INSERT INTO dim_property VALUES(?)',[(x,) for x in props]);db.executemany('INSERT INTO dim_year VALUES(?)',[(x,) for x in years])
    db.executemany('INSERT INTO dim_use_type VALUES(?,?)',[(v,k) for k,v in uses.items()]);db.executemany('INSERT INTO dim_neighborhood VALUES(?,?)',[(v,k) for k,v in neighborhoods.items()])
    db.execute('INSERT INTO dim_source VALUES(1,?,?,?,?)',(manifest['source_id'],manifest['landing_page'],manifest['retrieved_date'],manifest['included_csv_sha256']))
    issues=[]
    for line,r in enumerate(rows,2):
        values=[]
        for src,dest in NUMBERS.items():
            try:v=number(r[src])
            except ValueError:
                issues.append([line,r['OSEBuildingID'],r['DataYear'],src,'Invalid numeric value',r[src]]);v=None
            if src=='YearBuilt' and v is not None and v!=int(v):
                issues.append([line,r['OSEBuildingID'],r['DataYear'],src,'Noninteger construction year',r[src]]);v=None
            values.append(v)
        if r['Demolished'].lower() not in ('true','false'):raise ValueError(f'Unknown demolished flag on row {line}')
        record=[r['OSEBuildingID'],int(r['DataYear']),uses[r['EPAPropertyType'].strip() or 'Unknown'],neighborhoods[r['Neighborhood'].strip() or 'Unknown'],1,r['BuildingType'],*values,r['ComplianceStatus'],int(r['Demolished'].lower()=='true'),line]
        db.execute('INSERT INTO fact_building_energy VALUES('+','.join('?' for _ in record)+')',record)
    facts=[dict(r) for r in db.execute('SELECT * FROM analytics_energy ORDER BY reporting_year,property_id')]
    assert len(facts)==len(rows)
    assert not db.execute('PRAGMA foreign_key_check').fetchall()
    # Independent CSV-side energy control; compare matching missing-value populations.
    raw_energy=sum(number(r['SiteEnergyUse(kBtu)']) or 0 for r in rows)
    mart_energy=db.execute('SELECT SUM(site_energy_kbtu) FROM fact_building_energy').fetchone()[0]
    assert math.isclose(raw_energy,mart_energy,rel_tol=1e-12,abs_tol=.01)
    summary={'snapshot_date':manifest['retrieved_date'],'source_rows':len(rows),'fact_rows':len(facts),'properties':len(props),'years':years,'numeric_parse_exceptions':len(issues),'foreign_key_violations':0,'source_site_energy_kbtu':raw_energy,'mart_site_energy_kbtu':mart_energy,
      '2024':{'records':sum(r['reporting_year']==2024 for r in facts),'compliant':sum(r['reporting_year']==2024 and r['compliance_status']=='Compliant' for r in facts),'eligible_eui':sum(r['reporting_year']==2024 and r['eligible_eui']==1 for r in facts)}}
    for table in ['dim_property','dim_year','dim_use_type','dim_neighborhood','dim_source','fact_building_energy']:
        result=db.execute('SELECT * FROM '+table)
        with (output/(table+'.csv')).open('w',newline='') as f:
            writer=csv.writer(f);writer.writerow([c[0] for c in result.description]);writer.writerows(result)
    with (output/'exceptions.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['source_row','property_id','year','field','reason','value']);writer.writerows(issues)
    (output/'quality-report.json').write_text(json.dumps(summary,indent=2)+'\n')
    db.commit()
    with sqlite3.connect(output/'seattle-energy.sqlite') as target:db.backup(target)
    payload=[[r['reporting_year'],r['property_use'],r['neighborhood'],r['compliance_status'],r['site_eui_wn_kbtu_sqft'],r['eligible_eui']] for r in facts]
    template=(BASE/'dashboard-template.html').read_text()
    (output/'dashboard.html').write_text(template.replace('__DATA__',json.dumps(payload,separators=(',',':')).replace('</','<\/')))
    db.close();return summary
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=BASE/'results');args=parser.parse_args();print(json.dumps(build(BASE/'data/source.csv',args.output),indent=2))

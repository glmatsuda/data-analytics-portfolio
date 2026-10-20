"""Validate local floating timestamps and build a daily coverage-aware mart."""
from pathlib import Path
import csv,json,datetime,collections,math,sqlite3,hashlib
BASE=Path(__file__).parent
FIELDS=['date','crossings','west_sidewalk','east_sidewalk','source_rows','valid_rows','unique_hours','duplicate_hours','complete_day','year','month','weekday']
def prepare():
    source=BASE/'data/source.csv';manifest=json.loads((BASE/'data/source-manifest.json').read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest()!=manifest['included_csv_sha256']:raise ValueError('Snapshot hash changed; review and update provenance first')
    with source.open() as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=manifest['fields']:raise ValueError('Counter source schema changed')
        rows=list(reader)
    groups=collections.defaultdict(list);issues=[];fields=manifest['fields']
    for line,r in enumerate(rows,2):
        dt=datetime.datetime.strptime(r['Date'],'%m/%d/%Y %I:%M:%S %p');values=[];valid=True
        for key in fields[1:]:
            try:
                n=float(r[key].replace(',',''));assert math.isfinite(n) and n>=0 and n.is_integer();values.append(int(n))
            except (ValueError,AssertionError):valid=False;values.append(None)
        if valid and values[0]!=values[1]+values[2]:valid=False
        if not valid:issues.append([line,dt.isoformat(),'Missing/invalid counts or total differs from sidewalk sum'])
        groups[dt.date()].append((dt.hour,values,valid))
    output=BASE/'results';output.mkdir(exist_ok=True);daily=[]
    day=datetime.date(2022,1,1);end=datetime.date(2024,12,31)
    while day<=end:
        items=groups.get(day,[]);hours=[r[0] for r in items];valid=sum(r[2] for r in items)
        complete=len(items)==24 and valid==24 and len(set(hours))==24
        total=[sum(x[1][i] for x in items) if complete else '' for i in range(3)]
        daily.append([day.isoformat(),*total,len(items),valid,len(set(hours)),len(items)-len(set(hours)),int(complete),day.year,day.month,day.isoweekday()])
        day+=datetime.timedelta(days=1)
    with (output/'daily.csv').open('w',newline='') as f:w=csv.writer(f);w.writerow(FIELDS);w.writerows(daily)
    with (output/'exceptions.csv').open('w',newline='') as f:w=csv.writer(f);w.writerow(['source_row','timestamp','reason']);w.writerows(issues)
    summary={'source_rows':len(rows),'calendar_days':len(daily),'complete_days':sum(r[8] for r in daily),'excluded_incomplete_days':sum(not r[8] for r in daily),'invalid_hour_rows':len(issues),'study_window':'2022-01-01 through 2024-12-31','policy':'Only 24 unique hours with nonmissing nonnegative integer counts and matching totals. All other days remain present with null daily counts; never zero filled.'}
    (output/'quality-report.json').write_text(json.dumps(summary,indent=2)+'\n')
    db=sqlite3.connect(':memory:');db.executescript((BASE/'model/schema.sql').read_text());db.execute('INSERT INTO dim_station VALUES(?,?,?)',('FREMONT','Fremont Bridge','65db-xm6k'))
    for r in daily:
        db.execute('INSERT INTO dim_date VALUES(?,?,?,?)',(r[0],r[9],r[10],r[11]))
        db.execute('INSERT INTO fact_daily_crossings VALUES(?,?,?,?,?,?,?)',('FREMONT',r[0],None if r[1]=='' else r[1],r[4],r[5],r[6],r[8]))
    db.commit()
    with sqlite3.connect(output/'mobility.sqlite') as dest:db.backup(dest)
    db.close();return summary
if __name__=='__main__':print(json.dumps(prepare(),indent=2))

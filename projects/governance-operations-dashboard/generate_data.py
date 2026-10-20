"""Create synthetic governance requests at a fixed reporting cutoff."""
from pathlib import Path
import csv, random, datetime, json
AS_OF=datetime.date(2026,6,30)
FIELDS=['ticket_id','created_date','closed_date','domain','priority','owner_team','status','sla_days','age_or_cycle_days','closed_flag','on_time_flag','overdue_flag']
def flags(is_closed,days,sla):
    return [int(is_closed),int(is_closed and days<=sla),int(not is_closed and days>sla)]
def generate(destination):
    destination=Path(destination); destination.mkdir(parents=True,exist_ok=True); rng=random.Random(73); rows=[]
    for i in range(1,481):
        created=datetime.date(2026,1,1)+datetime.timedelta(days=rng.randrange(181))
        domain=rng.choice(['Customer','Finance','Product','Supplier'])
        priority=rng.choices(['High','Medium','Low'],[20,50,30])[0]; sla={'High':3,'Medium':7,'Low':14}[priority]
        duration=rng.randint(1,20)+(3 if domain=='Supplier' else 0)
        closed=created+datetime.timedelta(days=duration)
        is_closed=closed<=AS_OF and rng.random()>.16
        cycle=duration if is_closed else (AS_OF-created).days
        rows.append([f'GOV-{i:04}',created.isoformat(),closed.isoformat() if is_closed else '',domain,priority,
            {'Customer':'CRM stewardship','Finance':'Finance data','Product':'Product ops','Supplier':'Procurement data'}[domain],
            'Closed' if is_closed else 'Open',sla,cycle,*flags(is_closed,cycle,sla)])
    with (destination/'requests.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(FIELDS); w.writerows(rows)
    summary={'as_of':AS_OF.isoformat(),'requests':len(rows),'closed':sum(r[9] for r in rows),'on_time_closed':sum(r[10] for r in rows),'overdue_open':sum(r[11] for r in rows)}
    summary['open']=summary['requests']-summary['closed']; summary['closed_sla_rate']=summary['on_time_closed']/summary['closed']
    (destination/'expected_metrics.json').write_text(json.dumps(summary,indent=2)+'\n')
    return rows
if __name__=='__main__': generate(Path(__file__).parent/'data')

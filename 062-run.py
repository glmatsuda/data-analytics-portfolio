"""Build SQLite database and export analytics; Python 3.10+, no packages."""
from pathlib import Path
import csv, json, sqlite3, argparse
from generate_data import generate
BASE=Path(__file__).parent
def build(data):
    db=sqlite3.connect(':memory:'); db.row_factory=sqlite3.Row
    db.executescript((BASE/'sql/schema.sql').read_text())
    for table in ['products','orders']:
        with (Path(data)/f'{table}.csv').open(newline='') as f:
            reader=csv.DictReader(f); fields=reader.fieldnames
            db.executemany(f"INSERT INTO {table} VALUES ({','.join('?' for _ in fields)})",[tuple(r[k] for k in fields) for r in reader])
    return db
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=BASE/'example-output'); args=parser.parse_args()
    if not (BASE/'data/orders.csv').exists(): generate(BASE/'data')
    db=build(BASE/'data'); args.output.mkdir(parents=True,exist_ok=True)
    for name in ['monthly_performance','category_ranking','customer_repeat']:
        rows=db.execute((BASE/f'sql/{name}.sql').read_text()).fetchall()
        with (args.output/f'{name}.csv').open('w',newline='') as f:
            w=csv.writer(f); w.writerow(rows[0].keys()); w.writerows(rows)
    controls=dict(db.execute("SELECT COUNT(*) AS placed_orders, SUM(status='completed') AS completed_orders, SUM(net_revenue_cents) AS net_revenue_cents, SUM(contribution_cents) AS contribution_cents FROM order_metrics").fetchone())
    (args.output/'controls.json').write_text(json.dumps(controls,indent=2)+'\n')
    db.commit()
    with sqlite3.connect(args.output/'retail.db') as target: db.backup(target)
    print(json.dumps(controls)); db.close()
if __name__=='__main__': main()

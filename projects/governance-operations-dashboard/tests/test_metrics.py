import unittest, tempfile, csv, datetime, json
from pathlib import Path
from generate_data import generate, AS_OF, flags
class MetricTests(unittest.TestCase):
    def test_source_flags_reconcile(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp)
            with open(Path(tmp)/'requests.csv') as f: rows=list(csv.DictReader(f))
            closed=on_time=overdue=0
            self.assertEqual(len(rows),len({r['ticket_id'] for r in rows}))
            for r in rows:
                start=datetime.date.fromisoformat(r['created_date']); self.assertLessEqual(start,AS_OF)
                end=datetime.date.fromisoformat(r['closed_date']) if r['closed_date'] else AS_OF
                days=(end-start).days; self.assertEqual(days,int(r['age_or_cycle_days']))
                c=bool(r['closed_date']); closed+=c; on_time+=c and days<=int(r['sla_days']); overdue+=not c and days>int(r['sla_days'])
            expected=json.loads((Path(tmp)/'expected_metrics.json').read_text())
            self.assertEqual((closed,on_time,overdue),(expected['closed'],expected['on_time_closed'],expected['overdue_open']))
            self.assertEqual(480,expected['requests']); self.assertEqual(expected['open']+closed,480)
    def test_sla_boundary(self):
        # Exactly at the threshold is on time, and open is not yet overdue.
        self.assertEqual([1,1,0],flags(True,7,7))
        self.assertEqual([1,0,0],flags(True,8,7))
        self.assertEqual([0,0,0],flags(False,7,7))
        self.assertEqual([0,0,1],flags(False,8,7))
if __name__=='__main__': unittest.main()

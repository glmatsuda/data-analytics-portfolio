import unittest, tempfile, csv
from pathlib import Path
from consolidate import run, FIELDS
class ConsolidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.src=self.root/'in'; self.src.mkdir(); self.out=self.root/'out'
    def tearDown(self): self.tmp.cleanup()
    def write(self,rows,header=FIELDS):
        with (self.src/'a.csv').open('w',newline='') as f: w=csv.writer(f); w.writerow(header); w.writerows(rows)
    def test_duplicates_and_rerun_are_deterministic(self):
        row=['crm','accounts','account_id','integer','owner@example.com','Internal']; self.write([row,row])
        summary=run(self.src,self.out); self.assertEqual(1,summary['accepted_unique_columns']); self.assertEqual(1,summary['duplicate_rows_collapsed'])
        before={p.name:p.read_bytes() for p in self.out.iterdir()}; run(self.src,self.out)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.out.iterdir()})
    def test_conflict_quarantines_all_versions(self):
        a=['crm','accounts','id','integer','a@example.com','Internal']; b=a.copy(); b[-1]='Restricted'; self.write([a,b])
        summary=run(self.src,self.out); self.assertEqual(0,summary['accepted_unique_columns']); self.assertEqual(2,summary['conflicting_rows'])
    def test_schema_failure_preserves_existing_output(self):
        self.out.mkdir(); (self.out/'catalog.csv').write_text('keep')
        self.write([],['wrong']); self.assertRaises(ValueError,run,self.src,self.out)
        self.assertEqual('keep',(self.out/'catalog.csv').read_text())
    def test_missing_owner_rejected(self):
        self.write([['crm','accounts','id','integer','','Internal']]); self.assertEqual(1,run(self.src,self.out)['rejected_rows'])
    def test_no_inputs_and_nested_output_rejected(self):
        self.assertRaises(ValueError,run,self.src,self.out)
        self.assertRaises(ValueError,run,self.src,self.src/'output')
    def test_formula_injection_escaped_in_exceptions(self):
        self.write([['=1+1','accounts','id','integer','a@example.com','Internal']]); run(self.src,self.out)
        with (self.out/'exceptions.csv').open() as f: rows=list(csv.reader(f))
        self.assertEqual("'=1+1",rows[1][2])
if __name__=='__main__': unittest.main()

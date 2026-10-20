import unittest,csv,sqlite3,datetime
from prepare import BASE,prepare
class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):prepare()
    def test_calendar_coverage_and_nulls(self):
        with (BASE/'results/daily.csv').open() as f:rows=list(csv.DictReader(f))
        self.assertEqual(1096,len(rows));self.assertEqual(1096,len({r['date'] for r in rows}))
        for r in rows:
            if r['complete_day']=='1':self.assertEqual(int(r['crossings']),int(r['west_sidewalk'])+int(r['east_sidewalk']))
            else:self.assertEqual('',r['crossings'])
    def test_constraints_enforce_coverage(self):
        db=sqlite3.connect(BASE/'results/mobility.sqlite');db.execute('PRAGMA foreign_keys=ON')
        self.assertEqual([],db.execute('PRAGMA foreign_key_check').fetchall())
        with self.assertRaises(sqlite3.IntegrityError):db.execute("UPDATE fact_daily_crossings SET complete_day=0,crossings=1 WHERE rowid=1")
        db.close()
if __name__=='__main__':unittest.main()

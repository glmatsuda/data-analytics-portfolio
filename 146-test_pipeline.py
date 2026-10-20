import unittest,tempfile,sqlite3,csv,json
from pathlib import Path
from pipeline import build,BASE,number
class MartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name);cls.summary=build(BASE/'data/source.csv',cls.out)
        cls.db=sqlite3.connect(cls.out/'seattle-energy.sqlite');cls.db.execute('PRAGMA foreign_keys=ON')
    @classmethod
    def tearDownClass(cls):cls.db.close();cls.tmp.cleanup()
    def test_grain_and_source_count(self):
        with (BASE/'data/source.csv').open() as f:expected=sum(1 for _ in csv.DictReader(f))
        self.assertEqual(expected,self.db.execute('SELECT COUNT(*) FROM fact_building_energy').fetchone()[0])
    def test_join_preserves_population(self):
        self.assertEqual(self.summary['fact_rows'],self.db.execute('SELECT COUNT(*) FROM analytics_energy').fetchone()[0])
    def test_duplicate_key_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):self.db.execute('INSERT INTO fact_building_energy SELECT * FROM fact_building_energy LIMIT 1')
    def test_foreign_key_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):self.db.execute("UPDATE fact_building_energy SET property_id='ABSENT' WHERE rowid=1")
    def test_missing_differs_from_zero(self):
        self.assertIsNone(number(''));self.assertIsNone(number('NA'));self.assertEqual(0,number('0'));self.assertEqual(1234.5,number('1,234.5'))
    def test_source_hash_required(self):
        bad=self.out/'changed.csv';bad.write_text('changed')
        self.assertRaises(ValueError,build,bad,self.out/'other')
if __name__=='__main__':unittest.main()

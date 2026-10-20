from pathlib import Path
import csv,json,sqlite3,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import build
class ModelTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.summary=build.build(cls.tmp.name)
  cls.db=sqlite3.connect(Path(cls.tmp.name)/'seattle-energy.sqlite');cls.db.execute('PRAGMA foreign_keys=ON')
  with (build.BASE/'data/source.csv').open(newline='') as f:cls.source=list(csv.DictReader(f))
 @classmethod
 def tearDownClass(cls):cls.db.close();cls.tmp.cleanup()
 def rejects(self,sql,args=()):
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute(sql,args)
  self.db.rollback()
 def test_report_and_measurement_grains(self):
  self.assertEqual(len(self.source),self.db.execute('SELECT COUNT(*) FROM annual_report').fetchone()[0])
  self.assertEqual(len(self.source)*8,self.db.execute('SELECT COUNT(*) FROM measurement').fetchone()[0])
  self.assertEqual([],self.db.execute('SELECT report_id FROM measurement GROUP BY report_id HAVING COUNT(*)<>8').fetchall())
 def test_source_keys_and_values_round_trip(self):
  actual=self.db.execute('SELECT a.source_record,a.building_id,a.reporting_year,m.metric_code,m.raw_value,m.value,m.value_status FROM annual_report a JOIN measurement m USING(report_id)').fetchall()
  fields={m[0]:m[1] for m in build.METRICS}
  for record,bid,year,code,raw,value,status in actual:
   source=self.source[record-1]
   self.assertEqual((source['OSEBuildingID'],int(source['DataYear'])),(bid,year))
   self.assertEqual(source[fields[code]],raw)
   expected_raw=raw.strip().replace(',','')
   if expected_raw in ('','NA','N/A','null'):self.assertEqual((None,'missing'),(value,status))
   else:self.assertEqual((float(expected_raw),'reported'),(value,status))
 def test_preaggregation_prevents_fanout(self):
  self.assertEqual(len(self.source),self.db.execute('SELECT COUNT(*) FROM report_wide').fetchone()[0])
  for year in range(2015,2026):
   self.assertEqual(sum(int(r['DataYear'])==year for r in self.source),self.db.execute('SELECT COUNT(*) FROM report_wide WHERE reporting_year=?',(year,)).fetchone()[0])
 def test_foreign_key_rejects_orphan(self):
  self.rejects("INSERT INTO measurement VALUES(-1,'site_energy',1,'reported','1')")
 def test_natural_key_rejects_duplicate(self):
  self.rejects('INSERT INTO annual_report SELECT 999999,building_id,reporting_year,neighborhood_id,property_use_id,snapshot_id,999999,building_type,reported_year_built,reported_floors,compliance_status,demolished FROM annual_report LIMIT 1')
 def test_measurement_state_consistency(self):
  self.rejects("UPDATE measurement SET value=NULL,value_status='reported' WHERE report_id=1 AND metric_code='property_gfa'")
  self.rejects("UPDATE measurement SET value=0,value_status='missing' WHERE report_id=1 AND metric_code='property_gfa'")
 def test_missing_is_not_zero(self):
  count=self.db.execute("SELECT COUNT(*) FROM measurement WHERE value_status='missing' AND value IS NULL").fetchone()[0]
  self.assertEqual(22247,count)
 def test_annual_classification_preserved(self):
  source_labels={(r['OSEBuildingID'],int(r['DataYear'])):(r['Neighborhood'],r['EPAPropertyType']) for r in self.source}
  for bid,year,n,u in self.db.execute('SELECT building_id,reporting_year,neighborhood,property_use FROM report_wide'):
   self.assertEqual(source_labels[(bid,year)],(n,u))
 def test_traceability_and_integrity(self):
  self.assertEqual([],self.db.execute('PRAGMA foreign_key_check').fetchall())
  self.assertEqual('ok',self.db.execute('PRAGMA integrity_check').fetchone()[0])
  self.assertEqual(1,self.db.execute('SELECT COUNT(*) FROM source_snapshot').fetchone()[0])
 def test_parser_retains_invalid_separately(self):
  self.assertEqual((None,'invalid'),build.parse_number('not a number'))
  self.assertEqual((None,'invalid'),build.parse_number('NaN'))
  self.assertEqual((0.0,'reported'),build.parse_number('0'))
if __name__=='__main__':unittest.main()

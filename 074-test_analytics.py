import unittest, tempfile, csv, sqlite3
from pathlib import Path
from generate_data import generate
from run import build, BASE
class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); generate(self.tmp.name); self.db=build(self.tmp.name)
    def tearDown(self): self.db.close(); self.tmp.cleanup()
    def test_revenue_reconciles_to_independent_csv(self):
        with open(Path(self.tmp.name)/'products.csv') as f: products={r['product_id']:r for r in csv.DictReader(f)}
        with open(Path(self.tmp.name)/'orders.csv') as f: orders=list(csv.DictReader(f))
        expected=sum(int(r['quantity'])*int(products[r['product_id']]['price_cents'])-int(r['discount_cents']) for r in orders if r['status']=='completed')
        self.assertEqual(expected,self.db.execute('SELECT SUM(net_revenue_cents) FROM order_metrics').fetchone()[0])
        self.assertEqual(1800,len(orders))
    def test_months_and_window_boundary(self):
        rows=self.db.execute((BASE/'sql/monthly_performance.sql').read_text()).fetchall()
        self.assertEqual(6,len(rows)); self.assertIsNone(rows[0]['revenue_mom_change'])
        self.assertEqual(1800,sum(r['placed_orders'] for r in rows))
    def test_return_cancel_exclusion(self):
        self.assertEqual(0,self.db.execute("SELECT SUM(net_revenue_cents) FROM order_metrics WHERE status!='completed'").fetchone()[0])
    def test_duplicate_order_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError): self.db.execute('INSERT INTO orders SELECT * FROM orders LIMIT 1')
    def test_orphan_product_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError): self.db.execute("UPDATE orders SET product_id='absent' WHERE order_id='O00001'")
if __name__=='__main__': unittest.main()

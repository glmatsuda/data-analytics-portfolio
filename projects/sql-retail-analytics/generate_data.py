"""Deterministic synthetic order-level fixture. No real customers."""
from pathlib import Path
import csv, random, datetime
def generate(destination):
    destination = Path(destination); destination.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)
    products = [('P01','Workspace','Desk kit',4500,2300),('P02','Workspace','Stand',6900,3400),
                ('P03','Accessories','Cable kit',1900,700),('P04','Accessories','Hub',3900,1700),
                ('P05','Storage','Organizer',2900,1100),('P06','Storage','Case',5900,2800)]
    with (destination/'products.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['product_id','category','product_name','price_cents','unit_cost_cents']); w.writerows(products)
    with (destination/'orders.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['order_id','customer_id','order_date','product_id','region','channel','quantity','discount_cents','status'])
        for i in range(1,1801):
            product=rng.choice(products); qty=rng.randint(1,4)
            day=datetime.date(2026,1,1)+datetime.timedelta(days=rng.randrange(181))
            status=rng.choices(['completed','returned','cancelled'],[87,8,5])[0]
            w.writerow([f'O{i:05}',f'C{rng.randint(1,320):04}',day.isoformat(),product[0],
                rng.choice(['East','West','Central']),rng.choice(['Web','Marketplace']),qty,
                rng.choice([0,0,0,500,1000]),status])
if __name__=='__main__': generate(Path(__file__).parent/'data')

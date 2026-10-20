PRAGMA foreign_keys = ON;
CREATE TABLE products (
  product_id TEXT PRIMARY KEY, category TEXT NOT NULL, product_name TEXT NOT NULL,
  price_cents INTEGER NOT NULL CHECK(price_cents > 0),
  unit_cost_cents INTEGER NOT NULL CHECK(unit_cost_cents >= 0)
);
CREATE TABLE orders (
  order_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, order_date TEXT NOT NULL,
  product_id TEXT NOT NULL REFERENCES products(product_id), region TEXT NOT NULL,
  channel TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0),
  discount_cents INTEGER NOT NULL CHECK(discount_cents >= 0),
  status TEXT NOT NULL CHECK(status IN ('completed','returned','cancelled'))
);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE VIEW order_metrics AS
SELECT o.*, p.category, p.product_name,
  CASE WHEN status='completed' THEN quantity*price_cents-discount_cents ELSE 0 END AS net_revenue_cents,
  CASE WHEN status='completed' THEN quantity*(price_cents-unit_cost_cents)-discount_cents ELSE 0 END AS contribution_cents
FROM orders o JOIN products p USING(product_id);

-- Repeat purchaser = at least two completed orders in this six-month window.
WITH customers AS (
  SELECT customer_id, COUNT(*) AS completed_orders, SUM(net_revenue_cents) AS revenue_cents
  FROM order_metrics WHERE status='completed' GROUP BY customer_id
)
SELECT COUNT(*) AS purchasing_customers, SUM(completed_orders>=2) AS repeat_customers,
  ROUND(1.0*SUM(completed_orders>=2)/NULLIF(COUNT(*),0),4) AS repeat_purchaser_rate
FROM customers;

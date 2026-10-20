-- Grain: calendar month. Returns/cancellations contribute zero to revenue and cost.
WITH monthly AS (
  SELECT substr(order_date,1,7) AS month, COUNT(*) AS placed_orders,
    SUM(status='completed') AS completed_orders,
    SUM(net_revenue_cents) AS revenue_cents,
    SUM(contribution_cents) AS contribution_cents
  FROM order_metrics GROUP BY 1
), prior AS (
  SELECT *, LAG(revenue_cents) OVER (ORDER BY month) AS previous_revenue_cents
  FROM monthly
)
SELECT month, placed_orders, completed_orders,
  ROUND(revenue_cents/100.0,2) AS net_revenue_usd,
  ROUND(contribution_cents/100.0,2) AS contribution_usd,
  ROUND(1.0*contribution_cents/NULLIF(revenue_cents,0),4) AS contribution_margin,
  ROUND(1.0*revenue_cents/NULLIF(completed_orders,0)/100,2) AS average_completed_order_usd,
  ROUND(1.0*(revenue_cents-previous_revenue_cents)/NULLIF(previous_revenue_cents,0),4) AS revenue_mom_change
FROM prior ORDER BY month;

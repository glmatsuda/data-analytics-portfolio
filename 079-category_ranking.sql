WITH category AS (
  SELECT region, category, SUM(net_revenue_cents) AS revenue_cents,
    SUM(contribution_cents) AS contribution_cents
  FROM order_metrics GROUP BY region, category
)
SELECT region, category, ROUND(revenue_cents/100.0,2) AS net_revenue_usd,
  ROUND(contribution_cents/100.0,2) AS contribution_usd,
  DENSE_RANK() OVER (PARTITION BY region ORDER BY revenue_cents DESC) AS regional_rank
FROM category ORDER BY region, regional_rank, category;

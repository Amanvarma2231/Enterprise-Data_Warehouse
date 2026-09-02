-- =============================================================================
-- Analytics Query 6: Payment Gateway Health & Failure Rate Analysis
-- Transaction volume, gateway success rate %, and settlement amount
-- =============================================================================

SELECT
    payment_method,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN payment_status = 'Success' THEN 1 ELSE 0 END) AS successful_transactions,
    SUM(CASE WHEN payment_status = 'Failed' THEN 1 ELSE 0 END) AS failed_transactions,
    SUM(CASE WHEN payment_status = 'Refunded' THEN 1 ELSE 0 END) AS refunded_transactions,
    ROUND((SUM(CASE WHEN payment_status = 'Success' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100.0, 2) AS success_rate_pct,
    ROUND((SUM(CASE WHEN payment_status = 'Failed' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100.0, 2) AS failure_rate_pct,
    ROUND(SUM(CASE WHEN payment_status = 'Success' THEN payment_amount ELSE 0 END), 2) AS settled_volume_inr
FROM warehouse.fact_payments
GROUP BY payment_method
ORDER BY total_transactions DESC;

USE rms;

-- Fix all existing order totals by recalculating from order_items
UPDATE customer_order co
SET total_amount = (
    SELECT COALESCE(SUM(oi.quantity * oi.unit_price), 0)
    FROM order_item oi
    WHERE oi.order_id = co.order_id
);

-- Verify the fix
SELECT
    co.order_id,
    co.table_id,
    co.payment_status,
    co.total_amount as updated_total
FROM customer_order co
WHERE co.payment_status = 'UNPAID'
ORDER BY co.order_id;

SELECT 'Order totals updated successfully!' AS Status;

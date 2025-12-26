-- Create database views for reports
USE rms;

DROP VIEW IF EXISTS view_low_stock_items;
DROP VIEW IF EXISTS view_menu_profitability;
DROP VIEW IF EXISTS view_staff_performance;

CREATE VIEW view_low_stock_items AS
SELECT
    ing.ingredient_id,
    ing.name,
    ing.unit,
    ing.minimum_stock_threshold,
    ii.current_quantity,
    (ing.minimum_stock_threshold - ii.current_quantity) AS shortage,
    ii.average_unit_cost
FROM ingredient ing
JOIN inventory_item ii ON ing.ingredient_id = ii.ingredient_id
WHERE ii.current_quantity < ing.minimum_stock_threshold;

CREATE VIEW view_menu_profitability AS
SELECT
    mi.menu_item_id,
    mi.name,
    mi.category,
    mi.menu_price,
    COALESCE(SUM(mii.quantity_required * ii.average_unit_cost), 0) AS ingredient_cost,
    (mi.menu_price - COALESCE(SUM(mii.quantity_required * ii.average_unit_cost), 0)) AS profit_margin,
    CASE
        WHEN mi.menu_price > 0 THEN
            ((mi.menu_price - COALESCE(SUM(mii.quantity_required * ii.average_unit_cost), 0)) / mi.menu_price * 100)
        ELSE 0
    END AS profit_percentage
FROM menu_item mi
LEFT JOIN menu_item_ingredient mii ON mi.menu_item_id = mii.menu_item_id
LEFT JOIN inventory_item ii ON mii.ingredient_id = ii.ingredient_id
GROUP BY mi.menu_item_id, mi.name, mi.category, mi.menu_price;

CREATE VIEW view_staff_performance AS
SELECT
    e.employee_id,
    CONCAT(e.name, ' ', e.surname) AS staff_name,
    s.role,
    COUNT(DISTINCT co.order_id) AS total_orders,
    COALESCE(SUM(co.total_amount), 0) AS total_sales,
    COALESCE(AVG(co.total_amount), 0) AS avg_order_value
FROM employee e
JOIN staff s ON e.employee_id = s.employee_id
LEFT JOIN customer_order co ON e.employee_id = co.staff_id
WHERE co.payment_status = 'PAID'
GROUP BY e.employee_id, e.name, e.surname, s.role;

SELECT 'Views created successfully!' AS Status;

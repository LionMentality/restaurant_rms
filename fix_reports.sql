-- Fix reports and add inventory usage data
USE rms;

-- Drop existing views if they exist
DROP VIEW IF EXISTS view_low_stock_items;
DROP VIEW IF EXISTS view_menu_profitability;
DROP VIEW IF EXISTS view_staff_performance;

-- Create views for reports
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

-- Add sample inventory usage data for the past 30 days
-- Get ingredient IDs (assuming they exist from insert.sql)
SET @tomato_id = (SELECT ingredient_id FROM ingredient WHERE name = 'Tomatoes' LIMIT 1);
SET @lettuce_id = (SELECT ingredient_id FROM ingredient WHERE name = 'Lettuce' LIMIT 1);
SET @chicken_id = (SELECT ingredient_id FROM ingredient WHERE name = 'Chicken Breast' LIMIT 1);
SET @beef_id = (SELECT ingredient_id FROM ingredient WHERE name = 'Beef Sirloin' LIMIT 1);
SET @cheese_id = (SELECT ingredient_id FROM ingredient WHERE name = 'Mozzarella Cheese' LIMIT 1);
SET @flour_id = (SELECT ingredient_id FROM ingredient WHERE name = 'All-Purpose Flour' LIMIT 1);

-- Inventory adjustments (receiving shipments) - spread over 30 days
INSERT INTO inventory_usage (ingredient_id, usage_date, quantity_used, usage_type, note)
VALUES
    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 30 DAY), 50, 'ADJUSTMENT', 'Monthly shipment received'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 30 DAY), 30, 'ADJUSTMENT', 'Monthly shipment received'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 28 DAY), 40, 'ADJUSTMENT', 'Weekly shipment received'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 28 DAY), 35, 'ADJUSTMENT', 'Weekly shipment received'),
    (@cheese_id, DATE_SUB(CURDATE(), INTERVAL 25 DAY), 25, 'ADJUSTMENT', 'Shipment received'),
    (@flour_id, DATE_SUB(CURDATE(), INTERVAL 25 DAY), 100, 'ADJUSTMENT', 'Bulk order received'),

    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 21 DAY), 30, 'ADJUSTMENT', 'Weekly shipment received'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 21 DAY), 20, 'ADJUSTMENT', 'Weekly shipment received'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 20 DAY), 45, 'ADJUSTMENT', 'Weekly shipment received'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 20 DAY), 30, 'ADJUSTMENT', 'Weekly shipment received'),

    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 14 DAY), 35, 'ADJUSTMENT', 'Weekly shipment received'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 14 DAY), 25, 'ADJUSTMENT', 'Weekly shipment received'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 13 DAY), 40, 'ADJUSTMENT', 'Weekly shipment received'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 13 DAY), 35, 'ADJUSTMENT', 'Weekly shipment received'),

    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 7 DAY), 30, 'ADJUSTMENT', 'Weekly shipment received'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 7 DAY), 20, 'ADJUSTMENT', 'Weekly shipment received'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 6 DAY), 45, 'ADJUSTMENT', 'Weekly shipment received'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 6 DAY), 40, 'ADJUSTMENT', 'Weekly shipment received'),
    (@cheese_id, DATE_SUB(CURDATE(), INTERVAL 5 DAY), 30, 'ADJUSTMENT', 'Shipment received');

-- Waste tracking entries - spread over 30 days
INSERT INTO inventory_usage (ingredient_id, usage_date, quantity_used, usage_type, note)
VALUES
    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 28 DAY), 2.5, 'WASTE', 'Spoiled produce'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 26 DAY), 1.8, 'WASTE', 'Wilted leaves'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 24 DAY), 3.2, 'WASTE', 'Passed expiration date'),
    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 22 DAY), 1.5, 'WASTE', 'Bruised tomatoes'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 20 DAY), 2.0, 'WASTE', 'Spoiled produce'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 18 DAY), 2.8, 'WASTE', 'Discoloration'),
    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 16 DAY), 1.2, 'WASTE', 'Overripe'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 14 DAY), 1.5, 'WASTE', 'Wilted'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 12 DAY), 2.5, 'WASTE', 'Quality control'),
    (@cheese_id, DATE_SUB(CURDATE(), INTERVAL 10 DAY), 1.0, 'WASTE', 'Mold detected'),
    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 8 DAY), 1.8, 'WASTE', 'Spoiled produce'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 6 DAY), 1.3, 'WASTE', 'Wilted leaves'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 4 DAY), 2.2, 'WASTE', 'Quality control'),
    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 0.9, 'WASTE', 'Damaged in storage');

-- Sales usage (from orders) - spread over 30 days
INSERT INTO inventory_usage (ingredient_id, usage_date, quantity_used, usage_type, note)
VALUES
    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 29 DAY), 5.5, 'SALE', 'Used in customer orders'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 29 DAY), 3.2, 'SALE', 'Used in customer orders'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 27 DAY), 8.5, 'SALE', 'Used in customer orders'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 27 DAY), 6.8, 'SALE', 'Used in customer orders'),
    (@cheese_id, DATE_SUB(CURDATE(), INTERVAL 26 DAY), 4.2, 'SALE', 'Used in customer orders'),

    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 23 DAY), 6.2, 'SALE', 'Used in customer orders'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 23 DAY), 4.5, 'SALE', 'Used in customer orders'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 22 DAY), 9.5, 'SALE', 'Used in customer orders'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 21 DAY), 7.2, 'SALE', 'Used in customer orders'),
    (@cheese_id, DATE_SUB(CURDATE(), INTERVAL 20 DAY), 5.5, 'SALE', 'Used in customer orders'),

    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 17 DAY), 7.8, 'SALE', 'Used in customer orders'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 17 DAY), 5.2, 'SALE', 'Used in customer orders'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 15 DAY), 11.5, 'SALE', 'Used in customer orders'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 15 DAY), 8.8, 'SALE', 'Used in customer orders'),
    (@cheese_id, DATE_SUB(CURDATE(), INTERVAL 14 DAY), 6.2, 'SALE', 'Used in customer orders'),

    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 11 DAY), 6.5, 'SALE', 'Used in customer orders'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 11 DAY), 4.8, 'SALE', 'Used in customer orders'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 9 DAY), 10.2, 'SALE', 'Used in customer orders'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 9 DAY), 7.5, 'SALE', 'Used in customer orders'),
    (@cheese_id, DATE_SUB(CURDATE(), INTERVAL 8 DAY), 5.8, 'SALE', 'Used in customer orders'),

    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 5 DAY), 8.2, 'SALE', 'Used in customer orders'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 5 DAY), 5.5, 'SALE', 'Used in customer orders'),
    (@chicken_id, DATE_SUB(CURDATE(), INTERVAL 3 DAY), 12.5, 'SALE', 'Used in customer orders'),
    (@beef_id, DATE_SUB(CURDATE(), INTERVAL 3 DAY), 9.2, 'SALE', 'Used in customer orders'),
    (@cheese_id, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 6.5, 'SALE', 'Used in customer orders'),

    (@tomato_id, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 7.5, 'SALE', 'Used in customer orders'),
    (@lettuce_id, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 4.2, 'SALE', 'Used in customer orders'),
    (@chicken_id, CURDATE(), 10.8, 'SALE', 'Used in customer orders'),
    (@beef_id, CURDATE(), 8.5, 'SALE', 'Used in customer orders'),
    (@cheese_id, CURDATE(), 5.2, 'SALE', 'Used in customer orders');

SELECT 'Database views and inventory usage data added successfully!' AS Status;

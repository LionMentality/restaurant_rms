-- Sample orders across different dates for demonstration
-- Run this after schema.sql and insert.sql

USE rms;

-- Orders from 30 days ago
INSERT INTO customer_order (table_id, staff_id, order_datetime, total_amount, payment_status, special_requests)
VALUES
    (1, 3, DATE_SUB(NOW(), INTERVAL 30 DAY), 45.50, 'PAID', 'Extra napkins'),
    (2, 3, DATE_SUB(NOW(), INTERVAL 30 DAY), 67.80, 'PAID', NULL);

-- Orders from 20 days ago
INSERT INTO customer_order (table_id, staff_id, order_datetime, total_amount, payment_status, special_requests)
VALUES
    (3, 3, DATE_SUB(NOW(), INTERVAL 20 DAY), 89.25, 'PAID', 'No onions'),
    (4, 3, DATE_SUB(NOW(), INTERVAL 20 DAY), 123.40, 'PAID', 'Birthday celebration');

-- Orders from 15 days ago
INSERT INTO customer_order (table_id, staff_id, order_datetime, total_amount, payment_status, special_requests)
VALUES
    (1, 3, DATE_SUB(NOW(), INTERVAL 15 DAY), 56.90, 'PAID', NULL),
    (5, 3, DATE_SUB(NOW(), INTERVAL 15 DAY), 78.30, 'PAID', 'Gluten free');

-- Orders from 10 days ago
INSERT INTO customer_order (table_id, staff_id, order_datetime, total_amount, payment_status, special_requests)
VALUES
    (2, 3, DATE_SUB(NOW(), INTERVAL 10 DAY), 91.15, 'PAID', NULL),
    (6, 3, DATE_SUB(NOW(), INTERVAL 10 DAY), 134.50, 'PAID', 'Large party');

-- Orders from 7 days ago
INSERT INTO customer_order (table_id, staff_id, order_datetime, total_amount, payment_status, special_requests)
VALUES
    (3, 3, DATE_SUB(NOW(), INTERVAL 7 DAY), 45.75, 'PAID', NULL),
    (7, 3, DATE_SUB(NOW(), INTERVAL 7 DAY), 88.90, 'PAID', 'Window seat');

-- Orders from 5 days ago
INSERT INTO customer_order (table_id, staff_id, order_datetime, total_amount, payment_status, special_requests)
VALUES
    (1, 3, DATE_SUB(NOW(), INTERVAL 5 DAY), 102.40, 'PAID', NULL),
    (4, 3, DATE_SUB(NOW(), INTERVAL 5 DAY), 76.85, 'PAID', 'Quick service needed');

-- Orders from 3 days ago
INSERT INTO customer_order (table_id, staff_id, order_datetime, total_amount, payment_status, special_requests)
VALUES
    (2, 3, DATE_SUB(NOW(), INTERVAL 3 DAY), 65.20, 'PAID', NULL),
    (5, 3, DATE_SUB(NOW(), INTERVAL 3 DAY), 145.60, 'PAID', 'Anniversary dinner');

-- Orders from yesterday
INSERT INTO customer_order (table_id, staff_id, order_datetime, total_amount, payment_status, special_requests)
VALUES
    (3, 3, DATE_SUB(NOW(), INTERVAL 1 DAY), 54.30, 'PAID', NULL),
    (6, 3, DATE_SUB(NOW(), INTERVAL 1 DAY), 98.75, 'PAID', 'Vegetarian options');

-- Orders from today (some paid, some unpaid for active demonstration)
INSERT INTO customer_order (table_id, staff_id, order_datetime, total_amount, payment_status, special_requests)
VALUES
    (7, 3, NOW(), 0, 'UNPAID', NULL),
    (8, 3, NOW(), 0, 'UNPAID', 'Extra spicy');

-- Add some order items to recent orders for completeness
-- Get the most recent order IDs
SET @order1 = (SELECT order_id FROM customer_order ORDER BY order_datetime DESC LIMIT 1 OFFSET 0);
SET @order2 = (SELECT order_id FROM customer_order ORDER BY order_datetime DESC LIMIT 1 OFFSET 1);

-- Add items to these orders (assuming menu_item_ids 1-5 exist from insert.sql)
INSERT INTO order_item (order_id, menu_item_id, quantity, unit_price, item_status)
VALUES
    (@order1, 1, 2, 12.99, 'ORDERED'),
    (@order1, 2, 1, 15.99, 'ORDERED'),
    (@order2, 3, 1, 18.99, 'ORDERED'),
    (@order2, 4, 2, 22.99, 'ORDERED');

-- Create corresponding sale records for paid orders
INSERT INTO sale (order_id, sale_date, sale_amount)
SELECT order_id, DATE(order_datetime), total_amount
FROM customer_order
WHERE payment_status = 'PAID'
AND order_id NOT IN (SELECT order_id FROM sale WHERE order_id IS NOT NULL);

-- Add sample inventory usage data for reports
USE rms;

-- Inventory adjustments (receiving shipments) - spread over 30 days
INSERT INTO inventory_usage (ingredient_id, usage_date, quantity_used, usage_type, note)
VALUES
    -- Month ago shipments
    (1, DATE_SUB(CURDATE(), INTERVAL 30 DAY), 50, 'ADJUSTMENT', 'Monthly shipment received'),
    (2, DATE_SUB(CURDATE(), INTERVAL 30 DAY), 30, 'ADJUSTMENT', 'Monthly shipment received'),
    (9, DATE_SUB(CURDATE(), INTERVAL 28 DAY), 40, 'ADJUSTMENT', 'Weekly shipment received'),
    (10, DATE_SUB(CURDATE(), INTERVAL 28 DAY), 35, 'ADJUSTMENT', 'Weekly shipment received'),
    (13, DATE_SUB(CURDATE(), INTERVAL 25 DAY), 25, 'ADJUSTMENT', 'Shipment received'),
    (20, DATE_SUB(CURDATE(), INTERVAL 25 DAY), 100, 'ADJUSTMENT', 'Bulk order received'),

    -- 3 weeks ago
    (1, DATE_SUB(CURDATE(), INTERVAL 21 DAY), 30, 'ADJUSTMENT', 'Weekly shipment received'),
    (2, DATE_SUB(CURDATE(), INTERVAL 21 DAY), 20, 'ADJUSTMENT', 'Weekly shipment received'),
    (9, DATE_SUB(CURDATE(), INTERVAL 20 DAY), 45, 'ADJUSTMENT', 'Weekly shipment received'),
    (10, DATE_SUB(CURDATE(), INTERVAL 20 DAY), 30, 'ADJUSTMENT', 'Weekly shipment received'),

    -- 2 weeks ago
    (1, DATE_SUB(CURDATE(), INTERVAL 14 DAY), 35, 'ADJUSTMENT', 'Weekly shipment received'),
    (2, DATE_SUB(CURDATE(), INTERVAL 14 DAY), 25, 'ADJUSTMENT', 'Weekly shipment received'),
    (9, DATE_SUB(CURDATE(), INTERVAL 13 DAY), 40, 'ADJUSTMENT', 'Weekly shipment received'),
    (10, DATE_SUB(CURDATE(), INTERVAL 13 DAY), 35, 'ADJUSTMENT', 'Weekly shipment received'),

    -- Last week
    (1, DATE_SUB(CURDATE(), INTERVAL 7 DAY), 30, 'ADJUSTMENT', 'Weekly shipment received'),
    (2, DATE_SUB(CURDATE(), INTERVAL 7 DAY), 20, 'ADJUSTMENT', 'Weekly shipment received'),
    (9, DATE_SUB(CURDATE(), INTERVAL 6 DAY), 45, 'ADJUSTMENT', 'Weekly shipment received'),
    (10, DATE_SUB(CURDATE(), INTERVAL 6 DAY), 40, 'ADJUSTMENT', 'Weekly shipment received'),
    (13, DATE_SUB(CURDATE(), INTERVAL 5 DAY), 30, 'ADJUSTMENT', 'Shipment received');

-- Waste tracking entries
INSERT INTO inventory_usage (ingredient_id, usage_date, quantity_used, usage_type, note)
VALUES
    (1, DATE_SUB(CURDATE(), INTERVAL 28 DAY), 2.5, 'WASTE', 'Spoiled produce'),
    (2, DATE_SUB(CURDATE(), INTERVAL 26 DAY), 1.8, 'WASTE', 'Wilted leaves'),
    (9, DATE_SUB(CURDATE(), INTERVAL 24 DAY), 3.2, 'WASTE', 'Passed expiration date'),
    (1, DATE_SUB(CURDATE(), INTERVAL 22 DAY), 1.5, 'WASTE', 'Bruised tomatoes'),
    (2, DATE_SUB(CURDATE(), INTERVAL 20 DAY), 2.0, 'WASTE', 'Spoiled produce'),
    (10, DATE_SUB(CURDATE(), INTERVAL 18 DAY), 2.8, 'WASTE', 'Discoloration'),
    (1, DATE_SUB(CURDATE(), INTERVAL 16 DAY), 1.2, 'WASTE', 'Overripe'),
    (2, DATE_SUB(CURDATE(), INTERVAL 14 DAY), 1.5, 'WASTE', 'Wilted'),
    (9, DATE_SUB(CURDATE(), INTERVAL 12 DAY), 2.5, 'WASTE', 'Quality control'),
    (13, DATE_SUB(CURDATE(), INTERVAL 10 DAY), 1.0, 'WASTE', 'Mold detected'),
    (1, DATE_SUB(CURDATE(), INTERVAL 8 DAY), 1.8, 'WASTE', 'Spoiled produce'),
    (2, DATE_SUB(CURDATE(), INTERVAL 6 DAY), 1.3, 'WASTE', 'Wilted leaves'),
    (10, DATE_SUB(CURDATE(), INTERVAL 4 DAY), 2.2, 'WASTE', 'Quality control'),
    (1, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 0.9, 'WASTE', 'Damaged in storage');

-- Sales usage (from orders)
INSERT INTO inventory_usage (ingredient_id, usage_date, quantity_used, usage_type, note)
VALUES
    -- 4 weeks ago
    (1, DATE_SUB(CURDATE(), INTERVAL 29 DAY), 5.5, 'SALE', 'Used in customer orders'),
    (2, DATE_SUB(CURDATE(), INTERVAL 29 DAY), 3.2, 'SALE', 'Used in customer orders'),
    (9, DATE_SUB(CURDATE(), INTERVAL 27 DAY), 8.5, 'SALE', 'Used in customer orders'),
    (10, DATE_SUB(CURDATE(), INTERVAL 27 DAY), 6.8, 'SALE', 'Used in customer orders'),
    (13, DATE_SUB(CURDATE(), INTERVAL 26 DAY), 4.2, 'SALE', 'Used in customer orders'),

    -- 3 weeks ago
    (1, DATE_SUB(CURDATE(), INTERVAL 23 DAY), 6.2, 'SALE', 'Used in customer orders'),
    (2, DATE_SUB(CURDATE(), INTERVAL 23 DAY), 4.5, 'SALE', 'Used in customer orders'),
    (9, DATE_SUB(CURDATE(), INTERVAL 22 DAY), 9.5, 'SALE', 'Used in customer orders'),
    (10, DATE_SUB(CURDATE(), INTERVAL 21 DAY), 7.2, 'SALE', 'Used in customer orders'),
    (13, DATE_SUB(CURDATE(), INTERVAL 20 DAY), 5.5, 'SALE', 'Used in customer orders'),

    -- 2 weeks ago
    (1, DATE_SUB(CURDATE(), INTERVAL 17 DAY), 7.8, 'SALE', 'Used in customer orders'),
    (2, DATE_SUB(CURDATE(), INTERVAL 17 DAY), 5.2, 'SALE', 'Used in customer orders'),
    (9, DATE_SUB(CURDATE(), INTERVAL 15 DAY), 11.5, 'SALE', 'Used in customer orders'),
    (10, DATE_SUB(CURDATE(), INTERVAL 15 DAY), 8.8, 'SALE', 'Used in customer orders'),
    (13, DATE_SUB(CURDATE(), INTERVAL 14 DAY), 6.2, 'SALE', 'Used in customer orders'),

    -- Last week
    (1, DATE_SUB(CURDATE(), INTERVAL 11 DAY), 6.5, 'SALE', 'Used in customer orders'),
    (2, DATE_SUB(CURDATE(), INTERVAL 11 DAY), 4.8, 'SALE', 'Used in customer orders'),
    (9, DATE_SUB(CURDATE(), INTERVAL 9 DAY), 10.2, 'SALE', 'Used in customer orders'),
    (10, DATE_SUB(CURDATE(), INTERVAL 9 DAY), 7.5, 'SALE', 'Used in customer orders'),
    (13, DATE_SUB(CURDATE(), INTERVAL 8 DAY), 5.8, 'SALE', 'Used in customer orders'),

    -- This week
    (1, DATE_SUB(CURDATE(), INTERVAL 5 DAY), 8.2, 'SALE', 'Used in customer orders'),
    (2, DATE_SUB(CURDATE(), INTERVAL 5 DAY), 5.5, 'SALE', 'Used in customer orders'),
    (9, DATE_SUB(CURDATE(), INTERVAL 3 DAY), 12.5, 'SALE', 'Used in customer orders'),
    (10, DATE_SUB(CURDATE(), INTERVAL 3 DAY), 9.2, 'SALE', 'Used in customer orders'),
    (13, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 6.5, 'SALE', 'Used in customer orders'),

    -- Recent
    (1, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 7.5, 'SALE', 'Used in customer orders'),
    (2, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 4.2, 'SALE', 'Used in customer orders'),
    (9, CURDATE(), 10.8, 'SALE', 'Used in customer orders'),
    (10, CURDATE(), 8.5, 'SALE', 'Used in customer orders'),
    (13, CURDATE(), 5.2, 'SALE', 'Used in customer orders');

SELECT 'Inventory usage data added successfully!' AS Status;
SELECT COUNT(*) AS total_records FROM inventory_usage;

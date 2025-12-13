
USE rms;

SET FOREIGN_KEY_CHECKS = 0;

-- ==========================================
-- 1. EMPLOYEES (Managers + Staff)
-- ==========================================

INSERT INTO employee (name, surname, phone_number, email, address, salary, username, password_hash, is_active) VALUES
-- Managers
('John', 'Manager', '555-0001', 'john.manager@rms.com', '123 Main St, New York, NY 10001', 65000.00, 'jmanager', 'scrypt:32768:8:1$H6KIWGTKquIiaOwf$efdef9b44c81324355c00dcf0f2bfe1b496b3abb814e4c480eca05abab4ddf3a9d371f5deb0f681b291e4b8b85a75f342920ea75be23f4ff6078783b710a468f', TRUE),
('Sarah', 'Anderson', '555-0002', 'sarah.anderson@rms.com', '456 Oak Ave, New York, NY 10002', 62000.00, 'sanderson', 'scrypt:32768:8:1$H6KIWGTKquIiaOwf$efdef9b44c81324355c00dcf0f2bfe1b496b3abb814e4c480eca05abab4ddf3a9d371f5deb0f681b291e4b8b85a75f342920ea75be23f4ff6078783b710a468f', TRUE),

-- Staff (Servers)
('Emily', 'Williams', '555-0100', 'emily.w@rms.com', '789 Pine Rd, Brooklyn, NY 11201', 35000.00, 'ewilliams', 'scrypt:32768:8:1$H6KIWGTKquIiaOwf$efdef9b44c81324355c00dcf0f2bfe1b496b3abb814e4c480eca05abab4ddf3a9d371f5deb0f681b291e4b8b85a75f342920ea75be23f4ff6078783b710a468f', TRUE),
('Michael', 'Chen', '555-0101', 'michael.c@rms.com', '321 Elm St, Brooklyn, NY 11202', 33000.00, 'scrypt:32768:8:1$H6KIWGTKquIiaOwf$efdef9b44c81324355c00dcf0f2bfe1b496b3abb814e4c480eca05abab4ddf3a9d371f5deb0f681b291e4b8b85a75f342920ea75be23f4ff6078783b710a468f', TRUE),
('David', 'Martinez', '555-0102', 'david.m@rms.com', '654 Maple Dr, Queens, NY 11354', 34000.00, 'dmartinez', 'scrypt:32768:8:1$H6KIWGTKquIiaOwf$efdef9b44c81324355c00dcf0f2bfe1b496b3abb814e4c480eca05abab4ddf3a9d371f5deb0f681b291e4b8b85a75f342920ea75be23f4ff6078783b710a468f', TRUE),
('Lisa', 'Anderson', '555-0103', 'lisa.a@rms.com', '987 Cedar Ln, Queens, NY 11355', 33500.00, 'landerson', 'scrypt:32768:8:1$H6KIWGTKquIiaOwf$efdef9b44c81324355c00dcf0f2bfe1b496b3abb814e4c480eca05abab4ddf3a9d371f5deb0f681b291e4b8b85a75f342920ea75be23f4ff6078783b710a468f', TRUE),

-- Staff (Kitchen)
('Robert', 'Thompson', '555-0104', 'robert.t@rms.com', '147 Birch St, Bronx, NY 10451', 38000.00, 'rthompson', 'scrypt:32768:8:1$H6KIWGTKquIiaOwf$efdef9b44c81324355c00dcf0f2bfe1b496b3abb814e4c480eca05abab4ddf3a9d371f5deb0f681b291e4b8b85a75f342920ea75be23f4ff6078783b710a468f', TRUE),
('Amanda', 'Garcia', '555-0105', 'amanda.g@rms.com', '258 Willow Way, Bronx, NY 10452', 36000.00, 'agarcia', 'scrypt:32768:8:1$H6KIWGTKquIiaOwf$efdef9b44c81324355c00dcf0f2bfe1b496b3abb814e4c480eca05abab4ddf3a9d371f5deb0f681b291e4b8b85a75f342920ea75be23f4ff6078783b710a468f', TRUE),

-- Staff (Bartender)
('Kevin', 'Brown', '555-0106', 'kevin.b@rms.com', '369 Ash Ct, Manhattan, NY 10003', 34500.00, 'kbrown', 'scrypt:32768:8:1$H6KIWGTKquIiaOwf$efdef9b44c81324355c00dcf0f2bfe1b496b3abb814e4c480eca05abab4ddf3a9d371f5deb0f681b291e4b8b85a75f342920ea75be23f4ff6078783b710a468f', TRUE);

-- Assign Manager roles
INSERT INTO manager (employee_id) VALUES (1), (2);

-- Assign Staff roles
INSERT INTO staff (employee_id, role, manager_id) VALUES
(3, 'Server', 1),
(4, 'Server', 1),
(5, 'Server', 1),
(6, 'Server', 2),
(7, 'Chef', 1),
(8, 'Sous Chef', 1),
(9, 'Bartender', 2);

-- ==========================================
-- 2. INGREDIENTS
-- ==========================================

INSERT INTO ingredient (name, unit, minimum_stock_threshold) VALUES
-- Vegetables & Produce
('Tomatoes', 'kg', 5.0),
('Lettuce', 'heads', 10),
('Onions', 'kg', 3.0),
('Garlic', 'kg', 1.0),
('Bell Peppers', 'kg', 2.0),
('Mushrooms', 'kg', 2.0),
('Basil', 'bunches', 5),
('Parsley', 'bunches', 5),

-- Proteins
('Chicken Breast', 'kg', 10.0),
('Beef Sirloin', 'kg', 8.0),
('Salmon Fillet', 'kg', 6.0),
('Shrimp', 'kg', 5.0),

-- Dairy
('Mozzarella Cheese', 'kg', 4.0),
('Parmesan Cheese', 'kg', 2.0),
('Butter', 'kg', 3.0),
('Heavy Cream', 'L', 5.0),

-- Pantry
('Pasta (Spaghetti)', 'kg', 10.0),
('Pasta (Penne)', 'kg', 8.0),
('Rice', 'kg', 15.0),
('Flour', 'kg', 20.0),
('Olive Oil', 'L', 10.0),
('Tomato Sauce', 'L', 8.0),
('Balsamic Vinegar', 'L', 2.0),

-- Beverages
('Coffee Beans', 'kg', 5.0),
('Tea Bags', 'boxes', 3),
('Orange Juice', 'L', 10.0),
('Sparkling Water', 'L', 20.0);

-- ==========================================
-- 3. INVENTORY ITEMS
-- ==========================================

INSERT INTO inventory_item (ingredient_id, current_quantity, average_unit_cost, expiration_date) VALUES
-- Vegetables & Produce
(1, 25.0, 3.50, '2025-12-20'),
(2, 15, 1.50, '2025-12-18'),
(3, 12.0, 2.00, '2026-01-15'),
(4, 4.0, 8.00, '2026-02-01'),
(5, 8.0, 4.50, '2025-12-22'),
(6, 6.0, 5.00, '2025-12-19'),
(7, 8, 2.50, '2025-12-17'),
(8, 10, 2.00, '2025-12-18'),

-- Proteins
(9, 18.0, 8.50, '2025-12-16'),
(10, 15.0, 15.00, '2025-12-17'),
(11, 12.0, 18.00, '2025-12-15'),
(12, 8.0, 22.00, '2025-12-14'),

-- Dairy
(13, 10.0, 12.00, '2025-12-25'),
(14, 5.0, 18.00, '2026-01-10'),
(15, 8.0, 6.00, '2025-12-30'),
(16, 12.0, 4.50, '2025-12-28'),

-- Pantry
(17, 30.0, 3.00, '2026-06-01'),
(18, 25.0, 3.20, '2026-06-01'),
(19, 40.0, 2.00, '2026-08-01'),
(20, 50.0, 1.50, '2026-09-01'),
(21, 25.0, 8.00, '2026-03-01'),
(22, 20.0, 2.80, '2026-02-01'),
(23, 4.0, 12.00, '2026-05-01'),

-- Beverages
(24, 8.0, 15.00, '2026-01-15'),
(25, 5, 8.00, '2026-02-01'),
(26, 30.0, 1.20, '2026-01-20'),
(27, 50.0, 0.80, '2026-03-01');

-- ==========================================
-- 4. MENU ITEMS
-- ==========================================

INSERT INTO menu_item (name, category, menu_price, is_available, description) VALUES
-- Appetizers
('Bruschetta', 'Appetizer', 10.99, TRUE, 'Toasted bread with fresh tomatoes, garlic, and basil'),
('Caesar Salad', 'Appetizer', 12.50, TRUE, 'Fresh romaine lettuce with parmesan and croutons'),
('Caprese Salad', 'Appetizer', 13.99, TRUE, 'Fresh mozzarella, tomatoes, and basil with balsamic'),
('Garlic Bread', 'Appetizer', 6.99, TRUE, 'Homemade bread with garlic butter'),

-- Main Courses
('Spaghetti Carbonara', 'Main Course', 18.99, TRUE, 'Classic Italian pasta with bacon and cream sauce'),
('Grilled Chicken', 'Main Course', 22.50, TRUE, 'Herb-marinated chicken breast with vegetables'),
('Margherita Pizza', 'Main Course', 16.99, TRUE, 'Classic pizza with tomato sauce and mozzarella'),
('Beef Steak', 'Main Course', 32.99, TRUE, '8oz sirloin steak with mashed potatoes'),
('Salmon Fillet', 'Main Course', 28.99, TRUE, 'Grilled salmon with lemon butter sauce'),
('Penne Arrabbiata', 'Main Course', 17.50, TRUE, 'Spicy tomato sauce with penne pasta'),
('Mushroom Risotto', 'Main Course', 19.99, TRUE, 'Creamy rice with wild mushrooms'),
('Shrimp Scampi', 'Main Course', 26.99, TRUE, 'Garlic butter shrimp with linguine'),

-- Desserts
('Tiramisu', 'Dessert', 8.99, TRUE, 'Classic Italian coffee-flavored dessert'),
('Chocolate Lava Cake', 'Dessert', 9.99, TRUE, 'Warm chocolate cake with molten center'),
('Panna Cotta', 'Dessert', 7.99, TRUE, 'Italian cream dessert with berry sauce'),
('Cheesecake', 'Dessert', 8.50, TRUE, 'New York style cheesecake'),

-- Beverages
('Espresso', 'Beverage', 3.50, TRUE, 'Double shot of Italian espresso'),
('Cappuccino', 'Beverage', 4.50, TRUE, 'Espresso with steamed milk foam'),
('Fresh Orange Juice', 'Beverage', 4.99, TRUE, 'Freshly squeezed orange juice'),
('Sparkling Water', 'Beverage', 2.99, TRUE, 'San Pellegrino sparkling water'),
('House Wine (Glass)', 'Beverage', 8.99, TRUE, 'Red or white wine by the glass');

-- ==========================================
-- 5. MENU ITEM INGREDIENTS (Recipes)
-- ==========================================

INSERT INTO menu_item_ingredient (menu_item_id, ingredient_id, quantity_required) VALUES
-- Bruschetta (1)
(1, 1, 0.15), -- Tomatoes
(1, 4, 0.02), -- Garlic
(1, 7, 0.05), -- Basil

-- Caesar Salad (2)
(2, 2, 0.25), -- Lettuce
(2, 14, 0.03), -- Parmesan

-- Caprese Salad (3)
(3, 1, 0.15), -- Tomatoes
(3, 13, 0.15), -- Mozzarella
(3, 7, 0.05), -- Basil

-- Spaghetti Carbonara (5)
(5, 17, 0.25), -- Pasta
(5, 16, 0.10), -- Cream
(5, 14, 0.05), -- Parmesan

-- Grilled Chicken (6)
(6, 9, 0.30), -- Chicken
(6, 4, 0.02), -- Garlic
(6, 21, 0.05), -- Olive Oil

-- Margherita Pizza (7)
(7, 20, 0.20), -- Flour
(7, 1, 0.15), -- Tomatoes
(7, 13, 0.20), -- Mozzarella
(7, 7, 0.05), -- Basil

-- Beef Steak (8)
(8, 10, 0.35), -- Beef
(8, 15, 0.05), -- Butter

-- Salmon Fillet (9)
(9, 11, 0.30), -- Salmon
(9, 15, 0.03), -- Butter

-- Penne Arrabbiata (10)
(10, 18, 0.25), -- Penne
(10, 22, 0.15), -- Tomato Sauce
(10, 4, 0.02), -- Garlic

-- Shrimp Scampi (12)
(12, 12, 0.25), -- Shrimp
(12, 4, 0.03), -- Garlic
(12, 15, 0.05); -- Butter

-- ==========================================
-- 6. RESTAURANT TABLES
-- ==========================================

INSERT INTO restaurant_table (table_number, capacity, status) VALUES
(1, 4, 'OCCUPIED'),
(2, 2, 'OCCUPIED'),
(3, 6, 'AVAILABLE'),
(4, 4, 'RESERVED'),
(5, 8, 'OCCUPIED'),
(6, 2, 'AVAILABLE'),
(7, 4, 'OCCUPIED'),
(8, 4, 'OCCUPIED'),
(9, 6, 'AVAILABLE'),
(10, 2, 'AVAILABLE');

-- ==========================================
-- 7. SCHEDULES (Sample week: Dec 8-14, 2025)
-- ==========================================

INSERT INTO schedule (staff_id, shift_date, start_time, end_time, assigned_role) VALUES
-- Emily Williams (3) - Server
(3, '2025-12-08', '09:00:00', '17:00:00', 'Morning Server'),
(3, '2025-12-09', '14:00:00', '22:00:00', 'Evening Server'),
(3, '2025-12-10', '09:00:00', '17:00:00', 'Morning Server'),
(3, '2025-12-12', '14:00:00', '22:00:00', 'Evening Server'),
(3, '2025-12-13', '10:00:00', '18:00:00', 'Day Server'),

-- Michael Chen (4) - Server
(4, '2025-12-08', '14:00:00', '22:00:00', 'Evening Server'),
(4, '2025-12-09', '09:00:00', '17:00:00', 'Morning Server'),
(4, '2025-12-11', '14:00:00', '22:00:00', 'Evening Server'),
(4, '2025-12-13', '14:00:00', '22:00:00', 'Evening Server'),
(4, '2025-12-14', '10:00:00', '18:00:00', 'Day Server'),

-- David Martinez (5) - Server
(5, '2025-12-08', '10:00:00', '18:00:00', 'Day Server'),
(5, '2025-12-10', '14:00:00', '22:00:00', 'Evening Server'),
(5, '2025-12-12', '09:00:00', '17:00:00', 'Morning Server'),
(5, '2025-12-14', '14:00:00', '22:00:00', 'Evening Server'),

-- Robert Thompson (7) - Chef
(7, '2025-12-08', '10:00:00', '22:00:00', 'Head Chef'),
(7, '2025-12-09', '10:00:00', '22:00:00', 'Head Chef'),
(7, '2025-12-10', '10:00:00', '22:00:00', 'Head Chef'),
(7, '2025-12-11', '10:00:00', '22:00:00', 'Head Chef'),
(7, '2025-12-12', '10:00:00', '22:00:00', 'Head Chef');

-- ==========================================
-- 8. CUSTOMER ORDERS (Active orders)
-- ==========================================

INSERT INTO customer_order (table_id, staff_id, order_datetime, payment_status, special_requests, total_amount) VALUES
(1, 3, '2025-12-13 12:15:00', 'UNPAID', 'No onions please', 0),
(2, 3, '2025-12-13 12:30:00', 'UNPAID', NULL, 0),
(5, 4, '2025-12-13 11:45:00', 'UNPAID', 'Extra spicy', 0),
(7, 5, '2025-12-13 13:00:00', 'UNPAID', NULL, 0),
(8, 3, '2025-12-13 12:45:00', 'UNPAID', 'Gluten-free if possible', 0);

-- ==========================================
-- 9. ORDER ITEMS
-- ==========================================

INSERT INTO order_item (order_id, menu_item_id, quantity, unit_price, item_status) VALUES
-- Order 1 (Table 1) - Family lunch
(1, 1, 2, 10.99, 'SERVED'),    -- 2x Bruschetta
(1, 5, 2, 18.99, 'SERVED'),    -- 2x Carbonara
(1, 6, 1, 22.50, 'PREPARED'),  -- 1x Chicken
(1, 9, 1, 28.99, 'PREPARED'),  -- 1x Salmon
(1, 13, 2, 8.99, 'ORDERED'),   -- 2x Tiramisu

-- Order 2 (Table 2) - Quick lunch
(2, 2, 1, 12.50, 'SERVED'),    -- 1x Caesar Salad
(2, 7, 1, 16.99, 'PREPARED'),  -- 1x Pizza

-- Order 3 (Table 5) - Large group
(3, 3, 3, 13.99, 'SERVED'),    -- 3x Caprese
(3, 7, 4, 16.99, 'PREPARED'),  -- 4x Pizza
(3, 5, 2, 18.99, 'PREPARED'),  -- 2x Carbonara
(3, 18, 4, 4.50, 'SERVED'),    -- 4x Cappuccino
(3, 13, 3, 8.99, 'ORDERED'),   -- 3x Tiramisu

-- Order 4 (Table 7) - Dinner
(4, 4, 2, 6.99, 'SERVED'),     -- 2x Garlic Bread
(4, 8, 2, 32.99, 'ORDERED'),   -- 2x Steak
(4, 21, 2, 8.99, 'SERVED'),    -- 2x Wine

-- Order 5 (Table 8) - Light dinner
(5, 2, 2, 12.50, 'SERVED'),    -- 2x Caesar
(5, 9, 2, 28.99, 'PREPARED'),  -- 2x Salmon
(5, 15, 2, 7.99, 'ORDERED');   -- 2x Panna Cotta

-- ==========================================
-- 10. STAFF REQUESTS (Samples)
-- ==========================================

INSERT INTO staff_request (staff_id, manager_id, request_type, request_date, start_date, end_date, reason, status) VALUES
(3, 1, 'TIME_OFF', '2025-12-10', '2025-12-20', '2025-12-22', 'Family vacation', 'PENDING'),
(4, 1, 'OVERTIME', '2025-12-11', '2025-12-15', NULL, 'Need extra hours', 'PENDING'),
(5, 1, 'TIME_OFF', '2025-12-08', '2025-12-18', '2025-12-19', 'Doctor appointment', 'APPROVED'),
(6, 2, 'AVAILABILITY', '2025-12-09', '2025-12-16', NULL, 'Available evening shifts', 'APPROVED'),
(7, 1, 'TIME_OFF', '2025-12-05', '2025-12-14', '2025-12-14', 'Personal day', 'REJECTED');

-- ==========================================
-- 11. WASTE TRACKING (Sample data)
-- ==========================================

INSERT INTO waste_tracking (ingredient_id, waste_seq, waste_date, amount_wasted, reason) VALUES
(1, 1, '2025-12-10', 2.5, 'Expired'),
(2, 1, '2025-12-11', 3.0, 'Spoiled'),
(11, 1, '2025-12-12', 1.0, 'Expired'),
(12, 1, '2025-12-09', 0.5, 'Dropped'),
(7, 1, '2025-12-13', 2.0, 'Wilted');

-- ==========================================
-- 12. EXPENSES (Sample)
-- ==========================================

INSERT INTO expense (manager_id, expense_type, expense_date, amount, description) VALUES
(1, 'Equipment', '2025-12-01', 1500.00, 'New oven for kitchen'),
(1, 'Supplies', '2025-12-05', 450.00, 'Cleaning supplies and utensils'),
(2, 'Marketing', '2025-12-08', 300.00, 'Social media advertising'),
(1, 'Utilities', '2025-12-10', 850.00, 'Electricity and water bills'),
(2, 'Maintenance', '2025-12-12', 600.00, 'HVAC system repair');

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Database seeded successfully!' AS Status;
SELECT CONCAT(COUNT(*), ' employees') AS Employees FROM employee;
SELECT CONCAT(COUNT(*), ' ingredients') AS Ingredients FROM ingredient;
SELECT CONCAT(COUNT(*), ' menu items') AS Menu_Items FROM menu_item;
SELECT CONCAT(COUNT(*), ' tables') AS Tables FROM restaurant_table;
SELECT CONCAT(COUNT(*), ' active orders') AS Active_Orders FROM customer_order WHERE payment_status = 'UNPAID';
SELECT CONCAT(COUNT(*), ' schedules') AS Schedules FROM schedule;
SELECT CONCAT(COUNT(*), ' staff requests') AS Staff_Requests FROM staff_request;

SELECT '===========================================' AS '';
SELECT 'LOGIN CREDENTIALS (password: password123)' AS '';
SELECT '===========================================' AS '';
SELECT username, 
       CASE WHEN employee_id IN (1,2) THEN 'Manager' ELSE 'Staff' END AS Role
FROM employee
ORDER BY employee_id;
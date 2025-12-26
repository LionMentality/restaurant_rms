USE rms;

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS trg_update_order_total_after_insert;
DROP TRIGGER IF EXISTS trg_log_inventory_usage_after_insert;
DROP TRIGGER IF EXISTS trg_low_stock_after_insert;
DROP TRIGGER IF EXISTS trg_low_stock_after_update;

DELIMITER $$

-- Update order total after inserting an order item
CREATE TRIGGER trg_update_order_total_after_insert
AFTER INSERT ON order_item
FOR EACH ROW
BEGIN
  UPDATE customer_order
  SET total_amount = total_amount + (NEW.quantity * NEW.unit_price)
  WHERE order_id = NEW.order_id;
END$$

-- Log inventory usage after inserting an order item
CREATE TRIGGER trg_log_inventory_usage_after_insert
AFTER INSERT ON order_item
FOR EACH ROW
BEGIN
  INSERT INTO inventory_usage (ingredient_id, usage_date, quantity_used, usage_type, note)
  SELECT
    mii.ingredient_id,
    CURRENT_DATE,
    mii.quantity_required * NEW.quantity,
    'SALE',
    CONCAT('Order ', NEW.order_id)
  FROM menu_item_ingredient AS mii
  WHERE mii.menu_item_id = NEW.menu_item_id;
END$$

-- Create a low-stock alert after inventory insert
CREATE TRIGGER trg_low_stock_after_insert
AFTER INSERT ON inventory_item
FOR EACH ROW
BEGIN
  IF NEW.current_quantity < (
    SELECT minimum_stock_threshold
    FROM ingredient
    WHERE ingredient_id = NEW.ingredient_id
  ) THEN
    INSERT INTO inventory_alert (ingredient_id, current_qty, message)
    VALUES (NEW.ingredient_id, NEW.current_quantity, 'Stock below minimum threshold');
  END IF;
END$$

-- Create a low-stock alert after inventory update
CREATE TRIGGER trg_low_stock_after_update
AFTER UPDATE ON inventory_item
FOR EACH ROW
BEGIN
  IF NEW.current_quantity < (
    SELECT minimum_stock_threshold
    FROM ingredient
    WHERE ingredient_id = NEW.ingredient_id
  ) THEN
    INSERT INTO inventory_alert (ingredient_id, current_qty, message)
    VALUES (NEW.ingredient_id, NEW.current_quantity, 'Stock below minimum threshold');
  END IF;
END$$

DELIMITER ;

SELECT 'Triggers created successfully!' AS Status;
SHOW TRIGGERS;

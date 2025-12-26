#!/usr/bin/env python3
from db import get_conn

conn = get_conn()
cur = conn.cursor()

print("Creating triggers...")

# Drop existing triggers if they exist
try:
    cur.execute("DROP TRIGGER IF EXISTS trg_update_order_total_after_insert")
    cur.execute("DROP TRIGGER IF EXISTS trg_log_inventory_usage_after_insert")
    cur.execute("DROP TRIGGER IF EXISTS trg_low_stock_after_insert")
    cur.execute("DROP TRIGGER IF EXISTS trg_low_stock_after_update")
    print("Dropped existing triggers (if any)")
except Exception as e:
    print(f"Note: {e}")

# Create trigger to update order total after inserting an order item
cur.execute("""
CREATE TRIGGER trg_update_order_total_after_insert
AFTER INSERT ON order_item
FOR EACH ROW
BEGIN
  UPDATE customer_order
  SET total_amount = total_amount + (NEW.quantity * NEW.unit_price)
  WHERE order_id = NEW.order_id;
END
""")
print("✓ Created: trg_update_order_total_after_insert")

# Create trigger to log inventory usage after inserting an order item
cur.execute("""
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
END
""")
print("✓ Created: trg_log_inventory_usage_after_insert")

# Create trigger for low-stock alert after inventory insert
cur.execute("""
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
END
""")
print("✓ Created: trg_low_stock_after_insert")

# Create trigger for low-stock alert after inventory update
cur.execute("""
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
END
""")
print("✓ Created: trg_low_stock_after_update")

conn.commit()
conn.close()

print("\nAll triggers created successfully!")
print("New orders will now automatically update totals.")

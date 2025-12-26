#!/usr/bin/env python3
from db import get_conn

conn = get_conn()
cur = conn.cursor(dictionary=True)

# Fix all existing order totals
cur.execute("""
    UPDATE customer_order co
    SET total_amount = (
        SELECT COALESCE(SUM(oi.quantity * oi.unit_price), 0)
        FROM order_item oi
        WHERE oi.order_id = co.order_id
    )
""")

conn.commit()

# Verify the fix
cur.execute("""
    SELECT
        co.order_id,
        co.table_id,
        co.payment_status,
        co.total_amount as updated_total
    FROM customer_order co
    WHERE co.payment_status = 'UNPAID'
    ORDER BY co.order_id
""")

orders = cur.fetchall()
print('Updated order totals:')
for order in orders:
    print(f'  Order {order["order_id"]} (Table {order["table_id"]}): ${float(order["updated_total"]):.2f}')

# Calculate total revenue
cur.execute("""
    SELECT COALESCE(SUM(total_amount), 0) AS total_revenue
    FROM customer_order
    WHERE payment_status = 'UNPAID'
""")
revenue = cur.fetchone()
print(f'\nTotal current revenue: ${float(revenue["total_revenue"]):.2f}')

conn.close()
print('\nOrder totals fixed successfully!')

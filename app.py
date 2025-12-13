from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_conn

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"

def require_login():
    return "user_id" in session

@app.route("/", methods=["GET"])
def root():
    return redirect(url_for("dashboard") if require_login() else url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None)

    username = request.form.get("username","").strip()
    password = request.form.get("password","")

    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT employee_id, name, surname, username, password_hash, is_active
        FROM employee
        WHERE username = %s
    """, (username,))
    user = cur.fetchone()
    conn.close()

    if not user or not user["is_active"] or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid credentials.")

    session["user_id"] = user["employee_id"]
    session["full_name"] = f"{user['name']} {user['surname']}"
    session["username"] = user["username"]

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM manager WHERE employee_id=%s", (user["employee_id"],))
    is_manager = cur.fetchone() is not None
    conn.close()
    session["role"] = "manager" if is_manager else "staff"

    return redirect(url_for("dashboard"))

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", error=None)

    name = request.form.get("name", "").strip()
    surname = request.form.get("surname", "").strip()
    email = request.form.get("email", "").strip()
    phone_number = request.form.get("phone_number", "").strip()
    address = request.form.get("address", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "staff")
    staff_role = request.form.get("staff_role", "").strip()

    if not all([name, surname, address, username, password]):
        return render_template("register.html", error="Please fill all required fields.")

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT employee_id FROM employee WHERE username = %s", (username,))
    if cur.fetchone():
        conn.close()
        return render_template("register.html", error="Username already exists.")

    if email:
        cur.execute("SELECT employee_id FROM employee WHERE email = %s", (email,))
        if cur.fetchone():
            conn.close()
            return render_template("register.html", error="Email already registered.")

    password_hash = generate_password_hash(password)

    cur.execute("""
        INSERT INTO employee (name, surname, phone_number, email, address, username, password_hash, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
    """, (name, surname, phone_number or None, email or None, address, username, password_hash))
    
    employee_id = cur.lastrowid

    if role == "manager":
        cur.execute("INSERT INTO manager (employee_id) VALUES (%s)", (employee_id,))
    else:
        cur.execute("SELECT employee_id FROM manager LIMIT 1")
        manager_row = cur.fetchone()
        manager_id = manager_row["employee_id"] if manager_row else None
        
        if not manager_id:
            conn.rollback()
            conn.close()
            return render_template("register.html", error="No manager found. Please contact admin.")
        
        cur.execute("""
            INSERT INTO staff (employee_id, role, manager_id)
            VALUES (%s, %s, %s)
        """, (employee_id, staff_role or None, manager_id))

    conn.commit()
    conn.close()

    flash("Account created successfully! Please login.", "success")
    return redirect(url_for("login"))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not require_login():
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        surname = request.form.get("surname", "").strip()
        email = request.form.get("email", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        address = request.form.get("address", "").strip()

        if not all([name, surname, address]):
            return render_template("profile.html", user={}, error="Please fill all required fields.")

        cur.execute("""
            UPDATE employee
            SET name = %s, surname = %s, email = %s, phone_number = %s, address = %s
            WHERE employee_id = %s
        """, (name, surname, email or None, phone_number or None, address, user_id))
        
        conn.commit()
        session["full_name"] = f"{name} {surname}"
        flash("Profile updated successfully!", "success")

    cur.execute("""
        SELECT 
            e.employee_id, e.name, e.surname, e.email, e.phone_number, 
            e.address, e.username,
            s.role AS staff_role,
            m_emp.name AS manager_name,
            m_emp.email AS manager_email
        FROM employee e
        LEFT JOIN staff s ON s.employee_id = e.employee_id
        LEFT JOIN employee m_emp ON m_emp.employee_id = s.manager_id
        WHERE e.employee_id = %s
    """, (user_id,))
    
    user_data = cur.fetchone()
    conn.close()

    if not user_data:
        return redirect(url_for("logout"))

    user_data["role"] = session.get("role", "staff")
    success_msg = request.args.get("success")
    error_msg = request.args.get("error")

    return render_template(
        "profile.html", 
        active="profile",
        title="Profile",
        user=user_data,
        success=success_msg,
        error=error_msg
    )

@app.route("/profile/change-password", methods=["POST"])
def change_password():
    if not require_login():
        return redirect(url_for("login"))

    user_id = session["user_id"]
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not all([current_password, new_password, confirm_password]):
        return redirect(url_for("profile", error="All password fields are required."))

    if new_password != confirm_password:
        return redirect(url_for("profile", error="New passwords do not match."))

    if len(new_password) < 6:
        return redirect(url_for("profile", error="Password must be at least 6 characters."))

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT password_hash FROM employee WHERE employee_id = %s", (user_id,))
    user = cur.fetchone()

    if not user or not check_password_hash(user["password_hash"], current_password):
        conn.close()
        return redirect(url_for("profile", error="Current password is incorrect."))

    new_hash = generate_password_hash(new_password)
    cur.execute("UPDATE employee SET password_hash = %s WHERE employee_id = %s", (new_hash, user_id))
    conn.commit()
    conn.close()

    return redirect(url_for("profile", success="Password changed successfully!"))

@app.get("/dashboard")
def dashboard():
    if not require_login(): return redirect(url_for("login"))
    return render_template("dashboard.html", active="dashboard")

@app.get("/menu")
def menu_page():
    if not require_login():
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
          name,
          description,
          menu_price,
          is_available,
          category
        FROM menu_item
        ORDER BY category, name
    """)
    rows = cur.fetchall()
    conn.close()

    menu = {}
    for r in rows:
        menu.setdefault(r["category"], []).append(r)

    return render_template(
        "menu.html",
        active="menu",
        title="Menu",
        menu=menu
    )

def monday_of_current_week(d: date) -> date:
    return d - timedelta(days=d.weekday())

@app.get("/schedule")
def schedule_page():
    if not require_login():
        return redirect(url_for("login"))

    staff_id = session["user_id"]
    is_manager = session.get("role") == "manager"

    today = date.today()
    week_start = monday_of_current_week(today)
    week_end = week_start + timedelta(days=6)

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            s.schedule_id, 
            s.staff_id, 
            s.shift_date, 
            s.start_time, 
            s.end_time, 
            s.assigned_role
        FROM schedule s
        WHERE s.staff_id = %s
          AND s.shift_date BETWEEN %s AND %s
        ORDER BY s.shift_date, s.start_time
    """, (staff_id, week_start, week_end))
    shifts = cur.fetchall()

    cur.execute("""
        SELECT 
            request_id, 
            request_type, 
            request_date, 
            start_date, 
            end_date,
            start_time, 
            end_time, 
            extra_time, 
            reason, 
            status
        FROM staff_request
        WHERE staff_id = %s
        ORDER BY 
            CASE status 
                WHEN 'PENDING' THEN 1 
                WHEN 'APPROVED' THEN 2 
                ELSE 3 
            END,
            request_date DESC
        LIMIT 10
    """, (staff_id,))
    requests_rows = cur.fetchall()

    pending_count = 0
    if is_manager:
        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM staff_request r
            JOIN staff s ON r.staff_id = s.employee_id
            WHERE s.manager_id = %s AND r.status = 'PENDING'
        """, (staff_id,))
        result = cur.fetchone()
        pending_count = result["cnt"] if result else 0

    conn.close()

    week_days = [week_start + timedelta(days=i) for i in range(7)]

    shifts_by_day = {d.isoformat(): [] for d in week_days}
    for s in shifts:
        day_key = str(s["shift_date"])
        s["is_exchanged"] = False
        s["exchange_partner"] = None
        shifts_by_day[day_key].append(s)

    return render_template(
        "schedule.html",
        active="schedule",
        title="Schedule",
        week_start=week_start,
        week_end=week_end,
        week_days=week_days,
        shifts_by_day=shifts_by_day,
        requests_rows=requests_rows,
        pending_count=pending_count
    )

@app.post("/schedule/request-timeoff")
def request_timeoff():
    if not require_login():
        return redirect(url_for("login"))

    staff_id = session["user_id"]

    start_date = request.form.get("start_date")
    end_date   = request.form.get("end_date")
    reason     = (request.form.get("reason") or "").strip()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT manager_id FROM staff WHERE employee_id=%s", (staff_id,))
    row = cur.fetchone()
    manager_id = row[0] if row else None

    cur.execute("""
        INSERT INTO staff_request
          (staff_id, manager_id, request_type, request_date, start_date, end_date, reason, status)
        VALUES
          (%s, %s, 'TIME_OFF', CURDATE(), %s, %s, %s, 'PENDING')
    """, (staff_id, manager_id, start_date, end_date, reason))

    conn.commit()
    conn.close()
    flash("Time off request submitted.", "success")
    return redirect(url_for("schedule_page"))

@app.post("/schedule/request-overtime")
def request_overtime():
    if not require_login():
        return redirect(url_for("login"))

    staff_id = session["user_id"]
    shift_date = request.form.get("shift_date")
    start_time = request.form.get("start_time")
    end_time   = request.form.get("end_time")
    extra_time = request.form.get("extra_time", type=int)
    reason     = (request.form.get("reason") or "").strip()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT manager_id FROM staff WHERE employee_id=%s", (staff_id,))
    row = cur.fetchone()
    manager_id = row[0] if row else None

    cur.execute("""
        INSERT INTO staff_request
          (staff_id, manager_id, request_type, request_date, start_date, start_time, end_time, extra_time, reason, status)
        VALUES
          (%s, %s, 'OVERTIME', CURDATE(), %s, %s, %s, %s, %s, 'PENDING')
    """, (staff_id, manager_id, shift_date, start_time, end_time, extra_time, reason))

    conn.commit()
    conn.close()
    flash("Overtime request submitted.", "success")
    return redirect(url_for("schedule_page"))

@app.post("/schedule/request-availability")
def request_availability():
    if not require_login():
        return redirect(url_for("login"))

    staff_id = session["user_id"]
    day = request.form.get("day")
    start_time = request.form.get("start_time")
    end_time   = request.form.get("end_time")
    reason     = (request.form.get("reason") or "").strip()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT manager_id FROM staff WHERE employee_id=%s", (staff_id,))
    row = cur.fetchone()
    manager_id = row[0] if row else None

    cur.execute("""
        INSERT INTO staff_request
          (staff_id, manager_id, request_type, request_date, start_date, start_time, end_time, reason, status)
        VALUES
          (%s, %s, 'AVAILABILITY', CURDATE(), %s, %s, %s, %s, 'PENDING')
    """, (staff_id, manager_id, day, start_time, end_time, reason))

    conn.commit()
    conn.close()
    flash("Availability request submitted.", "success")
    return redirect(url_for("schedule_page"))

@app.get("/inventory")
def inventory_page():
    if not require_login():
        return redirect(url_for("login"))

    q = (request.args.get("q") or "").strip()

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total_items FROM inventory_item")
    total_items = cur.fetchone()["total_items"]

    cur.execute("""
        SELECT COUNT(*) AS low_stock_items
        FROM inventory_item ii
        JOIN ingredient ing ON ing.ingredient_id = ii.ingredient_id
        WHERE ii.current_quantity < ing.minimum_stock_threshold
    """)
    low_stock_items = cur.fetchone()["low_stock_items"]

    cur.execute("""
        SELECT COUNT(*) AS expiring_soon
        FROM inventory_item
        WHERE expiration_date IS NOT NULL
          AND DATEDIFF(expiration_date, CURDATE()) BETWEEN 0 AND 7
    """)
    expiring_soon = cur.fetchone()["expiring_soon"]

    cur.execute("""
        SELECT
          ii.inventory_item_id,
          ing.ingredient_id,
          ing.name AS ingredient_name,
          ing.unit,
          ing.minimum_stock_threshold,
          ii.current_quantity,
          ii.average_unit_cost,
          ii.expiration_date,
          ii.last_update_date,
          DATEDIFF(ii.expiration_date, CURDATE()) AS days_left
        FROM inventory_item ii
        JOIN ingredient ing ON ing.ingredient_id = ii.ingredient_id
        WHERE (%s = '' OR ing.name LIKE CONCAT('%%', %s, '%%'))
        ORDER BY ing.name
    """, (q, q))
    items = cur.fetchall()

    conn.close()

    for it in items:
        it["is_low_stock"] = it["current_quantity"] < it["minimum_stock_threshold"]
        it["is_expired"] = (it["days_left"] is not None and it["days_left"] < 0)
        it["is_expiring_soon"] = (it["days_left"] is not None and 0 <= it["days_left"] <= 7)

    return render_template(
        "inventory.html",
        active="inventory",
        title="Inventory Management",
        q=q,
        total_items=total_items,
        low_stock_items=low_stock_items,
        expiring_soon=expiring_soon,
        items=items
    )

@app.get("/waste")
def waste_page():
    if not require_login():
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT
          w.ingredient_id,
          ing.name AS ingredient_name,
          w.waste_seq,
          w.waste_date,
          w.amount_wasted,
          w.reason,
          i.average_unit_cost,
          (w.amount_wasted * i.average_unit_cost) AS waste_cost
        FROM waste_tracking w
        JOIN ingredient ing ON w.ingredient_id = ing.ingredient_id
        JOIN inventory_item i ON w.ingredient_id = i.ingredient_id
        ORDER BY w.waste_date DESC, ing.name ASC
    """)
    rows = cur.fetchall()

    cur.execute("SELECT COUNT(DISTINCT ingredient_id) AS distinct_ingredients_wasted FROM waste_tracking")
    total_waste_items = cur.fetchone()["distinct_ingredients_wasted"]

    cur.execute("""
        SELECT COALESCE(SUM(w.amount_wasted * i.average_unit_cost), 0) AS total_waste_cost
        FROM waste_tracking w
        JOIN inventory_item i ON w.ingredient_id = i.ingredient_id
    """)
    total_waste_cost = cur.fetchone()["total_waste_cost"]

    cur.execute("""
        SELECT reason, COUNT(*) AS occurrence
        FROM waste_tracking
        GROUP BY reason
        ORDER BY occurrence DESC
        LIMIT 1
    """)
    top_reason_row = cur.fetchone()
    most_common_reason = (top_reason_row["reason"] if top_reason_row else "—")

    conn.close()

    return render_template(
        "waste.html",
        active="waste",
        title="Waste Management",
        total_waste_items=total_waste_items,
        total_waste_cost=total_waste_cost,
        most_common_reason=most_common_reason,
        rows=rows
    )

@app.get("/tables")
def tables_page():
    if not require_login():
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total FROM restaurant_table")
    total_tables = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS c FROM restaurant_table WHERE status='OCCUPIED'")
    occupied_tables = cur.fetchone()["c"]

    cur.execute("""
        SELECT COUNT(*) AS active_orders
        FROM customer_order
        WHERE payment_status = 'UNPAID'
    """)
    active_orders = cur.fetchone()["active_orders"]

    cur.execute("""
        SELECT COALESCE(SUM(total_amount), 0) AS current_revenue
        FROM customer_order
        WHERE payment_status = 'UNPAID'
    """)
    current_revenue = cur.fetchone()["current_revenue"]

    cur.execute("""
        SELECT
            t.table_id,
            t.table_number,
            t.capacity,
            t.status,
            COUNT(DISTINCT co.order_id) AS parties,
            COALESCE(SUM(co.total_amount), 0) AS total_bill
        FROM restaurant_table t
        LEFT JOIN customer_order co ON co.table_id = t.table_id 
            AND co.payment_status = 'UNPAID'
        GROUP BY t.table_id, t.table_number, t.capacity, t.status
        ORDER BY t.table_number
    """)
    tables = cur.fetchall()
    conn.close()

    for t in tables:
        if int(t["parties"]) > 0 and t["status"] == "OCCUPIED":
            t["occupancy"] = t["capacity"]
        else:
            t["occupancy"] = 0
        t["parties"] = int(t["parties"] or 0)
        t["total_bill"] = float(t["total_bill"] or 0)

    return render_template(
        "tables.html",
        active="tables",
        title="Table Management",
        total_tables=total_tables,
        occupied_tables=occupied_tables,
        active_orders=active_orders,
        current_revenue=float(current_revenue),
        tables=tables
    )

@app.post("/tables/update-status")
def update_table_status():
    if not require_login():
        return redirect(url_for("login"))
    if session.get("role") != "manager":
        return redirect(url_for("dashboard"))

    table_id = request.form.get("table_id", type=int)
    new_status = (request.form.get("status") or "").upper()

    allowed = {"AVAILABLE", "OCCUPIED", "RESERVED", "CLOSED"}
    if new_status not in allowed:
        flash("Invalid table status.", "error")
        return redirect(url_for("tables_page"))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE restaurant_table
        SET status=%s
        WHERE table_id=%s
    """, (new_status, table_id))
    conn.commit()
    conn.close()

    flash("Table status updated.", "success")
    return redirect(url_for("tables_page"))

@app.get("/tables/<int:table_id>/details")
def table_details(table_id):
    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT table_id, table_number, capacity, status
        FROM restaurant_table
        WHERE table_id = %s
    """, (table_id,))
    table = cur.fetchone()

    if not table:
        conn.close()
        return jsonify({"error": "Table not found"}), 404

    cur.execute("""
        SELECT 
            o.order_id, 
            o.staff_id, 
            o.order_datetime, 
            o.total_amount,
            e.name, 
            e.surname
        FROM customer_order o
        JOIN employee e ON e.employee_id = o.staff_id
        WHERE o.table_id = %s
          AND o.payment_status = 'UNPAID'
        ORDER BY o.order_datetime DESC
        LIMIT 1
    """, (table_id,))
    order = cur.fetchone()

    items = []
    subtotal = 0.0

    if order:
        cur.execute("""
            SELECT
              oi.quantity,
              oi.unit_price,
              m.name
            FROM order_item oi
            JOIN menu_item m ON m.menu_item_id = oi.menu_item_id
            WHERE oi.order_id = %s
        """, (order["order_id"],))
        items = cur.fetchall()
        subtotal = sum(float(i["quantity"]) * float(i["unit_price"]) for i in items)

    conn.close()

    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + tax, 2)

    items_api = [
        {
            "qty": it["quantity"], 
            "name": it["name"], 
            "price_total": float(it["quantity"]) * float(it["unit_price"])
        }
        for it in items
    ]

    seated_at = "—"
    if order and order.get("order_datetime"):
        seated_at = str(order["order_datetime"])[11:16]

    return jsonify({
        "table_number": table["table_number"],
        "party": {
            "guests": table["capacity"] if order else 0,
            "seated_at": seated_at,
            "status": "Ordering" if order else "—",
            "server_name": f'{order["name"]} {order["surname"]}' if order else "—",
            "server_code": f'EMP{int(order["staff_id"]):03d}' if order else "—",
        },
        "items": items_api,
        "subtotal": float(subtotal),
        "tax": float(tax),
        "total": float(total),
    })

def require_manager():
    return session.get("role") == "manager"

@app.get("/staff-management")
def staff_management_page():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        return redirect(url_for("dashboard"))

    manager_id = session["user_id"]

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT
          s.employee_id AS staff_id,
          e.name AS first_name,
          e.surname AS last_name,
          e.email,
          e.phone_number,
          e.address,
          s.role,
          e.is_active
        FROM staff s
        JOIN employee e ON s.employee_id = e.employee_id
        WHERE s.manager_id = %s
        ORDER BY e.name, e.surname
    """, (manager_id,))
    staff_rows = cur.fetchall()

    cur.execute("""
        SELECT
          r.request_id,
          r.staff_id,
          e.name AS staff_name,
          e.surname AS staff_surname,
          r.request_type,
          r.request_date,
          r.start_date,
          r.end_date,
          r.start_time,
          r.end_time,
          r.extra_time,
          r.reason,
          r.status
        FROM staff_request r
        JOIN staff s ON r.staff_id = s.employee_id
        JOIN employee e ON s.employee_id = e.employee_id
        WHERE s.manager_id = %s
        ORDER BY r.request_date DESC, r.start_date ASC
    """, (manager_id,))
    req_rows = cur.fetchall()

    conn.close()

    return render_template(
        "staff_management.html",
        active="staff_management",
        title="Staff Management",
        staff_rows=staff_rows,
        req_rows=req_rows
    )

@app.post("/staff-management/request-status")
def update_staff_request_status():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        return redirect(url_for("dashboard"))

    manager_id = session["user_id"]
    request_id = request.form.get("request_id", type=int)
    new_status = (request.form.get("status") or "").upper()

    if new_status not in ("APPROVED", "REJECTED"):
        flash("Invalid status.", "error")
        return redirect(url_for("staff_management_page"))

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE staff_request
        SET status = %s
        WHERE request_id = %s
          AND staff_id IN (SELECT employee_id FROM staff WHERE manager_id = %s)
    """, (new_status, request_id, manager_id))

    conn.commit()
    conn.close()

    return redirect(url_for("staff_management_page"))

if __name__ == "__main__":
    app.run(debug=True)

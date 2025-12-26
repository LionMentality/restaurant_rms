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
          menu_item_id,
          name,
          description,
          menu_price,
          is_available,
          category
        FROM menu_item
        ORDER BY category, name
    """)
    rows = cur.fetchall()

    # Get all ingredients for the create modal
    cur.execute("SELECT ingredient_id, name, unit FROM ingredient ORDER BY name")
    ingredients = cur.fetchall()

    conn.close()

    menu = {}
    for r in rows:
        menu.setdefault(r["category"], []).append(r)

    return render_template(
        "menu.html",
        active="menu",
        title="Menu",
        menu=menu,
        ingredients=ingredients
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

    # Check if user is a staff member
    cur.execute("SELECT manager_id FROM staff WHERE employee_id=%s", (staff_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        flash("Only staff members can submit time off requests.", "error")
        return redirect(url_for("schedule_page"))

    manager_id = row[0]

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

    # Check if user is a staff member
    cur.execute("SELECT manager_id FROM staff WHERE employee_id=%s", (staff_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        flash("Only staff members can submit overtime requests.", "error")
        return redirect(url_for("schedule_page"))

    manager_id = row[0]

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

    # Check if user is a staff member
    cur.execute("SELECT manager_id FROM staff WHERE employee_id=%s", (staff_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        flash("Only staff members can submit availability requests.", "error")
        return redirect(url_for("schedule_page"))

    manager_id = row[0]

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

@app.post("/inventory/receive-shipment")
def receive_shipment():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("inventory_page"))

    ingredient_id = request.form.get("ingredient_id", type=int)
    quantity = request.form.get("quantity", type=float)
    unit_cost = request.form.get("unit_cost", type=float)
    expiration_date = request.form.get("expiration_date") or None

    if not all([ingredient_id, quantity, unit_cost]) or quantity <= 0 or unit_cost <= 0:
        flash("Invalid input. Please provide valid quantity and cost.", "error")
        return redirect(url_for("inventory_page"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Get current inventory
        cur.execute("""
            SELECT current_quantity, average_unit_cost
            FROM inventory_item
            WHERE ingredient_id = %s
        """, (ingredient_id,))
        inventory = cur.fetchone()

        if inventory:
            # Calculate weighted average cost
            current_qty = float(inventory["current_quantity"])
            current_cost = float(inventory["average_unit_cost"])
            new_avg_cost = ((current_qty * current_cost) + (quantity * unit_cost)) / (current_qty + quantity)

            # Update inventory
            cur.execute("""
                UPDATE inventory_item
                SET current_quantity = current_quantity + %s,
                    average_unit_cost = %s,
                    expiration_date = COALESCE(%s, expiration_date),
                    last_update_date = NOW()
                WHERE ingredient_id = %s
            """, (quantity, new_avg_cost, expiration_date, ingredient_id))
        else:
            # Create new inventory item
            cur.execute("""
                INSERT INTO inventory_item (ingredient_id, current_quantity, average_unit_cost, expiration_date, last_update_date)
                VALUES (%s, %s, %s, %s, NOW())
            """, (ingredient_id, quantity, unit_cost, expiration_date))

        # Log as adjustment in inventory_usage
        cur.execute("""
            INSERT INTO inventory_usage (ingredient_id, usage_date, quantity_used, usage_type, note)
            VALUES (%s, CURDATE(), %s, 'ADJUSTMENT', 'Shipment received')
        """, (ingredient_id, quantity))

        conn.commit()
        flash("Shipment received and inventory updated successfully!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error receiving shipment: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("inventory_page"))

@app.post("/inventory/adjust")
def adjust_inventory():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("inventory_page"))

    ingredient_id = request.form.get("ingredient_id", type=int)
    adjustment = request.form.get("adjustment", type=float)
    reason = request.form.get("reason", "").strip()

    if not all([ingredient_id, adjustment]) or adjustment == 0:
        flash("Invalid adjustment amount.", "error")
        return redirect(url_for("inventory_page"))

    try:
        conn = get_conn()
        cur = conn.cursor()

        # Update inventory
        cur.execute("""
            UPDATE inventory_item
            SET current_quantity = GREATEST(0, current_quantity + %s),
                last_update_date = NOW()
            WHERE ingredient_id = %s
        """, (adjustment, ingredient_id))

        if cur.rowcount == 0:
            flash("Ingredient not found in inventory.", "error")
            conn.close()
            return redirect(url_for("inventory_page"))

        # Log the adjustment
        usage_type = 'ADJUSTMENT' if adjustment > 0 else 'WASTE'
        note = f"Manual adjustment: {reason}" if reason else "Manual adjustment"
        cur.execute("""
            INSERT INTO inventory_usage (ingredient_id, usage_date, quantity_used, usage_type, note)
            VALUES (%s, CURDATE(), %s, %s, %s)
        """, (ingredient_id, abs(adjustment), usage_type, note))

        conn.commit()
        flash("Inventory adjusted successfully!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error adjusting inventory: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("inventory_page"))

@app.post("/inventory/update-threshold")
def update_threshold():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("inventory_page"))

    ingredient_id = request.form.get("ingredient_id", type=int)
    threshold = request.form.get("threshold", type=float)

    if not all([ingredient_id, threshold]) or threshold < 0:
        flash("Invalid threshold value.", "error")
        return redirect(url_for("inventory_page"))

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            UPDATE ingredient
            SET minimum_stock_threshold = %s
            WHERE ingredient_id = %s
        """, (threshold, ingredient_id))

        if cur.rowcount == 0:
            flash("Ingredient not found.", "error")
        else:
            flash("Minimum threshold updated successfully!", "success")

        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error updating threshold: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("inventory_page"))

@app.post("/inventory/delete/<int:ingredient_id>")
def delete_ingredient(ingredient_id):
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("inventory_page"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Get ingredient name for confirmation message
        cur.execute("SELECT name FROM ingredient WHERE ingredient_id = %s", (ingredient_id,))
        ingredient = cur.fetchone()

        if not ingredient:
            flash("Ingredient not found.", "error")
            conn.close()
            return redirect(url_for("inventory_page"))

        ingredient_name = ingredient["name"]

        # RESTRICT: Check if ingredient is used in any menu items
        cur.execute("""
            SELECT DISTINCT mi.menu_item_id, mi.name
            FROM menu_item mi
            JOIN menu_item_ingredient mii ON mi.menu_item_id = mii.menu_item_id
            WHERE mii.ingredient_id = %s
        """, (ingredient_id,))
        associated_menu_items = cur.fetchall()

        if associated_menu_items:
            # Ingredient is used in menu items - RESTRICT deletion
            menu_names = ", ".join([item["name"] for item in associated_menu_items])
            flash(f"Cannot delete ingredient '{ingredient_name}' because it is used in the following menu items: {menu_names}. Please remove it from these menu items first.", "error")
            conn.close()
            return redirect(url_for("inventory_page"))

        # Ingredient is not used in any menu items - safe to delete
        # Delete inventory alerts first (due to foreign key constraint)
        cur.execute("DELETE FROM inventory_alert WHERE ingredient_id = %s", (ingredient_id,))

        # Delete waste tracking records
        cur.execute("DELETE FROM waste_tracking WHERE ingredient_id = %s", (ingredient_id,))

        # Delete inventory usage records
        cur.execute("DELETE FROM inventory_usage WHERE ingredient_id = %s", (ingredient_id,))

        # Delete inventory item
        cur.execute("DELETE FROM inventory_item WHERE ingredient_id = %s", (ingredient_id,))

        # Finally delete the ingredient
        cur.execute("DELETE FROM ingredient WHERE ingredient_id = %s", (ingredient_id,))

        conn.commit()
        flash(f"Ingredient '{ingredient_name}' deleted successfully!", "success")

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error deleting ingredient: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("inventory_page"))

@app.get("/inventory/reports/weekly")
def inventory_weekly_report():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("dashboard"))

    # Get date range from query params or default to last 7 days
    end_date = request.args.get("end_date") or date.today().isoformat()
    start_date = request.args.get("start_date") or (date.today() - timedelta(days=7)).isoformat()

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Complex query with GROUP BY, date ranges, SUM aggregations
    cur.execute("""
        SELECT
            ing.ingredient_id,
            ing.name,
            ing.unit,
            iu.usage_type,
            SUM(iu.quantity_used) AS total_used,
            COUNT(*) AS usage_count,
            SUM(iu.quantity_used * ii.average_unit_cost) AS total_cost,
            AVG(ii.average_unit_cost) AS avg_cost
        FROM inventory_usage iu
        JOIN ingredient ing ON iu.ingredient_id = ing.ingredient_id
        JOIN inventory_item ii ON ing.ingredient_id = ii.ingredient_id
        WHERE iu.usage_date BETWEEN %s AND %s
        GROUP BY ing.ingredient_id, iu.usage_type
        ORDER BY total_cost DESC, ing.name
    """, (start_date, end_date))
    usage_data = cur.fetchall()

    # Summary statistics
    cur.execute("""
        SELECT
            iu.usage_type,
            COUNT(DISTINCT iu.ingredient_id) AS ingredient_count,
            SUM(iu.quantity_used * ii.average_unit_cost) AS type_total_cost
        FROM inventory_usage iu
        JOIN inventory_item ii ON iu.ingredient_id = ii.ingredient_id
        WHERE iu.usage_date BETWEEN %s AND %s
        GROUP BY iu.usage_type
    """, (start_date, end_date))
    summary = cur.fetchall()

    conn.close()

    return render_template(
        "inventory_report.html",
        active="inventory",
        title="Weekly Inventory Report",
        start_date=start_date,
        end_date=end_date,
        usage_data=usage_data,
        summary=summary
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

@app.post("/waste/record")
def record_waste():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("waste_page"))

    ingredient_id = request.form.get("ingredient_id", type=int)
    amount_wasted = request.form.get("amount_wasted", type=float)
    reason = request.form.get("reason", "").strip()

    if not all([ingredient_id, amount_wasted, reason]) or amount_wasted <= 0:
        flash("Please provide valid waste details.", "error")
        return redirect(url_for("waste_page"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Get next waste_seq for this ingredient
        cur.execute("""
            SELECT COALESCE(MAX(waste_seq), 0) + 1 AS next_seq
            FROM waste_tracking
            WHERE ingredient_id = %s
        """, (ingredient_id,))
        next_seq = cur.fetchone()["next_seq"]

        # Insert waste record
        cur.execute("""
            INSERT INTO waste_tracking (ingredient_id, waste_seq, waste_date, amount_wasted, reason)
            VALUES (%s, %s, CURDATE(), %s, %s)
        """, (ingredient_id, next_seq, amount_wasted, reason))

        # Log as usage
        cur.execute("""
            INSERT INTO inventory_usage (ingredient_id, usage_date, quantity_used, usage_type, note)
            VALUES (%s, CURDATE(), %s, 'WASTE', %s)
        """, (ingredient_id, amount_wasted, reason))

        # Update inventory quantity
        cur.execute("""
            UPDATE inventory_item
            SET current_quantity = GREATEST(0, current_quantity - %s),
                last_update_date = NOW()
            WHERE ingredient_id = %s
        """, (amount_wasted, ingredient_id))

        conn.commit()
        flash("Waste recorded successfully!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error recording waste: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("waste_page"))

@app.get("/waste/reports/weekly")
def waste_weekly_report():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("dashboard"))

    end_date = request.args.get("end_date") or date.today().isoformat()
    start_date = request.args.get("start_date") or (date.today() - timedelta(days=7)).isoformat()

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Complex query with GROUP BY, WEEK(), aggregations
    cur.execute("""
        SELECT
            ing.name,
            ing.unit,
            w.reason,
            SUM(w.amount_wasted) AS total_wasted,
            COUNT(*) AS incidents,
            SUM(w.amount_wasted * ii.average_unit_cost) AS total_cost,
            WEEK(w.waste_date) AS week_num
        FROM waste_tracking w
        JOIN ingredient ing ON w.ingredient_id = ing.ingredient_id
        JOIN inventory_item ii ON w.ingredient_id = ii.ingredient_id
        WHERE w.waste_date BETWEEN %s AND %s
        GROUP BY ing.ingredient_id, w.reason, WEEK(w.waste_date)
        ORDER BY total_cost DESC
    """, (start_date, end_date))
    waste_data = cur.fetchall()

    conn.close()

    return render_template(
        "waste_report.html",
        active="waste",
        title="Weekly Waste Report",
        start_date=start_date,
        end_date=end_date,
        waste_data=waste_data
    )

@app.post("/menu/create")
def create_menu_item():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("menu_page"))

    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    menu_price = request.form.get("menu_price", type=float)
    is_available = request.form.get("is_available", "1") == "1"

    # Get ingredient IDs and quantities (multiple)
    ingredient_ids = request.form.getlist("ingredient_ids[]")
    quantities = request.form.getlist("quantities[]")

    if not all([name, category, menu_price]) or menu_price <= 0:
        flash("Please provide valid menu item details.", "error")
        return redirect(url_for("menu_page"))

    try:
        conn = get_conn()
        cur = conn.cursor()

        # Insert menu item
        cur.execute("""
            INSERT INTO menu_item (name, category, menu_price, is_available, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, category, menu_price, is_available, description))

        menu_item_id = cur.lastrowid

        # Insert recipe ingredients
        for ing_id, qty in zip(ingredient_ids, quantities):
            if ing_id and qty:
                cur.execute("""
                    INSERT INTO menu_item_ingredient (menu_item_id, ingredient_id, quantity_required)
                    VALUES (%s, %s, %s)
                """, (menu_item_id, int(ing_id), float(qty)))

        conn.commit()
        flash("Menu item created successfully!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error creating menu item: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("menu_page"))

@app.post("/menu/edit/<int:menu_item_id>")
def edit_menu_item(menu_item_id):
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("menu_page"))

    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    menu_price = request.form.get("menu_price", type=float)
    is_available = request.form.get("is_available", "1") == "1"

    if not all([name, category, menu_price]) or menu_price <= 0:
        flash("Please provide valid menu item details.", "error")
        return redirect(url_for("menu_page"))

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            UPDATE menu_item
            SET name = %s, category = %s, menu_price = %s, is_available = %s, description = %s
            WHERE menu_item_id = %s
        """, (name, category, menu_price, is_available, description, menu_item_id))

        conn.commit()
        flash("Menu item updated successfully!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error updating menu item: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("menu_page"))

@app.post("/menu/toggle-availability/<int:menu_item_id>")
def toggle_menu_availability(menu_item_id):
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        return jsonify({"error": "unauthorized"}), 403

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            UPDATE menu_item
            SET is_available = NOT is_available
            WHERE menu_item_id = %s
        """, (menu_item_id,))

        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.get("/menu/item/<int:menu_item_id>/cost-analysis")
def menu_cost_analysis(menu_item_id):
    if not require_login():
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Complex nested query with multiple JOINs
    cur.execute("""
        SELECT
            mi.menu_item_id,
            mi.name,
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
        WHERE mi.menu_item_id = %s
        GROUP BY mi.menu_item_id
    """, (menu_item_id,))
    item = cur.fetchone()

    # Get ingredient breakdown
    cur.execute("""
        SELECT
            ing.name AS ingredient_name,
            mii.quantity_required,
            ing.unit,
            ii.average_unit_cost,
            (mii.quantity_required * ii.average_unit_cost) AS ingredient_total_cost
        FROM menu_item_ingredient mii
        JOIN ingredient ing ON mii.ingredient_id = ing.ingredient_id
        JOIN inventory_item ii ON ing.ingredient_id = ii.ingredient_id
        WHERE mii.menu_item_id = %s
        ORDER BY ingredient_total_cost DESC
    """, (menu_item_id,))
    ingredients = cur.fetchall()

    conn.close()

    return render_template(
        "menu_cost_analysis.html",
        active="menu",
        title="Cost Analysis",
        item=item,
        ingredients=ingredients
    )

@app.post("/orders/create")
def create_order():
    if not require_login():
        return redirect(url_for("login"))

    table_id = request.form.get("table_id", type=int)
    special_requests = request.form.get("special_requests", "").strip()
    selected_items = request.form.getlist("menu_items")

    if not table_id:
        flash("Invalid table selection.", "error")
        return redirect(url_for("tables_page"))

    if not selected_items:
        flash("Please select at least one menu item.", "error")
        return redirect(url_for("tables_page"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Determine staff_id: check if current user is a staff member
        user_id = session["user_id"]
        cur.execute("SELECT employee_id FROM staff WHERE employee_id = %s", (user_id,))
        staff_member = cur.fetchone()

        if staff_member:
            # Current user is staff, use their ID
            staff_id = user_id
        else:
            # Current user is a manager, get any available staff member
            cur.execute("SELECT employee_id FROM staff WHERE employee_id IN (SELECT employee_id FROM employee WHERE is_active = TRUE) LIMIT 1")
            available_staff = cur.fetchone()

            if not available_staff:
                flash("No staff members available to assign order.", "error")
                conn.close()
                return redirect(url_for("tables_page"))

            staff_id = available_staff["employee_id"]

        # Create order
        cur.execute("""
            INSERT INTO customer_order (table_id, staff_id, order_datetime, payment_status, special_requests)
            VALUES (%s, %s, NOW(), 'UNPAID', %s)
        """, (table_id, staff_id, special_requests))

        order_id = cur.lastrowid

        # Add selected menu items to the order
        for menu_item_id in selected_items:
            quantity_key = f"quantity_{menu_item_id}"
            quantity = request.form.get(quantity_key, type=int)

            if not quantity or quantity <= 0:
                quantity = 1

            # Get menu item price
            cur.execute("""
                SELECT menu_price, is_available
                FROM menu_item
                WHERE menu_item_id = %s
            """, (menu_item_id,))
            menu_item = cur.fetchone()

            if menu_item and menu_item["is_available"]:
                unit_price = menu_item["menu_price"]

                # Insert order item (triggers will handle total and inventory)
                cur.execute("""
                    INSERT INTO order_item (order_id, menu_item_id, quantity, unit_price, item_status)
                    VALUES (%s, %s, %s, %s, 'ORDERED')
                """, (order_id, menu_item_id, quantity, unit_price))

        # Update table status to OCCUPIED
        cur.execute("""
            UPDATE restaurant_table
            SET status = 'OCCUPIED'
            WHERE table_id = %s
        """, (table_id,))

        conn.commit()
        flash("Order created successfully with items!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error creating order: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("tables_page"))

@app.post("/orders/<int:order_id>/add-item")
def add_order_item(order_id):
    if not require_login():
        return redirect(url_for("login"))

    menu_item_id = request.form.get("menu_item_id", type=int)
    quantity = request.form.get("quantity", type=int)

    if not all([menu_item_id, quantity]) or quantity <= 0:
        flash("Invalid item or quantity.", "error")
        return redirect(url_for("tables_page"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Get menu item price
        cur.execute("""
            SELECT menu_price, is_available
            FROM menu_item
            WHERE menu_item_id = %s
        """, (menu_item_id,))
        menu_item = cur.fetchone()

        if not menu_item or not menu_item["is_available"]:
            flash("Menu item not available.", "error")
            conn.close()
            return redirect(url_for("tables_page"))

        unit_price = menu_item["menu_price"]

        # Insert order item (triggers will handle total and inventory)
        cur.execute("""
            INSERT INTO order_item (order_id, menu_item_id, quantity, unit_price, item_status)
            VALUES (%s, %s, %s, %s, 'ORDERED')
        """, (order_id, menu_item_id, quantity, unit_price))

        conn.commit()
        flash("Item added to order!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error adding item: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("tables_page"))

@app.post("/orders/<int:order_id>/complete")
def complete_order(order_id):
    if not require_login():
        return redirect(url_for("login"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Get order details
        cur.execute("""
            SELECT table_id, total_amount
            FROM customer_order
            WHERE order_id = %s
        """, (order_id,))
        order = cur.fetchone()

        if not order:
            flash("Order not found.", "error")
            conn.close()
            return redirect(url_for("tables_page"))

        # Update order status
        cur.execute("""
            UPDATE customer_order
            SET payment_status = 'PAID'
            WHERE order_id = %s
        """, (order_id,))

        # Create sale record
        cur.execute("""
            INSERT INTO sale (order_id, sale_date, sale_amount)
            VALUES (%s, CURDATE(), %s)
        """, (order_id, order["total_amount"]))

        # Update table to AVAILABLE
        cur.execute("""
            UPDATE restaurant_table
            SET status = 'AVAILABLE'
            WHERE table_id = %s
        """, (order["table_id"],))

        conn.commit()
        flash("Order completed and payment processed!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error completing order: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("tables_page"))

@app.get("/orders/search")
def search_orders():
    if not require_login():
        return redirect(url_for("login"))

    # Get search filters
    start_date = request.args.get("start_date") or (date.today() - timedelta(days=30)).isoformat()
    end_date = request.args.get("end_date") or date.today().isoformat()
    staff_name = request.args.get("staff_name", "").strip()
    payment_status = request.args.get("payment_status", "").strip()
    table_number = request.args.get("table_number", "").strip()

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Complex search query with LIKE, date ranges, multiple filters
    query = """
        SELECT
            co.order_id,
            co.order_datetime,
            co.total_amount,
            co.payment_status,
            co.special_requests,
            rt.table_number,
            CONCAT(e.name, ' ', e.surname) AS staff_name
        FROM customer_order co
        JOIN restaurant_table rt ON co.table_id = rt.table_id
        JOIN employee e ON co.staff_id = e.employee_id
        WHERE DATE(co.order_datetime) BETWEEN %s AND %s
    """
    params = [start_date, end_date]

    if staff_name:
        query += " AND (e.name LIKE %s OR e.surname LIKE %s)"
        params.extend([f"%{staff_name}%", f"%{staff_name}%"])

    if payment_status:
        query += " AND co.payment_status = %s"
        params.append(payment_status)

    if table_number:
        query += " AND rt.table_number LIKE %s"
        params.append(f"%{table_number}%")

    query += " ORDER BY co.order_datetime DESC"

    cur.execute(query, params)
    orders = cur.fetchall()

    conn.close()

    return render_template(
        "order_search.html",
        active="tables",
        title="Search Orders",
        start_date=start_date,
        end_date=end_date,
        staff_name=staff_name,
        payment_status=payment_status,
        table_number=table_number,
        orders=orders
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

    # Get available menu items for the new order modal
    cur.execute("""
        SELECT menu_item_id, name, category, menu_price, is_available
        FROM menu_item
        WHERE is_available = TRUE
        ORDER BY category, name
    """)
    menu_items = cur.fetchall()

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
        tables=tables,
        menu_items=menu_items
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

@app.post("/staff-management/delete/<int:employee_id>")
def delete_staff_member(employee_id):
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("staff_management_page"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Get employee details
        cur.execute("""
            SELECT e.name, e.surname, e.employee_id
            FROM employee e
            JOIN staff s ON e.employee_id = s.employee_id
            WHERE e.employee_id = %s AND s.manager_id = %s
        """, (employee_id, session["user_id"]))
        employee = cur.fetchone()

        if not employee:
            flash("Employee not found or you don't have permission to delete them.", "error")
            conn.close()
            return redirect(url_for("staff_management_page"))

        employee_name = f"{employee['name']} {employee['surname']}"

        # RESTRICT: Check for dependencies
        dependencies = []

        # Check for orders
        cur.execute("SELECT COUNT(*) as count FROM customer_order WHERE staff_id = %s", (employee_id,))
        order_count = cur.fetchone()["count"]
        if order_count > 0:
            dependencies.append(f"{order_count} order(s)")

        # Check for schedules
        cur.execute("SELECT COUNT(*) as count FROM schedule WHERE staff_id = %s", (employee_id,))
        schedule_count = cur.fetchone()["count"]
        if schedule_count > 0:
            dependencies.append(f"{schedule_count} schedule(s)")

        # Check for payroll records
        cur.execute("SELECT COUNT(*) as count FROM payroll WHERE employee_id = %s", (employee_id,))
        payroll_count = cur.fetchone()["count"]
        if payroll_count > 0:
            dependencies.append(f"{payroll_count} payroll record(s)")

        if dependencies:
            # Has dependencies - RESTRICT deletion
            dep_str = ", ".join(dependencies)
            flash(f"Cannot delete {employee_name} because they have associated records: {dep_str}. Please deactivate the employee instead.", "error")
            conn.close()
            return redirect(url_for("staff_management_page"))

        # No dependencies - safe to delete
        # Delete staff requests
        cur.execute("DELETE FROM staff_request WHERE staff_id = %s", (employee_id,))

        # Delete from staff table
        cur.execute("DELETE FROM staff WHERE employee_id = %s", (employee_id,))

        # Delete from employee table
        cur.execute("DELETE FROM employee WHERE employee_id = %s", (employee_id,))

        conn.commit()
        flash(f"Staff member {employee_name} deleted successfully!", "success")

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error deleting staff member: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("staff_management_page"))

@app.post("/schedule/create")
def create_schedule():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("schedule_page"))

    staff_id = request.form.get("staff_id", type=int)
    shift_date = request.form.get("shift_date")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    assigned_role = request.form.get("assigned_role", "").strip()

    if not all([staff_id, shift_date, start_time, end_time]):
        flash("Please provide all schedule details.", "error")
        return redirect(url_for("schedule_manager_page"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Check for conflicts
        cur.execute("""
            SELECT schedule_id
            FROM schedule
            WHERE staff_id = %s
                AND shift_date = %s
                AND (
                    (start_time BETWEEN %s AND %s) OR
                    (end_time BETWEEN %s AND %s) OR
                    (%s BETWEEN start_time AND end_time)
                )
        """, (staff_id, shift_date, start_time, end_time, start_time, end_time, start_time))

        if cur.fetchone():
            flash("Schedule conflict detected for this staff member.", "error")
            conn.close()
            return redirect(url_for("schedule_manager_page"))

        # Insert schedule
        cur.execute("""
            INSERT INTO schedule (staff_id, shift_date, start_time, end_time, assigned_role)
            VALUES (%s, %s, %s, %s, %s)
        """, (staff_id, shift_date, start_time, end_time, assigned_role))

        conn.commit()
        flash("Schedule created successfully!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error creating schedule: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("schedule_manager_page"))

@app.post("/schedule/edit/<int:schedule_id>")
def edit_schedule(schedule_id):
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("schedule_page"))

    shift_date = request.form.get("shift_date")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    assigned_role = request.form.get("assigned_role", "").strip()

    if not all([shift_date, start_time, end_time]):
        flash("Please provide all schedule details.", "error")
        return redirect(url_for("schedule_manager_page"))

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            UPDATE schedule
            SET shift_date = %s, start_time = %s, end_time = %s, assigned_role = %s
            WHERE schedule_id = %s
        """, (shift_date, start_time, end_time, assigned_role, schedule_id))

        conn.commit()
        flash("Schedule updated successfully!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error updating schedule: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("schedule_manager_page"))

@app.post("/schedule/delete/<int:schedule_id>")
def delete_schedule(schedule_id):
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        return jsonify({"error": "unauthorized"}), 403

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("DELETE FROM schedule WHERE schedule_id = %s", (schedule_id,))
        conn.commit()

        return jsonify({"success": True})
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.get("/schedule/manager")
def schedule_manager_page():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("dashboard"))

    manager_id = session["user_id"]

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Get all staff for this manager
    cur.execute("""
        SELECT s.employee_id, e.name, e.surname, s.role
        FROM staff s
        JOIN employee e ON s.employee_id = e.employee_id
        WHERE s.manager_id = %s
        ORDER BY e.name, e.surname
    """, (manager_id,))
    staff_list = cur.fetchall()

    # Get approved availability requests
    cur.execute("""
        SELECT
            e.name,
            e.surname,
            sr.staff_id,
            sr.start_date,
            sr.start_time,
            sr.end_time,
            sr.request_type
        FROM staff_request sr
        JOIN employee e ON sr.staff_id = e.employee_id
        JOIN staff s ON sr.staff_id = s.employee_id
        WHERE s.manager_id = %s
            AND sr.status = 'APPROVED'
            AND sr.request_type IN ('AVAILABILITY', 'TIME_OFF')
            AND sr.start_date >= CURDATE()
        ORDER BY sr.start_date
    """, (manager_id,))
    availability = cur.fetchall()

    # Get upcoming schedules
    cur.execute("""
        SELECT
            sch.schedule_id,
            sch.staff_id,
            sch.shift_date,
            sch.start_time,
            sch.end_time,
            sch.assigned_role,
            e.name,
            e.surname
        FROM schedule sch
        JOIN employee e ON sch.staff_id = e.employee_id
        JOIN staff s ON sch.staff_id = s.employee_id
        WHERE s.manager_id = %s
            AND sch.shift_date >= CURDATE()
        ORDER BY sch.shift_date, sch.start_time
    """, (manager_id,))
    schedules = cur.fetchall()

    conn.close()

    return render_template(
        "schedule_manager.html",
        active="schedule",
        title="Schedule Management",
        staff_list=staff_list,
        availability=availability,
        schedules=schedules
    )

@app.post("/payroll/calculate")
def calculate_payroll():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("dashboard"))

    period_start = request.form.get("period_start")
    period_end = request.form.get("period_end")

    if not all([period_start, period_end]):
        flash("Please provide period dates.", "error")
        return redirect(url_for("payroll_page"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Calculate hours per employee
        cur.execute("""
            SELECT
                s.employee_id,
                e.salary,
                SUM(TIMESTAMPDIFF(HOUR, sch.start_time, sch.end_time)) AS total_hours,
                SUM(CASE
                    WHEN TIMESTAMPDIFF(HOUR, sch.start_time, sch.end_time) > 8
                    THEN TIMESTAMPDIFF(HOUR, sch.start_time, sch.end_time) - 8
                    ELSE 0
                END) AS overtime_hours
            FROM schedule sch
            JOIN staff s ON sch.staff_id = s.employee_id
            JOIN employee e ON s.employee_id = e.employee_id
            WHERE sch.shift_date BETWEEN %s AND %s
            GROUP BY s.employee_id
        """, (period_start, period_end))

        employees = cur.fetchall()

        # Calculate gross pay and insert payroll records
        for emp in employees:
            salary = float(emp["salary"] or 0)
            total_hours = float(emp["total_hours"] or 0)
            overtime_hours = float(emp["overtime_hours"] or 0)

            # Hourly rate (assuming salary is annual)
            hourly_rate = salary / 2080 if salary > 0 else 15  # 2080 = 40 hours * 52 weeks
            gross_pay = (total_hours * hourly_rate) + (overtime_hours * hourly_rate * 1.5)

            cur.execute("""
                INSERT INTO payroll (employee_id, pay_period_start, pay_period_end, hours_worked, overtime_hours, gross_pay, payment_date)
                VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
            """, (emp["employee_id"], period_start, period_end, total_hours, overtime_hours, gross_pay))

        # Create labor cost record
        cur.execute("""
            SELECT
                SUM(hours_worked) AS total_hours,
                SUM(gross_pay) AS total_wages
            FROM payroll
            WHERE pay_period_start = %s AND pay_period_end = %s
        """, (period_start, period_end))
        labor = cur.fetchone()

        cur.execute("""
            INSERT INTO labor_cost (period_start, period_end, total_hours, total_wages)
            VALUES (%s, %s, %s, %s)
        """, (period_start, period_end, labor["total_hours"], labor["total_wages"]))

        labor_cost_id = cur.lastrowid

        # Link payroll to labor cost
        cur.execute("""
            SELECT payroll_id
            FROM payroll
            WHERE pay_period_start = %s AND pay_period_end = %s
        """, (period_start, period_end))
        payroll_ids = cur.fetchall()

        for pr in payroll_ids:
            cur.execute("""
                INSERT INTO payroll_labor_cost (payroll_id, labor_cost_id)
                VALUES (%s, %s)
            """, (pr["payroll_id"], labor_cost_id))

        conn.commit()
        flash("Payroll calculated successfully!", "success")
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error calculating payroll: {str(e)}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("payroll_page"))

@app.get("/payroll")
def payroll_page():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("dashboard"))

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Get recent payroll records
    cur.execute("""
        SELECT
            p.payroll_id,
            e.name,
            e.surname,
            p.pay_period_start,
            p.pay_period_end,
            p.hours_worked,
            p.overtime_hours,
            p.gross_pay,
            p.payment_date
        FROM payroll p
        JOIN employee e ON p.employee_id = e.employee_id
        ORDER BY p.pay_period_end DESC, e.name
        LIMIT 50
    """)
    payrolls = cur.fetchall()

    conn.close()

    return render_template(
        "payroll.html",
        active="payroll",
        title="Payroll Management",
        payrolls=payrolls
    )

@app.get("/payroll/labor-cost-analysis")
def labor_cost_analysis():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("dashboard"))

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Complex nested query with multiple aggregations
    cur.execute("""
        SELECT
            lc.labor_cost_id,
            lc.period_start,
            lc.period_end,
            lc.total_hours,
            lc.total_wages,
            (SELECT SUM(total_amount)
             FROM customer_order co
             JOIN sale s ON co.order_id = s.order_id
             WHERE s.sale_date BETWEEN lc.period_start AND lc.period_end) AS period_revenue,
            (lc.total_wages / NULLIF((SELECT SUM(total_amount)
                                      FROM customer_order co
                                      JOIN sale s ON co.order_id = s.order_id
                                      WHERE s.sale_date BETWEEN lc.period_start AND lc.period_end), 0) * 100) AS labor_cost_percentage
        FROM labor_cost lc
        ORDER BY lc.period_end DESC
        LIMIT 20
    """)
    analysis = cur.fetchall()

    conn.close()

    return render_template(
        "labor_cost_analysis.html",
        active="payroll",
        title="Labor Cost Analysis",
        analysis=analysis
    )

@app.get("/reports/dashboard")
def reports_dashboard():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("dashboard"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Use views for quick metrics
        cur.execute("SELECT * FROM view_low_stock_items ORDER BY shortage DESC LIMIT 10")
        low_stock = cur.fetchall()

        cur.execute("SELECT * FROM view_menu_profitability ORDER BY profit_margin DESC")
        menu_profit = cur.fetchall()

        cur.execute("SELECT * FROM view_staff_performance ORDER BY total_sales DESC LIMIT 10")
        staff_perf = cur.fetchall()

        conn.close()

        return render_template(
            "reports_dashboard.html",
            active="reports",
            title="Reports Dashboard",
            low_stock=low_stock,
            menu_profit=menu_profit,
            staff_perf=staff_perf
        )
    except Exception as e:
        if conn:
            conn.close()
        flash(f"Error loading reports: {str(e)}. Please ensure database views are created by running schema.sql", "error")
        return redirect(url_for("dashboard"))

@app.get("/reports/menu-performance")
def menu_performance_report():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("dashboard"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM view_menu_profitability ORDER BY profit_margin DESC")
        items = cur.fetchall()

        conn.close()

        return render_template(
            "menu_performance.html",
            active="reports",
            title="Menu Performance Report",
            items=items
        )
    except Exception as e:
        if conn:
            conn.close()
        flash(f"Error loading menu performance report: {str(e)}. Please ensure database views are created.", "error")
        return redirect(url_for("dashboard"))

@app.get("/reports/staff-performance")
def staff_performance_report():
    if not require_login():
        return redirect(url_for("login"))
    if not require_manager():
        flash("Access denied. Manager privileges required.", "error")
        return redirect(url_for("dashboard"))

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM view_staff_performance ORDER BY total_sales DESC")
        staff = cur.fetchall()

        conn.close()

        return render_template(
            "staff_performance.html",
            active="reports",
            title="Staff Performance Report",
            staff=staff
        )
    except Exception as e:
        if conn:
            conn.close()
        flash(f"Error loading staff performance report: {str(e)}. Please ensure database views are created.", "error")
        return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Restaurant Management System (RMS) - A Flask-based web application for managing restaurant operations including staff scheduling, inventory, orders, tables, and waste tracking. Built for CS 353 Database Systems course at Bilkent University.

**Tech Stack:** Python 3.8+, Flask 3.1+, MySQL 8.0+, Jinja2 templates

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Database Operations
```bash
# Initialize/reset database (requires MySQL running)
sudo mysql < schema.sql
sudo mysql < insert.sql

# Or manually create database
sudo mysql
CREATE USER 'rms_user'@'localhost' IDENTIFIED BY 'rms_password';
GRANT ALL PRIVILEGES ON rms.* TO 'rms_user'@'localhost';
FLUSH PRIVILEGES;
```

### Running the Application
```bash
# Development server (default: http://127.0.0.1:5000)
python app.py

# The app runs in debug mode when executed directly
```

### Environment Configuration
Create a `.env` file in the project root:
```env
DB_HOST=127.0.0.1
DB_USER=rms_user
DB_PASSWORD=rms_password
DB_NAME=rms
```

## Architecture

### Application Structure
- **app.py** - Main Flask application with all routes and business logic (single-file architecture)
- **db.py** - Database connection factory using mysql-connector-python
- **templates/** - Jinja2 HTML templates (base.html + feature-specific pages)
- **static/css/** - Stylesheet resources
- **static/js/** - Client-side JavaScript
- **schema.sql** - Database schema with tables, constraints, and triggers
- **insert.sql** - Sample data initialization

### Database Architecture

**Key Relationships:**
- **Employee hierarchy:** `employee` → `manager` (1:1) or `staff` (1:1)
- Staff members have a `manager_id` foreign key (every staff reports to one manager)
- **Orders flow:** `restaurant_table` → `customer_order` (placed by `staff`) → `order_item` (references `menu_item`)
- **Inventory chain:** `ingredient` → `inventory_item` (tracks quantities) → `menu_item_ingredient` (recipe requirements)
- **Request system:** `staff` creates `staff_request` approved by their `manager`

**Important Triggers:**
- `trg_update_order_total_after_insert` - Auto-calculates order totals when items added
- `trg_log_inventory_usage_after_insert` - Records ingredient usage on order placement
- `trg_low_stock_after_insert/update` - Creates alerts when inventory drops below threshold

### Authentication & Sessions
- Password hashing: `werkzeug.security` (scrypt algorithm)
- Session-based auth storing: `user_id`, `full_name`, `username`, `role` (manager/staff)
- Role checking: `require_manager()` for manager-only routes
- All routes except `/login` and `/register` require authentication

### Key Application Flows

**Staff Request Workflow:**
1. Staff submits request (TIME_OFF, AVAILABILITY, or OVERTIME) via schedule page
2. Request stored with status='PENDING' and assigned to their manager
3. Manager views requests on staff management page
4. Manager approves/rejects, updating status

**Order & Inventory Flow:**
1. Order created for a table by staff member
2. Order items added → trigger updates order total
3. Trigger automatically logs ingredient usage from menu_item_ingredient mappings
4. Inventory quantities decreased; alerts created if below minimum threshold

**Table Status Management:**
- States: AVAILABLE, OCCUPIED, RESERVED, CLOSED
- Manager can update status via `/tables/update-status`
- Status determines visibility and operations in table view

## Code Patterns & Conventions

### Database Queries
- Always use parameterized queries with `%s` placeholders (never string formatting)
- Use `dictionary=True` cursor for named column access in routes
- Explicitly close connections: `conn.close()` after operations
- Commit required for INSERT/UPDATE/DELETE: `conn.commit()`

### Route Structure Pattern
```python
@app.route("/endpoint", methods=["GET", "POST"])
def handler():
    if not require_login():
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    # ... query logic ...
    conn.close()

    return render_template("page.html", active="nav_item", title="Page Title", **data)
```

### Template Rendering
- All templates extend `base.html`
- Pass `active="page_name"` to highlight navigation
- Pass `title="Page Title"` for page header
- Flash messages: `flash("message", "success"|"error")` → displayed in base template

### Manager-Only Routes
Protect with:
```python
if not require_manager():
    return redirect(url_for("dashboard"))
```

## Testing Accounts

Password for all accounts: `password123`

- **Manager:** `jmanager` (employee_id: 1)
- **Staff:** `ewilliams` (employee_id: 3, Server role)

Additional accounts available in insert.sql (sanderson, mchen, dmartinez, landerson, rthompson, agarcia, kbrown)

## Database Schema Notes

### Composite Primary Keys
- `waste_tracking`: (ingredient_id, waste_seq)
- `customer_review`: (order_id, review_seq)
- Many-to-many junction tables use composite PKs

### Constraint Patterns
- `CHECK` constraints enforce enum-like values (e.g., status fields)
- `ON DELETE CASCADE` used for dependent data (order_item → customer_order)
- `ON DELETE RESTRICT` protects critical references (menu_item_id in orders)
- `ON DELETE SET NULL` for optional managers in requests

### Naming Conventions
- Tables: snake_case (e.g., `menu_item`, `restaurant_table`)
- Foreign keys: `fk_[table]_[referenced_table]` (e.g., `fk_order_staff`)
- Triggers: `trg_[action]_[timing]_[event]` (e.g., `trg_update_order_total_after_insert`)

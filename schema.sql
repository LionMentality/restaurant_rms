

DROP DATABASE IF EXISTS rms;
CREATE DATABASE rms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE rms;

-- ---------- EMPLOYEES / ROLES ----------

CREATE TABLE employee (
  employee_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  surname VARCHAR(100) NOT NULL,
  phone_number VARCHAR(20),
  email VARCHAR(150) UNIQUE,
  address VARCHAR(255) NOT NULL,
  salary DECIMAL(10,2) NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE manager (
  employee_id INT PRIMARY KEY,
  CONSTRAINT fk_manager_employee
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE staff (
  employee_id INT PRIMARY KEY,
  role VARCHAR(50),
  manager_id INT NOT NULL,
  CONSTRAINT fk_staff_employee
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_staff_manager
    FOREIGN KEY (manager_id) REFERENCES manager(employee_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE manages (
  manager_id INT NOT NULL,
  staff_id INT NOT NULL,
  PRIMARY KEY (manager_id, staff_id),
  FOREIGN KEY (manager_id) REFERENCES manager(employee_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (staff_id) REFERENCES staff(employee_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------- SCHEDULING / REQUESTS ----------

CREATE TABLE schedule (
  schedule_id INT AUTO_INCREMENT PRIMARY KEY,
  staff_id INT NOT NULL,
  shift_date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  assigned_role VARCHAR(50),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_schedule_staff
    FOREIGN KEY (staff_id) REFERENCES staff(employee_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_shift_time CHECK (end_time > start_time)
) ENGINE=InnoDB;

CREATE TABLE staff_request (
  request_id INT AUTO_INCREMENT PRIMARY KEY,
  staff_id INT NOT NULL,
  manager_id INT,
  request_type VARCHAR(20) NOT NULL,
  request_date DATE NOT NULL,
  start_date DATE,
  end_date DATE,
  start_time TIME,
  end_time TIME,
  extra_time INT,
  reason TEXT,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  CONSTRAINT fk_req_staff
    FOREIGN KEY (staff_id) REFERENCES staff(employee_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_req_manager
    FOREIGN KEY (manager_id) REFERENCES manager(employee_id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_request_type CHECK (request_type IN ('TIME_OFF','AVAILABILITY','OVERTIME')),
  CONSTRAINT chk_request_status CHECK (status IN ('PENDING','APPROVED','REJECTED'))
) ENGINE=InnoDB;

-- ---------- PAYROLL / COSTS ----------

CREATE TABLE payroll (
  payroll_id INT AUTO_INCREMENT PRIMARY KEY,
  employee_id INT NOT NULL,
  pay_period_start DATE NOT NULL,
  pay_period_end DATE NOT NULL,
  hours_worked NUMERIC(6,2) NOT NULL,
  overtime_hours NUMERIC(6,2) NOT NULL DEFAULT 0,
  gross_pay DECIMAL(10,2) NOT NULL,
  payment_date DATE NOT NULL,
  CONSTRAINT fk_payroll_employee
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE labor_cost (
  labor_cost_id INT AUTO_INCREMENT PRIMARY KEY,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  total_hours NUMERIC(10,2) NOT NULL,
  total_wages DECIMAL(12,2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE payroll_labor_cost (
  payroll_id INT NOT NULL,
  labor_cost_id INT NOT NULL,
  PRIMARY KEY (payroll_id, labor_cost_id),
  CONSTRAINT fk_plc_payroll
    FOREIGN KEY (payroll_id) REFERENCES payroll(payroll_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_plc_labor_cost
    FOREIGN KEY (labor_cost_id) REFERENCES labor_cost(labor_cost_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------- INGREDIENTS / INVENTORY ----------

CREATE TABLE ingredient (
  ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  unit VARCHAR(20) NOT NULL,
  minimum_stock_threshold NUMERIC(10,2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE inventory_item (
  inventory_item_id INT AUTO_INCREMENT PRIMARY KEY,
  ingredient_id INT NOT NULL,
  current_quantity NUMERIC(10,2) NOT NULL,
  average_unit_cost DECIMAL(10,2) NOT NULL,
  expiration_date DATE,
  last_update_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_inv_ingredient
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE inventory_usage (
  usage_id INT AUTO_INCREMENT PRIMARY KEY,
  ingredient_id INT NOT NULL,
  usage_date DATE NOT NULL,
  quantity_used NUMERIC(10,2) NOT NULL,
  usage_type VARCHAR(20) NOT NULL,
  note TEXT,
  CONSTRAINT fk_usage_ingredient
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_usage_type CHECK (usage_type IN ('SALE','WASTE','ADJUSTMENT'))
) ENGINE=InnoDB;

CREATE TABLE waste_tracking (
  ingredient_id INT NOT NULL,
  waste_seq INT NOT NULL,
  waste_date DATE NOT NULL,
  amount_wasted NUMERIC(10,2) NOT NULL,
  reason TEXT,
  PRIMARY KEY (ingredient_id, waste_seq),
  CONSTRAINT fk_waste_ingredient
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE inventory_alert (
  alert_id INT AUTO_INCREMENT PRIMARY KEY,
  ingredient_id INT NOT NULL,
  alert_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  current_qty NUMERIC(10,2) NOT NULL,
  message TEXT NOT NULL,
  is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT fk_alert_ingredient
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------- MENU / TABLES / ORDERS ----------

CREATE TABLE menu_item (
  menu_item_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  category VARCHAR(50) DEFAULT 'Main Course',
  menu_price DECIMAL(10,2) NOT NULL,
  is_available BOOLEAN NOT NULL DEFAULT TRUE,
  description TEXT
) ENGINE=InnoDB;

CREATE TABLE menu_item_ingredient (
  menu_item_id INT NOT NULL,
  ingredient_id INT NOT NULL,
  quantity_required NUMERIC(10,2) NOT NULL,
  PRIMARY KEY (menu_item_id, ingredient_id),
  CONSTRAINT fk_mi_menu
    FOREIGN KEY (menu_item_id) REFERENCES menu_item(menu_item_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_mi_ingredient
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE restaurant_table (
  table_id INT AUTO_INCREMENT PRIMARY KEY,
  table_number INT NOT NULL UNIQUE,
  capacity INT NOT NULL,
  status VARCHAR(20) NOT NULL,
  CONSTRAINT chk_table_status CHECK (status IN ('AVAILABLE','OCCUPIED','RESERVED','CLOSED'))
) ENGINE=InnoDB;

CREATE TABLE customer_order (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  table_id INT NOT NULL,
  staff_id INT NOT NULL,
  order_datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  payment_status VARCHAR(20) NOT NULL,
  special_requests TEXT,
  total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_order_table
    FOREIGN KEY (table_id) REFERENCES restaurant_table(table_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_order_staff
    FOREIGN KEY (staff_id) REFERENCES staff(employee_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_payment_status CHECK (payment_status IN ('UNPAID','PAID','CANCELLED'))
) ENGINE=InnoDB;

CREATE TABLE order_item (
  order_id INT NOT NULL,
  menu_item_id INT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  item_status VARCHAR(20),
  PRIMARY KEY (order_id, menu_item_id),
  CONSTRAINT fk_oi_order
    FOREIGN KEY (order_id) REFERENCES customer_order(order_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_oi_menuitem
    FOREIGN KEY (menu_item_id) REFERENCES menu_item(menu_item_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_oi_quantity CHECK (quantity > 0),
  CONSTRAINT chk_item_status CHECK (item_status IN ('ORDERED','PREPARED','SERVED','CANCELLED'))
) ENGINE=InnoDB;

CREATE TABLE customer_review (
  order_id INT NOT NULL,
  review_seq INT NOT NULL,
  rating INT,
  comment TEXT,
  review_datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (order_id, review_seq),
  CONSTRAINT fk_review_order
    FOREIGN KEY (order_id) REFERENCES customer_order(order_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB;

-- ---------- SALES / EXPENSES / REPORTS ----------

CREATE TABLE sale (
  order_id INT PRIMARY KEY,
  sale_date DATE NOT NULL,
  sale_amount DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_sale_order
    FOREIGN KEY (order_id) REFERENCES customer_order(order_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE expense (
  expense_id INT AUTO_INCREMENT PRIMARY KEY,
  manager_id INT NOT NULL,
  expense_type VARCHAR(50) NOT NULL,
  expense_date DATE NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  description TEXT,
  CONSTRAINT fk_expense_manager
    FOREIGN KEY (manager_id) REFERENCES manager(employee_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE report (
  report_id INT AUTO_INCREMENT PRIMARY KEY,
  manager_id INT NOT NULL,
  report_type VARCHAR(30) NOT NULL,
  content TEXT,
  report_date DATE NOT NULL,
  period_start DATE,
  period_end DATE,
  CONSTRAINT fk_report_manager
    FOREIGN KEY (manager_id) REFERENCES manager(employee_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_report_type CHECK (report_type IN ('MENU_PERFORMANCE','STAFF_EFFICIENCY','INVENTORY_USAGE','COST_ANALYSIS'))
) ENGINE=InnoDB;

CREATE TABLE cost_analysis_report (
  report_id INT PRIMARY KEY,
  total_revenue DECIMAL(12,2) NOT NULL,
  total_expenses DECIMAL(12,2) NOT NULL,
  total_labor_cost DECIMAL(12,2) NOT NULL,
  net_profit DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_car_report
    FOREIGN KEY (report_id) REFERENCES report(report_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE report_menu_item (
  report_id INT NOT NULL,
  menu_item_id INT NOT NULL,
  PRIMARY KEY (report_id, menu_item_id),
  FOREIGN KEY (report_id) REFERENCES report(report_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (menu_item_id) REFERENCES menu_item(menu_item_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------- TRIGGERS ----------

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

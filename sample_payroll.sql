USE rms;

-- Calculate payroll for the existing schedule period (Dec 8-14, 2025)
-- This simulates what the Calculate Payroll button does

-- Emily Williams (employee_id: 3)
-- Shifts: 5 shifts totaling 40 hours
INSERT INTO payroll (employee_id, pay_period_start, pay_period_end, hours_worked, overtime_hours, gross_pay, payment_date)
VALUES (3, '2025-12-08', '2025-12-14', 40.00, 0.00, 673.08, '2025-12-15');

-- Michael Chen (employee_id: 4)
-- Shifts: 5 shifts totaling 40 hours
INSERT INTO payroll (employee_id, pay_period_start, pay_period_end, hours_worked, overtime_hours, gross_pay, payment_date)
VALUES (4, '2025-12-08', '2025-12-14', 40.00, 0.00, 634.62, '2025-12-15');

-- David Martinez (employee_id: 5)
-- Shifts: 4 shifts totaling 32 hours
INSERT INTO payroll (employee_id, pay_period_start, pay_period_end, hours_worked, overtime_hours, gross_pay, payment_date)
VALUES (5, '2025-12-08', '2025-12-14', 32.00, 0.00, 522.88, '2025-12-15');

-- Robert Thompson (employee_id: 7)
-- Shifts: 5 shifts totaling 60 hours (12 hours each shift = 4 overtime per shift)
INSERT INTO payroll (employee_id, pay_period_start, pay_period_end, hours_worked, overtime_hours, gross_pay, payment_date)
VALUES (7, '2025-12-08', '2025-12-14', 60.00, 20.00, 1643.27, '2025-12-15');

-- Create corresponding labor cost record
INSERT INTO labor_cost (period_start, period_end, total_hours, total_wages)
VALUES ('2025-12-08', '2025-12-14', 172.00, 3473.85);

-- Link payroll records to labor cost
SET @labor_cost_id = LAST_INSERT_ID();

INSERT INTO payroll_labor_cost (payroll_id, labor_cost_id)
SELECT payroll_id, @labor_cost_id
FROM payroll
WHERE pay_period_start = '2025-12-08' AND pay_period_end = '2025-12-14';

SELECT 'Payroll records created successfully!' AS Status;
SELECT COUNT(*) AS 'Total Payroll Records' FROM payroll;

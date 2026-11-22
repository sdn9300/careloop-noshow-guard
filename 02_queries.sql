-- ==============================================================================
-- CareLoop Clinics: No-Show Guard
-- Part 2: Relational Analytics & SQL Queries (02_queries.sql)
-- Course: IIT Roorkee & Masai School — Data Science & AI Capstone
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Task 2.1: Build and load the database (4 marks)
-- ------------------------------------------------------------------------------
-- Note: Skip CREATE DATABASE / USE lines if running on SQLiteOnline
CREATE DATABASE IF NOT EXISTS noshowguard;
USE noshowguard;

-- Drop existing tables for idempotent execution
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS clinics;

-- 1. Create Parent Table: clinics
CREATE TABLE clinics (
    clinic_id VARCHAR(5) PRIMARY KEY,
    clinic_name VARCHAR(40) NOT NULL,
    city VARCHAR(20) NOT NULL,
    tier VARCHAR(10),
    latitude DECIMAL(8,4),
    longitude DECIMAL(8,4),
    temp_c DECIMAL(5,1)
);

-- 2. Create Child Table: appointments
CREATE TABLE appointments (
    appointment_id VARCHAR(8) PRIMARY KEY,
    patient_id VARCHAR(8) NOT NULL,
    clinic_id VARCHAR(5) NOT NULL,
    booked_on DATE,
    appt_date DATE,
    age INT,
    gender VARCHAR(1),
    distance_km DECIMAL(5,1),
    fee_inr INT,
    booking_channel VARCHAR(10),
    visit_type VARCHAR(12),
    reminder_sent VARCHAR(3),
    prior_no_shows INT,
    status VARCHAR(10),
    lead_days INT,
    no_show INT,
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
);

-- [RUN load_data.sql SCRIPT HERE TO INSERT 8 CLINICS AND 990 APPOINTMENTS]

-- Verification 1: Confirm clinic count (Expected: 8)
SELECT COUNT(*) AS total_clinics FROM clinics;

-- Verification 2: Confirm appointment count and no-show count (Expected: 990 total, 218 no-shows)
SELECT COUNT(*) AS total_appointments, SUM(no_show) AS total_no_shows 
FROM appointments;

-- Verification 3: Duplicate Primary Key Insertion Test
-- Attempting to insert a duplicate appointment_id ('A0001'):
-- INSERT INTO appointments VALUES ('A0001', 'P196', 'C05', '2025-01-22', '2025-02-05', 48, 'F', 8.2, 500, 'App', 'Consultation', 'Yes', 0, 'Attended', 14, 0);

/*
================================================================================
TASK 2.1 DUPLICATE-KEY ERROR TEXT RECORDED:
================================================================================
MySQL 8 Server Error:
Error Code: 1062. Duplicate entry 'A0001' for key 'appointments.PRIMARY'

SQLite / SQLiteOnline Error:
Error: UNIQUE constraint failed: appointments.appointment_id
================================================================================
*/


-- ------------------------------------------------------------------------------
-- Task 2.2: No-show rate by clinic (5 marks)
-- ------------------------------------------------------------------------------

-- Query 2.2.A: High-volume clinics only (HAVING count >= 95), sorted by no_show_pct DESC
-- Expected order: Hadapsar (27.3%), Malviya Nagar (26.8%), Kothrud (22.5%),
--                 Vijay Nagar (20.8%), Edappally (16.2%), Vaishali Nagar (13.8%)
SELECT 
    c.clinic_name,
    c.city,
    COUNT(*) AS appointments,
    SUM(a.no_show) AS no_shows,
    ROUND(100.0 * SUM(a.no_show) / COUNT(*), 1) AS no_show_pct
FROM appointments a
JOIN clinics c ON a.clinic_id = c.clinic_id
GROUP BY c.clinic_id, c.clinic_name, c.city
HAVING COUNT(*) >= 95
ORDER BY no_show_pct DESC;

-- Query 2.2.B: All 8 clinics unfiltered to inspect low-volume locations
-- Finding: Gomti Nagar Care Point (Lucknow) has the highest raw no-show rate (33.3%),
--          but only 90 appointments. Sitabuldi Health Point (Nagpur) has 82 appts at 15.9%.
SELECT 
    c.clinic_name,
    c.city,
    COUNT(*) AS appointments,
    SUM(a.no_show) AS no_shows,
    ROUND(100.0 * SUM(a.no_show) / COUNT(*), 1) AS no_show_pct
FROM appointments a
JOIN clinics c ON a.clinic_id = c.clinic_id
GROUP BY c.clinic_id, c.clinic_name, c.city
ORDER BY no_show_pct DESC;


-- ------------------------------------------------------------------------------
-- Task 2.3: Does booking far ahead matter? (4 marks)
-- ------------------------------------------------------------------------------
-- Categorizes lead days into four distinct operational bands using CASE WHEN.
-- Upper limits inclusive: 7, 14, and 30 belong to the lower band.
-- Ordered chronologically by MIN(lead_days).
-- Expected: 1-7 (390 / 63 / 16.2%), 8-14 (304 / 53 / 17.4%), 
--           15-30 (253 / 76 / 30.0%), 31+ (43 / 26 / 60.5%)
SELECT 
    CASE 
        WHEN lead_days <= 7 THEN '1-7'
        WHEN lead_days <= 14 THEN '8-14'
        WHEN lead_days <= 30 THEN '15-30'
        ELSE '31+'
    END AS lead_time_band,
    COUNT(*) AS appointments,
    SUM(no_show) AS no_shows,
    ROUND(100.0 * SUM(no_show) / COUNT(*), 1) AS no_show_pct
FROM appointments
GROUP BY lead_time_band
ORDER BY MIN(lead_days) ASC;


-- ------------------------------------------------------------------------------
-- Task 2.4: Month-by-month trend (4 marks)
-- ------------------------------------------------------------------------------
-- Uses CTE 'monthly' and LAG() window function to calculate month-over-month rate deltas.
-- Expected: 2025-01 (157 / 24.8% / NULL), 2025-02 (151 / 20.5% / -4.3),
--           2025-03 (142 / 20.4% / -0.1), 2025-04 (177 / 20.9% / +0.5),
--           2025-05 (198 / 23.7% / +2.8), 2025-06 (165 / 21.2% / -2.5)
WITH monthly AS (
    SELECT 
        SUBSTR(appt_date, 1, 7) AS month,
        COUNT(*) AS appointments,
        ROUND(100.0 * SUM(no_show) / COUNT(*), 1) AS no_show_pct
    FROM appointments
    GROUP BY SUBSTR(appt_date, 1, 7)
)
SELECT 
    month,
    appointments,
    no_show_pct,
    ROUND(no_show_pct - LAG(no_show_pct) OVER (ORDER BY month), 1) AS mom_change
FROM monthly
ORDER BY month ASC;


-- ------------------------------------------------------------------------------
-- Task 2.5: Rank clinics inside each city (5 marks)
-- ------------------------------------------------------------------------------
-- Partitions by city using RANK() and compares clinic rate against corporate overall rate (22.02%).
-- Expected ranking:
--   Indore:  Vijay Nagar 20.8%, rank 1, below
--   Jaipur:  Malviya Nagar 26.8%, rank 1, above; Vaishali Nagar 13.8%, rank 2, below
--   Kochi:   Edappally 16.2%, rank 1, below
--   Lucknow: Gomti Nagar 33.3%, rank 1, above
--   Nagpur:  Sitabuldi 15.9%, rank 1, below
--   Pune:    Hadapsar 27.3%, rank 1, above; Kothrud 22.5%, rank 2, above
WITH clinic_rates AS (
    SELECT 
        c.clinic_name,
        c.city,
        ROUND(100.0 * SUM(a.no_show) / COUNT(*), 1) AS no_show_pct
    FROM appointments a
    JOIN clinics c ON a.clinic_id = c.clinic_id
    GROUP BY c.clinic_id, c.clinic_name, c.city
)
SELECT 
    city,
    clinic_name,
    no_show_pct,
    RANK() OVER (PARTITION BY city ORDER BY no_show_pct DESC) AS rank_in_city,
    CASE 
        WHEN no_show_pct > (SELECT ROUND(100.0 * SUM(no_show) / COUNT(*), 2) FROM appointments) THEN 'above'
        WHEN no_show_pct < (SELECT ROUND(100.0 * SUM(no_show) / COUNT(*), 2) FROM appointments) THEN 'below'
        ELSE 'equal'
    END AS vs_overall
FROM clinic_rates
ORDER BY city ASC, rank_in_city ASC;

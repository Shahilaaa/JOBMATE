-- PostgreSQL schema for Your JobMate
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('employee', 'stakeholder')) NOT NULL,
    approved BOOLEAN DEFAULT FALSE
);

CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill VARCHAR(100),
    rate_hourly NUMERIC(10,2),
    rate_daily NUMERIC(10,2),
    rate_monthly NUMERIC(10,2),
    availability TEXT
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    stakeholder_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    employee_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_id INT NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    duration VARCHAR(10) CHECK (duration IN ('hour', 'day', 'month')),
    cost NUMERIC(10,2),
    status VARCHAR(20) DEFAULT 'pending'
);

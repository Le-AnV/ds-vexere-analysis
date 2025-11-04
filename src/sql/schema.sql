-- ============================
-- 		DATABASE: Vexere
-- ============================


-- ============================
-- 		1. Bảng cities
-- ============================
CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(50) NOT NULL,
    city_abbr VARCHAR(10)
);

-- ============================
-- 		2. Bảng routes
-- ============================
CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    start_city_id INTEGER NOT NULL REFERENCES cities(city_id) ON DELETE CASCADE,
    destination_city_id INTEGER NOT NULL REFERENCES cities(city_id) ON DELETE CASCADE,
    UNIQUE (start_city_id, destination_city_id)
);

-- ============================
-- 		3. Bảng bus_companies
-- ============================
CREATE TABLE bus_companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    reviewer_count INTEGER DEFAULT 0,
    rating_overall NUMERIC(3,2) CHECK (rating_overall BETWEEN 0 AND 5),
    rating_safety NUMERIC(3,2) CHECK (rating_safety BETWEEN 0 AND 5),
    rating_info_accuracy NUMERIC(3,2) CHECK (rating_info_accuracy BETWEEN 0 AND 5),
    rating_info_completeness NUMERIC(3,2) CHECK (rating_info_completeness BETWEEN 0 AND 5),
    rating_staff_attitude NUMERIC(3,2) CHECK (rating_staff_attitude BETWEEN 0 AND 5),
    rating_comfort NUMERIC(3,2) CHECK (rating_comfort BETWEEN 0 AND 5),
    rating_service_quality NUMERIC(3,2) CHECK (rating_service_quality BETWEEN 0 AND 5),
    rating_punctuality NUMERIC(3,2) CHECK (rating_punctuality BETWEEN 0 AND 5)
);

-- ============================
-- 		4. Bảng trips
-- ============================
CREATE TABLE trips (
    trip_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES bus_companies(company_id) ON DELETE CASCADE,
    route_id INTEGER NOT NULL REFERENCES routes(route_id) ON DELETE CASCADE,
    number_of_seat INTEGER,
    departure_date DATE NOT NULL,
    departure_time TIME WITHOUT TIME ZONE,
    duration_minutes INTEGER CHECK (duration_minutes > 0),
	pickup_point VARCHAR(100), 
	dropoff_point VARCHAR(100),
    price_discounted NUMERIC(10,0) CHECK (price_discounted >= 0),
	price_original NUMERIC(10,0) CHECK (price_original >= 0)
);
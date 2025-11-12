-- BUS COMPANIES
CREATE TABLE bus_companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) UNIQUE NOT NULL
);

-- CITIES
CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(50) UNIQUE NOT NULL
);

-- ROUTES
CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    start_city_id INTEGER NOT NULL REFERENCES cities(city_id) ON DELETE CASCADE,
    destination_city_id INTEGER NOT NULL REFERENCES cities(city_id) ON DELETE CASCADE,
    UNIQUE (start_city_id, destination_city_id),
    CONSTRAINT check_cities_different CHECK (start_city_id <> destination_city_id)
);

-- TRIPS
CREATE TABLE trips (
    trip_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES bus_companies(company_id) ON DELETE CASCADE,
    route_id INTEGER NOT NULL REFERENCES routes(route_id) ON DELETE CASCADE,
    number_of_seat INTEGER NOT NULL CHECK (number_of_seat > 0),
    departure_date DATE NOT NULL,
    departure_time TIME WITHOUT TIME ZONE,
    arrival_time TIME WITHOUT TIME ZONE,
    duration_minutes INTEGER CHECK (duration_minutes > 0),
    pickup_point VARCHAR(100),
    dropoff_point VARCHAR(100),
    price_original NUMERIC(10,0) NOT NULL CHECK (price_original >= 0),
    price_discounted NUMERIC(10,0) CHECK (price_discounted >= 0)
);

-- COMPANY ROUTE RATINGS
CREATE TABLE company_route_ratings (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES bus_companies(company_id) ON DELETE CASCADE,
    route_id INT NOT NULL REFERENCES routes(route_id) ON DELETE CASCADE,
    crawl_date DATE NOT NULL DEFAULT CURRENT_DATE,
    reviewer_count INT NOT NULL DEFAULT 0 CHECK (reviewer_count >= 0),
    rating_overall NUMERIC(3,2),
    rating_safety NUMERIC(3,2),
    rating_info_accuracy NUMERIC(3,2),
    rating_info_completeness NUMERIC(3,2),
    rating_staff_attitude NUMERIC(3,2),
    rating_comfort NUMERIC(3,2),
    rating_service_quality NUMERIC(3,2),
    rating_punctuality NUMERIC(3,2),
    UNIQUE (company_id, route_id, crawl_date)
);

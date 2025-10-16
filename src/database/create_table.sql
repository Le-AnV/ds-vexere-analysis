CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(50) NOT NULL,
    city_abbr VARCHAR(10)
);

CREATE TABLE bus_companies (
    bus_company_id SERIAL PRIMARY KEY,
    bus_company_name VARCHAR(100) NOT NULL,
    rating_overall NUMERIC(3, 2),
    rating_service_quantity NUMERIC(3, 2),
    rating_comfort NUMERIC(3, 2),
    rating_punctuality NUMERIC(3, 2),
    rating_staff_attitude NUMERIC(3, 2),
    rating_safety NUMERIC(3, 2),
    rating_info_accuracy NUMERIC(3, 2)
);

CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    start_city_id INTEGER NOT NULL REFERENCES cities(city_id),
    destination_city_id INTEGER NOT NULL REFERENCES cities(city_id),
    -- Đảm bảo tuyến đường không trùng lặp
    UNIQUE (start_city_id, destination_city_id)
);


CREATE TABLE trips (
    trip_id SERIAL PRIMARY KEY,
    bus_company_id INTEGER NOT NULL REFERENCES bus_companies(bus_company_id),
    route_id INTEGER NOT NULL REFERENCES routes(route_id),
    number_of_seat INTEGER,
    departure_date DATE,
    departure_time TIME WITHOUT TIME ZONE,
    arrival_time TIME WITHOUT TIME ZONE,
    duration_h_m INTERVAL, -- Dùng INTERVAL cho khoảng thời gian (ví dụ: '04:30:00' cho 4 giờ 30 phút)
    pickup_point VARCHAR(100),
    dropoff_point VARCHAR(100),
    price_original NUMERIC(10, 0),
    price_discounted NUMERIC(10, 0),
    discount_percentage NUMERIC(4, 2)
);
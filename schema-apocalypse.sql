-- SQL Schema for Apocalypse Indicators Integration
-- Add to existing nwo-signal-spectrum database

-- Table for apocalypse signals
CREATE TABLE IF NOT EXISTS apocalypse_signals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical', 'extreme') NOT NULL,
    description TEXT NOT NULL,
    metadata JSON,
    region VARCHAR(50),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_severity (severity),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table for signal baselines (historical averages)
CREATE TABLE IF NOT EXISTS signal_baselines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    value DECIMAL(20, 8) NOT NULL,
    sample_count INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_type_region (type, region)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table for apocalypse level history
CREATE TABLE IF NOT EXISTS apocalypse_level_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level TINYINT NOT NULL CHECK (level BETWEEN 1 AND 5),
    description VARCHAR(255),
    active_signals INT DEFAULT 0,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_recorded (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table for aircraft tracking (for aviation anomaly detection)
CREATE TABLE IF NOT EXISTS aircraft_sightings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    icao_hex VARCHAR(6) NOT NULL,
    callsign VARCHAR(10),
    aircraft_type VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    altitude INT,
    speed INT,
    heading INT,
    is_business_jet BOOLEAN DEFAULT FALSE,
    owner_category ENUM('private', 'corporate', 'government', 'military', 'unknown') DEFAULT 'unknown',
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_icao (icao_hex),
    INDEX idx_detected (detected_at),
    INDEX idx_business_jet (is_business_jet, detected_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table for seismic events
CREATE TABLE IF NOT EXISTS seismic_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usgs_id VARCHAR(50) UNIQUE,
    magnitude DECIMAL(3, 1) NOT NULL,
    place VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    depth DECIMAL(8, 3),
    tsunami_warning BOOLEAN DEFAULT FALSE,
    felt_reports INT,
    event_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_magnitude (magnitude),
    INDEX idx_event_time (event_time),
    INDEX idx_location (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table for solar activity
CREATE TABLE IF NOT EXISTS solar_activity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_type ENUM('flare', 'cme', 'geomagnetic_storm', 'proton_event') NOT NULL,
    flare_class VARCHAR(2),
    kp_index TINYINT,
    speed_kms INT,
    direction VARCHAR(20),
    arrival_time DATETIME,
    event_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (activity_type),
    INDEX idx_event_time (event_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table for radiation readings
CREATE TABLE IF NOT EXISTS radiation_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50),
    location_name VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    value_usvh DECIMAL(10, 6),
    baseline_usvh DECIMAL(10, 6),
    deviation_percent DECIMAL(8, 2),
    measured_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor (sensor_id),
    INDEX idx_measured (measured_at),
    INDEX idx_location (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table for near-Earth objects
CREATE TABLE IF NOT EXISTS neo_objects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nasa_id VARCHAR(50) UNIQUE,
    name VARCHAR(100),
    diameter_min_m DECIMAL(10, 3),
    diameter_max_m DECIMAL(10, 3),
    is_hazardous BOOLEAN DEFAULT FALSE,
    approach_date DATE,
    miss_distance_km DECIMAL(15, 3),
    miss_distance_ld DECIMAL(10, 6),
    relative_velocity_kmh DECIMAL(12, 3),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_approach (approach_date),
    INDEX idx_hazardous (is_hazardous),
    INDEX idx_distance (miss_distance_ld)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- View for current apocalypse dashboard
CREATE OR REPLACE VIEW apocalypse_dashboard AS
SELECT 
    (SELECT COUNT(*) FROM apocalypse_signals 
     WHERE created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR) 
     AND severity IN ('critical', 'extreme')) as critical_count,
    (SELECT COUNT(*) FROM apocalypse_signals 
     WHERE created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)) as total_signals_24h,
    (SELECT MAX(magnitude) FROM seismic_events 
     WHERE event_time > DATE_SUB(NOW(), INTERVAL 24 HOUR)) as max_quake_magnitude,
    (SELECT COUNT(*) FROM aircraft_sightings 
     WHERE is_business_jet = TRUE 
     AND detected_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)) as business_jets_last_hour,
    (SELECT MAX(level) FROM apocalypse_level_history 
     WHERE recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)) as max_level_24h,
    NOW() as last_updated;

-- Insert initial baselines
INSERT INTO signal_baselines (type, region, value) VALUES
('aviation', 'global', 150.0),
('aviation', 'davos', 25.0),
('aviation', 'maui', 15.0),
('aviation', 'monaco', 30.0),
('radiation', 'global', 0.1),
('seismic', 'global', 2.5)
ON DUPLICATE KEY UPDATE value = VALUES(value);

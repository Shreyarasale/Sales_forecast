CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('ACCOUNT_MANAGER', 'SEGMENT_HEAD', 'FACTORY_HEAD') NOT NULL,
  segment_id INT NULL,
  factory_id INT NULL,
  account_manager_id INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS forecasts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  account_manager_id INT NOT NULL,
  customer_id INT NOT NULL,
  product_designation VARCHAR(100) NOT NULL,
  factory VARCHAR(100) NOT NULL,
  forecast_month VARCHAR(7) NOT NULL,
  input_volume INT NOT NULL,
  final_volume INT NOT NULL,
  mode ENUM('history', 'user_growth', 'market_intelligence') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS market_intelligence (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  factor_percent DECIMAL(6,2) NOT NULL,
  customer_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (id, username, password_hash, role, segment_id, factory_id, account_manager_id)
VALUES
  (1, 'john.wicks', '$2a$08$1Jf5Xl2T4tYf2gYpD2dE7uR.2tGq6uVd0hOeQwFplQWv6yv0sW4H2', 'ACCOUNT_MANAGER', NULL, NULL, 1),
  (2, 'rachel', '$2a$08$1Jf5Xl2T4tYf2gYpD2dE7uR.2tGq6uVd0hOeQwFplQWv6yv0sW4H2', 'SEGMENT_HEAD', 101, NULL, NULL),
  (3, 'abhinav', '$2a$08$1Jf5Xl2T4tYf2gYpD2dE7uR.2tGq6uVd0hOeQwFplQWv6yv0sW4H2', 'FACTORY_HEAD', NULL, 501, NULL)
ON DUPLICATE KEY UPDATE username = VALUES(username);

INSERT INTO market_intelligence (title, factor_percent, customer_id)
VALUES
  ('Tractor segment is projected to grow by 10 percent this quarter', 10.00, 1),
  ('Mahindra announced capex expansion in west India', 6.00, 1),
  ('Farm equipment replacement demand improved in north region', 4.00, 2);

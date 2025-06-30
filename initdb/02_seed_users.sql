-- Populate users with realistic data
INSERT INTO users (username, email, password_hash, created_at) VALUES
('john_doe', 'john.doe@email.com', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQD.1Zom', NOW() - INTERVAL '6 months'),
('sarah_smith', 'sarah.smith@email.com', '$2a$12$9dKzKqEHAR6IXOPj3z9IY.meTtCa7M9E0Py3fEr1kkHxZqKZ4XKlW', NOW() - INTERVAL '5 months'),
('mike_wilson', 'mike.wilson@email.com', '$2a$12$QdCyS0TI88bZ5KoLKp7pJ.Xq.6Zg5EGxYUn7BWsXHXGc0LOYeHKkq', NOW() - INTERVAL '5 months'),
('emily_brown', 'emily.brown@email.com', '$2a$12$7EyPZpGhX5VN3r4IW4JQPOyy6F4YnHf4MQ9RS./.U0i4v0tHHZcNS', NOW() - INTERVAL '4 months'),
('david_jones', 'david.jones@email.com', '$2a$12$KZvG4YcGWNJkW6c2FOKnUOHPUt0bRrYGb.J9I4kPHPzq0HUUwXBwa', NOW() - INTERVAL '4 months'),
('lisa_taylor', 'lisa.taylor@email.com', '$2a$12$1xK8Gu.gqV/IhXRbF.BXfeB3Xc3aa8LwZd6oJ.Bs0ZjnL9QgC9Qje', NOW() - INTERVAL '3 months'),
('james_anderson', 'james.anderson@email.com', '$2a$12$QEr5KjXb5ZH.RH8tK7ZE8O/0deB3kQWPUFE8DpYG0gYnT.YnTQx6.', NOW() - INTERVAL '3 months'),
('amy_garcia', 'amy.garcia@email.com', '$2a$12$mK8YP9J8oKz.Xs3ZJq5Kz.1xR1YH6IzCU8NwTX3xJ1QW3Qq5O2KPW', NOW() - INTERVAL '2 months'),
('robert_martinez', 'robert.martinez@email.com', '$2a$12$Xb0Yz1g5D5O1o2J.qX9Qn.4J0QX8v8X3Z5Y2K3Q4Z5Y2K3Q4Z5Y2K', NOW() - INTERVAL '2 months'),
('jennifer_lopez', 'jennifer.lopez@email.com', '$2a$12$Xb0Yz1g5D5O1o2J.qX9Qn.4J0QX8v8X3Z5Y2K3Q4Z5Y2K3Q4Z5Y2K', NOW() - INTERVAL '1 month');

-- Add more users as needed for a large dataset

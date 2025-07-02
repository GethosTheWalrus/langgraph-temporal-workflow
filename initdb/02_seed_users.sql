-- Populate users with realistic enhanced data
INSERT INTO users (
    username, email, password_hash, first_name, last_name, phone, date_of_birth,
    customer_segment, preferred_contact_method, marketing_opt_in, customer_status,
    lifetime_value, last_engagement_date, created_at
) VALUES
-- Gaming enthusiasts and high-value customers
('john_doe', 'john.doe@email.com', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQD.1Zom', 
 'John', 'Doe', '555-0101', '1988-03-15', 'gaming', 'email', true, 'vip', 
 8500.00, NOW() - INTERVAL '10 days', NOW() - INTERVAL '6 months'),

('sarah_smith', 'sarah.smith@email.com', '$2a$12$9dKzKqEHAR6IXOPj3z9IY.meTtCa7M9E0Py3fEr1kkHxZqKZ4XKlW',
 'Sarah', 'Smith', '555-0102', '1992-07-22', 'workstation', 'phone', true, 'active',
 6200.00, NOW() - INTERVAL '15 days', NOW() - INTERVAL '5 months'),

('mike_wilson', 'mike.wilson@email.com', '$2a$12$QdCyS0TI88bZ5KoLKp7pJ.Xq.6Zg5EGxYUn7BWsXHXGc0LOYeHKkq',
 'Mike', 'Wilson', '555-0103', '1985-11-08', 'enthusiast', 'email', true, 'active',
 4800.00, NOW() - INTERVAL '8 days', NOW() - INTERVAL '5 months'),

('emily_brown', 'emily.brown@email.com', '$2a$12$7EyPZpGhX5VN3r4IW4JQPOyy6F4YnHf4MQ9RS./.U0i4v0tHHZcNS',
 'Emily', 'Brown', '555-0104', '1994-02-14', 'budget', 'email', false, 'active',
 2400.00, NOW() - INTERVAL '3 days', NOW() - INTERVAL '4 months'),

('david_jones', 'david.jones@email.com', '$2a$12$KZvG4YcGWNJkW6c2FOKnUOHPUt0bRrYGb.J9I4kPHPzq0HUUwXBwa',
 'David', 'Jones', '555-0105', '1990-05-30', 'gaming', 'sms', true, 'at_risk',
 3200.00, NOW() - INTERVAL '45 days', NOW() - INTERVAL '4 months'),

('lisa_taylor', 'lisa.taylor@email.com', '$2a$12$1xK8Gu.gqV/IhXRbF.BXfeB3Xc3aa8LwZd6oJ.Bs0ZjnL9QgC9Qje',
 'Lisa', 'Taylor', '555-0106', '1987-09-12', 'workstation', 'email', true, 'active',
 5600.00, NOW() - INTERVAL '12 days', NOW() - INTERVAL '3 months'),

('james_anderson', 'james.anderson@email.com', '$2a$12$QEr5KjXb5ZH.RH8tK7ZE8O/0deB3kQWPUFE8DpYG0gYnT.YnTQx6.',
 'James', 'Anderson', '555-0107', '1983-12-03', 'enthusiast', 'phone', true, 'vip',
 9200.00, NOW() - INTERVAL '5 days', NOW() - INTERVAL '3 months'),

('amy_garcia', 'amy.garcia@email.com', '$2a$12$mK8YP9J8oKz.Xs3ZJq5Kz.1xR1YH6IzCU8NwTX3xJ1QW3Qq5O2KPW',
 'Amy', 'Garcia', '555-0108', '1991-04-18', 'budget', 'email', false, 'active',
 1800.00, NOW() - INTERVAL '20 days', NOW() - INTERVAL '2 months'),

('robert_martinez', 'robert.martinez@email.com', '$2a$12$Xb0Yz1g5D5O1o2J.qX9Qn.4J0QX8v8X3Z5Y2K3Q4Z5Y2K3Q4Z5Y2K',
 'Robert', 'Martinez', '555-0109', '1989-08-25', 'gaming', 'email', true, 'active',
 4100.00, NOW() - INTERVAL '7 days', NOW() - INTERVAL '2 months'),

('jennifer_lopez', 'jennifer.lopez@email.com', '$2a$12$Xb0Yz1g5D5O1o2J.qX9Qn.4J0QX8v8X3Z5Y2K3Q4Z5Y2K3Q4Z5Y2K',
 'Jennifer', 'Lopez', '555-0110', '1993-01-10', 'workstation', 'phone', true, 'at_risk',
 2900.00, NOW() - INTERVAL '65 days', NOW() - INTERVAL '1 month'),

-- Additional users for more comprehensive testing
('alex_chen', 'alex.chen@email.com', '$2a$12$ExampleHashForTesting123456789', 
 'Alex', 'Chen', '555-0111', '1986-06-20', 'enthusiast', 'email', true, 'churned',
 0.00, NOW() - INTERVAL '180 days', NOW() - INTERVAL '8 months'),

('maria_rodriguez', 'maria.rodriguez@email.com', '$2a$12$ExampleHashForTesting123456789',
 'Maria', 'Rodriguez', '555-0112', '1995-10-05', 'budget', 'sms', false, 'active',
 950.00, NOW() - INTERVAL '25 days', NOW() - INTERVAL '2 months');

-- Add more users as needed for a large dataset

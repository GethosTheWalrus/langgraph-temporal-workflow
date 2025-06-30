-- Populate orders with realistic data
WITH user_address_ids AS (
    SELECT u.id as user_id, a.id as address_id 
    FROM users u 
    JOIN addresses a ON u.id = a.user_id
)
INSERT INTO orders (user_id, address_id, status, total, order_type, created_at, updated_at)
VALUES
-- Recent orders (last month)
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 1),
    (SELECT address_id FROM user_address_ids WHERE user_id = 1),
    'delivered', 4299.99, 'prebuilt',
    NOW() - INTERVAL '25 days',
    NOW() - INTERVAL '22 days'
),
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 2),
    (SELECT address_id FROM user_address_ids WHERE user_id = 2),
    'delivered', 3799.99, 'prebuilt',
    NOW() - INTERVAL '20 days',
    NOW() - INTERVAL '17 days'
),
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 3),
    (SELECT address_id FROM user_address_ids WHERE user_id = 3),
    'shipped', 2999.99, 'prebuilt',
    NOW() - INTERVAL '15 days',
    NOW() - INTERVAL '13 days'
),
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 4),
    (SELECT address_id FROM user_address_ids WHERE user_id = 4),
    'processing', 2199.99, 'prebuilt',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days'
),

-- Orders from 2-3 months ago
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 5),
    (SELECT address_id FROM user_address_ids WHERE user_id = 5),
    'delivered', 1899.99, 'prebuilt',
    NOW() - INTERVAL '2 months',
    NOW() - INTERVAL '2 months' + INTERVAL '3 days'
),
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 6),
    (SELECT address_id FROM user_address_ids WHERE user_id = 6),
    'delivered', 1499.99, 'prebuilt',
    NOW() - INTERVAL '2 months' - INTERVAL '15 days',
    NOW() - INTERVAL '2 months' - INTERVAL '12 days'
),
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 7),
    (SELECT address_id FROM user_address_ids WHERE user_id = 7),
    'delivered', 999.99, 'prebuilt',
    NOW() - INTERVAL '3 months',
    NOW() - INTERVAL '3 months' + INTERVAL '3 days'
),

-- Orders from 4-6 months ago
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 8),
    (SELECT address_id FROM user_address_ids WHERE user_id = 8),
    'delivered', 4499.99, 'prebuilt',
    NOW() - INTERVAL '4 months',
    NOW() - INTERVAL '4 months' + INTERVAL '3 days'
),
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 9),
    (SELECT address_id FROM user_address_ids WHERE user_id = 9),
    'delivered', 3999.99, 'prebuilt',
    NOW() - INTERVAL '5 months',
    NOW() - INTERVAL '5 months' + INTERVAL '3 days'
),
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 10),
    (SELECT address_id FROM user_address_ids WHERE user_id = 10),
    'delivered', 2999.99, 'prebuilt',
    NOW() - INTERVAL '6 months',
    NOW() - INTERVAL '6 months' + INTERVAL '3 days'
),

-- Custom build orders
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 1),
    (SELECT address_id FROM user_address_ids WHERE user_id = 1),
    'delivered', 3299.99, 'custom',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '7 days'
),
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 3),
    (SELECT address_id FROM user_address_ids WHERE user_id = 3),
    'shipped', 2799.99, 'custom',
    NOW() - INTERVAL '8 days',
    NOW() - INTERVAL '6 days'
),
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 5),
    (SELECT address_id FROM user_address_ids WHERE user_id = 5),
    'processing', 1999.99, 'custom',
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '3 days'
),

-- Cancelled orders
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 2),
    (SELECT address_id FROM user_address_ids WHERE user_id = 2),
    'cancelled', 4299.99, 'prebuilt',
    NOW() - INTERVAL '45 days',
    NOW() - INTERVAL '44 days'
),
(
    (SELECT user_id FROM user_address_ids WHERE user_id = 4),
    (SELECT address_id FROM user_address_ids WHERE user_id = 4),
    'cancelled', 2199.99, 'custom',
    NOW() - INTERVAL '35 days',
    NOW() - INTERVAL '34 days'
);

-- Add thousands more orders as needed

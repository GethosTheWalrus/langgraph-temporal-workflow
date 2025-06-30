-- Populate carts
INSERT INTO carts (user_id, created_at) VALUES
(1, NOW() - INTERVAL '1 day'),
(2, NOW() - INTERVAL '2 days'),
(3, NOW() - INTERVAL '3 days'),
(4, NOW() - INTERVAL '4 days'),
(5, NOW() - INTERVAL '5 days');

-- Add thousands more carts as needed

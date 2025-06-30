-- Populate reviews
INSERT INTO reviews (user_id, prebuilt_pc_id, rating, comment, created_at) VALUES
(1, 1, 5, 'Amazing gaming PC!', NOW() - INTERVAL '25 days'),
(2, 2, 4, 'Great for creative work.', NOW() - INTERVAL '8 days'),
(3, 3, 3, 'Good value for the price.', NOW() - INTERVAL '1 day'),
(4, 4, 5, 'Super compact and powerful.', NOW() - INTERVAL '3 days'),
(5, 5, 4, 'Very quiet and efficient.', NOW() - INTERVAL '2 days');

-- Add thousands more reviews as needed

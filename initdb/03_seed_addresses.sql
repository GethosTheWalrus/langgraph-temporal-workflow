-- Populate addresses with realistic data
WITH user_ids AS (
    SELECT id, username FROM users
)
INSERT INTO addresses (user_id, address_line1, address_line2, city, state, postal_code, country, created_at)
SELECT 
    u.id,
    CASE u.username
        WHEN 'john_doe' THEN '123 Main Street'
        WHEN 'sarah_smith' THEN '456 Oak Avenue'
        WHEN 'mike_wilson' THEN '789 Pine Road'
        WHEN 'emily_brown' THEN '321 Maple Drive'
        WHEN 'david_jones' THEN '654 Cedar Lane'
        WHEN 'lisa_taylor' THEN '987 Birch Street'
        WHEN 'james_anderson' THEN '147 Elm Court'
        WHEN 'amy_garcia' THEN '258 Willow Way'
        WHEN 'robert_martinez' THEN '369 Spruce Boulevard'
        WHEN 'jennifer_lopez' THEN '741 Ash Street'
    END,
    CASE u.username
        WHEN 'john_doe' THEN 'Apt 4B'
        WHEN 'sarah_smith' THEN 'Suite 205'
        WHEN 'mike_wilson' THEN NULL
        WHEN 'emily_brown' THEN 'Unit 12'
        WHEN 'david_jones' THEN NULL
        WHEN 'lisa_taylor' THEN 'Apt 7C'
        WHEN 'james_anderson' THEN NULL
        WHEN 'amy_garcia' THEN 'Suite 101'
        WHEN 'robert_martinez' THEN NULL
        WHEN 'jennifer_lopez' THEN 'Unit 15'
    END,
    CASE u.username
        WHEN 'john_doe' THEN 'New York'
        WHEN 'sarah_smith' THEN 'Los Angeles'
        WHEN 'mike_wilson' THEN 'Chicago'
        WHEN 'emily_brown' THEN 'Houston'
        WHEN 'david_jones' THEN 'Phoenix'
        WHEN 'lisa_taylor' THEN 'Philadelphia'
        WHEN 'james_anderson' THEN 'San Antonio'
        WHEN 'amy_garcia' THEN 'San Diego'
        WHEN 'robert_martinez' THEN 'Dallas'
        WHEN 'jennifer_lopez' THEN 'San Jose'
    END,
    CASE u.username
        WHEN 'john_doe' THEN 'NY'
        WHEN 'sarah_smith' THEN 'CA'
        WHEN 'mike_wilson' THEN 'IL'
        WHEN 'emily_brown' THEN 'TX'
        WHEN 'david_jones' THEN 'AZ'
        WHEN 'lisa_taylor' THEN 'PA'
        WHEN 'james_anderson' THEN 'TX'
        WHEN 'amy_garcia' THEN 'CA'
        WHEN 'robert_martinez' THEN 'TX'
        WHEN 'jennifer_lopez' THEN 'CA'
    END,
    CASE u.username
        WHEN 'john_doe' THEN '10001'
        WHEN 'sarah_smith' THEN '90001'
        WHEN 'mike_wilson' THEN '60601'
        WHEN 'emily_brown' THEN '77001'
        WHEN 'david_jones' THEN '85001'
        WHEN 'lisa_taylor' THEN '19101'
        WHEN 'james_anderson' THEN '78201'
        WHEN 'amy_garcia' THEN '92101'
        WHEN 'robert_martinez' THEN '75201'
        WHEN 'jennifer_lopez' THEN '95101'
    END,
    'United States',
    NOW() - INTERVAL '6 months'
FROM user_ids u;

-- Add more addresses as needed for a large dataset

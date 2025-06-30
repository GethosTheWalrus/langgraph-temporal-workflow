-- Populate order tracking with realistic data
WITH order_statuses AS (
    SELECT 
        id,
        status as order_status,
        created_at,
        updated_at
    FROM orders
    WHERE status NOT IN ('cancelled', 'processing')
)
INSERT INTO order_tracking (order_id, status, updated_at, tracking_number)
SELECT 
    o.id,
    'order_received',
    o.created_at + INTERVAL '1 hour',
    CASE 
        WHEN o.order_status IN ('shipped', 'delivered') THEN 
            '1Z' || UPPER(
                SUBSTRING(
                    MD5(RANDOM()::TEXT || CLOCK_TIMESTAMP()::TEXT)
                    FROM 1 FOR 16
                )
            )
        ELSE NULL
    END
FROM order_statuses o
UNION ALL
SELECT 
    o.id,
    'processing',
    o.created_at + INTERVAL '1 day',
    CASE 
        WHEN o.order_status IN ('shipped', 'delivered') THEN 
            '1Z' || UPPER(
                SUBSTRING(
                    MD5(RANDOM()::TEXT || CLOCK_TIMESTAMP()::TEXT)
                    FROM 1 FOR 16
                )
            )
        ELSE NULL
    END
FROM order_statuses o
UNION ALL
SELECT 
    o.id,
    'shipped',
    o.created_at + INTERVAL '2 days',
    CASE 
        WHEN o.order_status IN ('shipped', 'delivered') THEN 
            '1Z' || UPPER(
                SUBSTRING(
                    MD5(RANDOM()::TEXT || CLOCK_TIMESTAMP()::TEXT)
                    FROM 1 FOR 16
                )
            )
        ELSE NULL
    END
FROM order_statuses o
WHERE o.order_status IN ('shipped', 'delivered')
UNION ALL
SELECT 
    o.id,
    'delivered',
    o.updated_at,
    CASE 
        WHEN o.order_status = 'delivered' THEN 
            '1Z' || UPPER(
                SUBSTRING(
                    MD5(RANDOM()::TEXT || CLOCK_TIMESTAMP()::TEXT)
                    FROM 1 FOR 16
                )
            )
        ELSE NULL
    END
FROM order_statuses o
WHERE o.order_status = 'delivered';

-- Add tracking entries for processing orders
INSERT INTO order_tracking (order_id, status, updated_at, tracking_number)
SELECT 
    id,
    'order_received',
    created_at + INTERVAL '1 hour',
    NULL
FROM orders
WHERE status = 'processing'
UNION ALL
SELECT 
    id,
    'processing',
    updated_at,
    NULL
FROM orders
WHERE status = 'processing';

-- Add thousands more tracking records as needed

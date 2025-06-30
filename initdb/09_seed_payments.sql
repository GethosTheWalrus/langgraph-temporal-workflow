-- Populate payments with realistic data
WITH order_data AS (
    SELECT 
        id, 
        total, 
        status,
        created_at,
        CASE 
            WHEN status = 'cancelled' THEN 'failed'
            WHEN status IN ('delivered', 'shipped', 'processing') THEN 'completed'
            ELSE 'pending'
        END as payment_status
    FROM orders
)
INSERT INTO payments (order_id, payment_method, payment_status, amount, transaction_id, created_at)
SELECT 
    o.id,
    CASE (EXTRACT(DOW FROM o.created_at) + id) % 3
        WHEN 0 THEN 'credit_card'
        WHEN 1 THEN 'paypal'
        ELSE 'bank_transfer'
    END as payment_method,
    o.payment_status,
    o.total,
    CASE 
        WHEN o.payment_status = 'completed' THEN 
            'txn_' || LOWER(
                SUBSTRING(
                    MD5(RANDOM()::TEXT || CLOCK_TIMESTAMP()::TEXT)
                    FROM 1 FOR 20
                )
            )
        ELSE NULL
    END as transaction_id,
    o.created_at + INTERVAL '1 hour'
FROM order_data o;

-- Add failed payment attempts for cancelled orders
INSERT INTO payments (order_id, payment_method, payment_status, amount, transaction_id, created_at)
SELECT 
    o.id,
    CASE (EXTRACT(DOW FROM o.created_at) + id) % 3
        WHEN 0 THEN 'credit_card'
        WHEN 1 THEN 'paypal'
        ELSE 'bank_transfer'
    END as payment_method,
    'failed',
    o.total,
    NULL as transaction_id,
    o.created_at + INTERVAL '30 minutes'
FROM orders o
WHERE o.status = 'cancelled';

-- Add thousands more payments as needed

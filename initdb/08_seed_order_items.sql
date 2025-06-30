-- Populate order items with realistic data
WITH order_ids AS (
    SELECT id, order_type, total FROM orders
),
prebuilt_ids AS (
    SELECT id, name, price FROM prebuilt_pcs
),
part_ids AS (
    SELECT id, name, price FROM pc_parts
)
INSERT INTO order_items (order_id, prebuilt_pc_id, pc_part_id, quantity, price)
SELECT 
    o.id as order_id,
    CASE 
        WHEN o.order_type = 'prebuilt' THEN
            CASE 
                WHEN o.total > 4000 THEN (SELECT id FROM prebuilt_ids WHERE name IN ('Titan X Pro', 'Creator Pro Max') LIMIT 1)
                WHEN o.total > 3500 THEN (SELECT id FROM prebuilt_ids WHERE name IN ('Phoenix AMD Edition', 'Render Master') LIMIT 1)
                WHEN o.total > 2500 THEN (SELECT id FROM prebuilt_ids WHERE name = 'Nova RTX 4080' LIMIT 1)
                WHEN o.total > 2000 THEN (SELECT id FROM prebuilt_ids WHERE name = 'Stellar Gaming Pro' LIMIT 1)
                WHEN o.total > 1500 THEN (SELECT id FROM prebuilt_ids WHERE name IN ('Radeon Warrior', 'Aurora i5') LIMIT 1)
                ELSE (SELECT id FROM prebuilt_ids WHERE name IN ('Starter Pro', 'Essential Gaming') LIMIT 1)
            END
        ELSE NULL
    END as prebuilt_pc_id,
    CASE 
        WHEN o.order_type = 'custom' THEN
            CASE 
                WHEN o.total > 3000 THEN (SELECT id FROM part_ids WHERE name LIKE '%4090%' LIMIT 1)
                WHEN o.total > 2500 THEN (SELECT id FROM part_ids WHERE name LIKE '%4080%' LIMIT 1)
                WHEN o.total > 2000 THEN (SELECT id FROM part_ids WHERE name LIKE '%4070%' LIMIT 1)
                ELSE (SELECT id FROM part_ids WHERE name LIKE '%7600%' LIMIT 1)
            END
        ELSE NULL
    END as pc_part_id,
    1 as quantity,
    o.total as price
FROM order_ids o;

-- For custom builds, add additional components
INSERT INTO order_items (order_id, prebuilt_pc_id, pc_part_id, quantity, price)
SELECT 
    o.id as order_id,
    NULL as prebuilt_pc_id,
    p.id as pc_part_id,
    1 as quantity,
    p.price as price
FROM orders o
CROSS JOIN LATERAL (
    SELECT id, price, category
    FROM pc_parts
    WHERE category IN ('CPU', 'Motherboard', 'RAM', 'Storage', 'PSU', 'Case', 'Cooling')
    AND CASE 
        WHEN o.total > 3000 THEN price > 300
        WHEN o.total > 2000 THEN price > 200
        ELSE price > 100
    END
    LIMIT 1
) p
WHERE o.order_type = 'custom';

-- Add thousands more order items as needed

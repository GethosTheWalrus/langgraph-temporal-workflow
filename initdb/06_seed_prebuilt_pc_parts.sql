-- Populate pre-built PC parts (many-to-many)
INSERT INTO prebuilt_pc_parts (prebuilt_pc_id, pc_part_id, quantity) VALUES
(1, 1, 1), -- Gamer Xtreme: Intel i9
(1, 3, 1), -- Gamer Xtreme: RTX 4090
(1, 5, 2), -- Gamer Xtreme: 32GB RAM
(1, 8, 1), -- Gamer Xtreme: ASUS MB
(1, 10, 1), -- Gamer Xtreme: Corsair PSU
(2, 2, 1), -- Creator Studio: Ryzen 9
(2, 4, 1), -- Creator Studio: RX 7900 XTX
(2, 5, 2), -- Creator Studio: 32GB RAM
(2, 9, 1), -- Creator Studio: MSI MB
(2, 10, 1), -- Creator Studio: Corsair PSU
(3, 1, 1), -- Budget Builder: Intel i9
(3, 7, 1), -- Budget Builder: Seagate HDD
(3, 5, 1), -- Budget Builder: 32GB RAM
(3, 8, 1), -- Budget Builder: ASUS MB
(4, 2, 1), -- Mini ITX Beast: Ryzen 9
(4, 3, 1), -- Mini ITX Beast: RTX 4090
(4, 6, 1), -- Mini ITX Beast: Samsung SSD
(4, 9, 1), -- Mini ITX Beast: MSI MB
(5, 1, 1), -- Silent Pro: Intel i9
(5, 5, 2), -- Silent Pro: 32GB RAM
(5, 8, 1); -- Silent Pro: ASUS MB

-- Add thousands more prebuilt_pc_parts as needed

-- Only run this script when executed from Docker entrypoint
DO $$
BEGIN
    -- Check if this is being run from Docker entrypoint
    IF current_setting('POSTGRES_DB', true) IS NOT NULL THEN
        -- Delete any existing entries to prevent duplicates
        DELETE FROM prebuilt_pc_parts;

        -- Create a temporary table for staging the matches
        CREATE TEMPORARY TABLE IF NOT EXISTS temp_prebuilt_matches (
            prebuilt_pc_id INTEGER,
            pc_part_id INTEGER,
            category VARCHAR(50),
            PRIMARY KEY (prebuilt_pc_id, pc_part_id)
        );

        -- Clear the temporary table if it exists
        TRUNCATE temp_prebuilt_matches;

        -- Insert matches into temporary table
        INSERT INTO temp_prebuilt_matches (prebuilt_pc_id, pc_part_id, category)
        SELECT DISTINCT ON (p.id, pt.category)
            p.id as prebuilt_pc_id,
            pt.id as pc_part_id,
            pt.category
        FROM prebuilt_pcs p
        CROSS JOIN pc_parts pt
        WHERE 
            -- Titan X Pro
            (p.name = 'Titan X Pro' AND (
                (pt.name LIKE '%14900K%' AND pt.category = 'CPU') OR
                (pt.name LIKE '%4090%' AND pt.category = 'GPU') OR
                (pt.name LIKE '%Maximus Z790%' AND pt.category = 'Motherboard') OR
                (pt.name LIKE '%Dominator%64GB%' AND pt.category = 'RAM') OR
                (pt.name LIKE '%T700 4TB%' AND pt.category = 'Storage') OR
                (pt.name LIKE '%HX1500i%' AND pt.category = 'PSU') OR
                (pt.name LIKE '%O11 Dynamic%' AND pt.category = 'Case') OR
                (pt.name LIKE '%Liquid Freezer II 360%' AND pt.category = 'Cooling') OR
                (pt.name LIKE '%UNI Fan%' AND pt.category = 'Fans')
            ))
            OR
            -- Phoenix AMD Edition
            (p.name = 'Phoenix AMD Edition' AND (
                (pt.name LIKE '%7950X3D%' AND pt.category = 'CPU') OR
                (pt.name LIKE '%7900 XTX%' AND pt.category = 'GPU') OR
                (pt.name LIKE '%STRIX X670E%' AND pt.category = 'Motherboard') OR
                (pt.name LIKE '%Trident Z5%32GB%' AND pt.category = 'RAM') OR
                (pt.name LIKE '%990 PRO 2TB%' AND pt.category = 'Storage') OR
                (pt.name LIKE '%Dark Power 13%' AND pt.category = 'PSU') OR
                (pt.name LIKE '%Torrent%' AND pt.category = 'Case') OR
                (pt.name LIKE '%Galahad AIO%' AND pt.category = 'Cooling') OR
                (pt.name LIKE '%NF-A12x25%' AND pt.category = 'Fans')
            ))
            OR
            -- Nova RTX 4080
            (p.name = 'Nova RTX 4080' AND (
                (pt.name LIKE '%14700K%' AND pt.category = 'CPU') OR
                (pt.name LIKE '%4080 SUPER%' AND pt.category = 'GPU') OR
                (pt.name LIKE '%MPG Z790%' AND pt.category = 'Motherboard') OR
                (pt.name LIKE '%Trident Z5%32GB%' AND pt.category = 'RAM') OR
                (pt.name LIKE '%SN850X%' AND pt.category = 'Storage') OR
                (pt.name LIKE '%SuperNOVA 850%' AND pt.category = 'PSU') OR
                (pt.name LIKE '%5000D%' AND pt.category = 'Case') OR
                (pt.name LIKE '%NH-D15%' AND pt.category = 'Cooling') OR
                (pt.name LIKE '%P12%' AND pt.category = 'Fans')
            ))
            OR
            -- Stellar Gaming Pro
            (p.name = 'Stellar Gaming Pro' AND (
                (pt.name LIKE '%14600K%' AND pt.category = 'CPU') OR
                (pt.name LIKE '%4070 Ti SUPER%' AND pt.category = 'GPU') OR
                (pt.name LIKE '%MPG Z790%' AND pt.category = 'Motherboard') OR
                (pt.name LIKE '%Crucial%32GB%' AND pt.category = 'RAM') OR
                (pt.name LIKE '%SN850X%' AND pt.category = 'Storage') OR
                (pt.name LIKE '%SuperNOVA 850%' AND pt.category = 'PSU') OR
                (pt.name LIKE '%5000D%' AND pt.category = 'Case') OR
                (pt.name LIKE '%NH-D15%' AND pt.category = 'Cooling') OR
                (pt.name LIKE '%P12%' AND pt.category = 'Fans')
            ))
            OR
            -- Radeon Warrior
            (p.name = 'Radeon Warrior' AND (
                (pt.name LIKE '%7800X3D%' AND pt.category = 'CPU') OR
                (pt.name LIKE '%7800 XT%' AND pt.category = 'GPU') OR
                (pt.name LIKE '%B650 TOMAHAWK%' AND pt.category = 'Motherboard') OR
                (pt.name LIKE '%Crucial%32GB%' AND pt.category = 'RAM') OR
                (pt.name LIKE '%990 PRO%' AND pt.category = 'Storage') OR
                (pt.name LIKE '%SuperNOVA 850%' AND pt.category = 'PSU') OR
                (pt.name LIKE '%5000D%' AND pt.category = 'Case') OR
                (pt.name LIKE '%Galahad AIO%' AND pt.category = 'Cooling') OR
                (pt.name LIKE '%P12%' AND pt.category = 'Fans')
            ))
        ORDER BY p.id, pt.category, pt.id;

        -- Insert from temporary table to final table
        INSERT INTO prebuilt_pc_parts (prebuilt_pc_id, pc_part_id, quantity)
        SELECT 
            prebuilt_pc_id,
            pc_part_id,
            CASE category
                WHEN 'Fans' THEN 3  -- Most cases need multiple fans
                ELSE 1
            END as quantity
        FROM temp_prebuilt_matches;

        -- Clean up
        DROP TABLE IF EXISTS temp_prebuilt_matches;
    END IF;
END;
$$;

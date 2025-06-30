-- Populate cart items
INSERT INTO cart_items (cart_id, prebuilt_pc_id, pc_part_id, quantity) VALUES
(1, 2, NULL, 1),
(1, NULL, 4, 2),
(2, 3, NULL, 1),
(3, NULL, 5, 1),
(4, NULL, 6, 1),
(5, 1, NULL, 1);

-- Add thousands more cart items as needed

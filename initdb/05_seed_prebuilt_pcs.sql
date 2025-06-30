-- Populate prebuilt PCs
INSERT INTO prebuilt_pcs (name, description, price, stock, image_url, created_at) VALUES
-- High-end Gaming PCs
('Titan X Pro', 'Ultimate gaming and content creation PC featuring RTX 4090 and Intel i9-14900K', 4299.99, 15, 'https://cdn.mcp.com/prebuilt/titan-x-pro.jpg', NOW()),
('Phoenix AMD Edition', 'High-performance AMD gaming rig with RX 7900 XTX and Ryzen 9 7950X3D', 3799.99, 20, 'https://cdn.mcp.com/prebuilt/phoenix-amd.jpg', NOW()),
('Nova RTX 4080', 'Premium gaming experience with RTX 4080 SUPER and Intel i7-14700K', 2999.99, 25, 'https://cdn.mcp.com/prebuilt/nova-rtx.jpg', NOW()),

-- Mid-range Gaming PCs
('Stellar Gaming Pro', 'Great 1440p gaming with RTX 4070 Ti SUPER and Intel i5-14600K', 2199.99, 30, 'https://cdn.mcp.com/prebuilt/stellar-gaming.jpg', NOW()),
('Radeon Warrior', 'Excellent price-performance with RX 7800 XT and Ryzen 7 7800X3D', 1899.99, 35, 'https://cdn.mcp.com/prebuilt/radeon-warrior.jpg', NOW()),
('Aurora i5', 'Reliable 1080p gaming with RTX 4060 Ti and Intel i5-13600K', 1499.99, 40, 'https://cdn.mcp.com/prebuilt/aurora-i5.jpg', NOW()),

-- Budget Gaming PCs
('Starter Pro', 'Great entry-level gaming with RX 7600 and Ryzen 5 7600X', 999.99, 50, 'https://cdn.mcp.com/prebuilt/starter-pro.jpg', NOW()),
('Essential Gaming', 'Affordable 1080p gaming with RTX 4060 and Intel i5-13400F', 899.99, 60, 'https://cdn.mcp.com/prebuilt/essential-gaming.jpg', NOW()),

-- Workstation PCs
('Creator Pro Max', 'Professional workstation with RTX 4090 and i9-14900K', 4499.99, 10, 'https://cdn.mcp.com/prebuilt/creator-pro-max.jpg', NOW()),
('Render Master', 'Rendering powerhouse with RX 7900 XTX and Ryzen 9 7950X3D', 3999.99, 12, 'https://cdn.mcp.com/prebuilt/render-master.jpg', NOW());

-- Add thousands more pre-built PCs as needed

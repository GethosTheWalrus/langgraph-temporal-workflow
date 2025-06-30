-- Populate PC parts with realistic current market data
INSERT INTO pc_parts (name, description, category, price, stock, image_url, created_at) VALUES
-- CPUs
('Intel Core i9-14900K', '24 Cores (8P+16E), 32 Threads, Up to 6.0GHz, DDR5 Support', 'CPU', 569.99, 75, 'https://cdn.mcp.com/parts/cpu/14900k.jpg', NOW()),
('Intel Core i7-14700K', '20 Cores (8P+12E), 28 Threads, Up to 5.6GHz, DDR5 Support', 'CPU', 409.99, 100, 'https://cdn.mcp.com/parts/cpu/14700k.jpg', NOW()),
('Intel Core i5-14600K', '14 Cores (6P+8E), 20 Threads, Up to 5.3GHz, DDR5 Support', 'CPU', 319.99, 150, 'https://cdn.mcp.com/parts/cpu/14600k.jpg', NOW()),
('AMD Ryzen 9 7950X3D', '16 Cores, 32 Threads, Up to 5.7GHz, 144MB Cache', 'CPU', 649.99, 60, 'https://cdn.mcp.com/parts/cpu/7950x3d.jpg', NOW()),
('AMD Ryzen 7 7800X3D', '8 Cores, 16 Threads, Up to 5.0GHz, 104MB Cache', 'CPU', 449.99, 85, 'https://cdn.mcp.com/parts/cpu/7800x3d.jpg', NOW()),
('AMD Ryzen 5 7600X', '6 Cores, 12 Threads, Up to 5.3GHz, AM5 Socket', 'CPU', 249.99, 120, 'https://cdn.mcp.com/parts/cpu/7600x.jpg', NOW()),

-- GPUs
('NVIDIA GeForce RTX 4090', '24GB GDDR6X, 2.52GHz, DLSS 3, Ray Tracing', 'GPU', 1599.99, 40, 'https://cdn.mcp.com/parts/gpu/rtx4090.jpg', NOW()),
('NVIDIA GeForce RTX 4080 SUPER', '16GB GDDR6X, 2.55GHz, DLSS 3.5', 'GPU', 999.99, 65, 'https://cdn.mcp.com/parts/gpu/rtx4080s.jpg', NOW()),
('NVIDIA GeForce RTX 4070 Ti SUPER', '16GB GDDR6X, 2.61GHz, Great 1440p Performance', 'GPU', 799.99, 80, 'https://cdn.mcp.com/parts/gpu/rtx4070tis.jpg', NOW()),
('AMD Radeon RX 7900 XTX', '24GB GDDR6, 2.5GHz, FSR 3', 'GPU', 949.99, 55, 'https://cdn.mcp.com/parts/gpu/rx7900xtx.jpg', NOW()),
('AMD Radeon RX 7800 XT', '16GB GDDR6, 2.43GHz, Great 1440p Value', 'GPU', 549.99, 90, 'https://cdn.mcp.com/parts/gpu/rx7800xt.jpg', NOW()),
('AMD Radeon RX 7600', '8GB GDDR6, 2.25GHz, Excellent 1080p Performance', 'GPU', 269.99, 110, 'https://cdn.mcp.com/parts/gpu/rx7600.jpg', NOW()),

-- Motherboards
('ASUS ROG Maximus Z790 Hero', 'Intel LGA 1700, DDR5, PCIe 5.0, WiFi 6E', 'Motherboard', 629.99, 45, 'https://cdn.mcp.com/parts/mb/maximus-z790.jpg', NOW()),
('MSI MPG Z790 Edge WiFi', 'Intel LGA 1700, DDR5, PCIe 5.0, 2.5GbE LAN', 'Motherboard', 369.99, 70, 'https://cdn.mcp.com/parts/mb/mpg-z790.jpg', NOW()),
('ASUS ROG STRIX X670E-E', 'AMD AM5, DDR5, PCIe 5.0, WiFi 6E', 'Motherboard', 499.99, 55, 'https://cdn.mcp.com/parts/mb/strix-x670e.jpg', NOW()),
('MSI MAG B650 TOMAHAWK', 'AMD AM5, DDR5, PCIe 4.0, 2.5GbE LAN', 'Motherboard', 259.99, 85, 'https://cdn.mcp.com/parts/mb/mag-b650.jpg', NOW()),

-- RAM
('G.SKILL Trident Z5 RGB 32GB', 'DDR5-6400 CL32 (2x16GB), Samsung B-die', 'RAM', 189.99, 100, 'https://cdn.mcp.com/parts/ram/trident-z5-32.jpg', NOW()),
('Corsair Dominator Platinum 64GB', 'DDR5-6000 CL30 (2x32GB), RGB', 'RAM', 339.99, 60, 'https://cdn.mcp.com/parts/ram/dominator-64.jpg', NOW()),
('Crucial RAM 32GB', 'DDR5-5600 CL36 (2x16GB), Value Performance', 'RAM', 134.99, 150, 'https://cdn.mcp.com/parts/ram/crucial-32.jpg', NOW()),

-- Storage
('Samsung 990 PRO 2TB', 'PCIe 4.0 NVMe, 7450/6900 MB/s', 'Storage', 189.99, 120, 'https://cdn.mcp.com/parts/storage/990pro-2tb.jpg', NOW()),
('WD Black SN850X 1TB', 'PCIe 4.0 NVMe, 7300/6300 MB/s', 'Storage', 129.99, 140, 'https://cdn.mcp.com/parts/storage/sn850x-1tb.jpg', NOW()),
('Crucial T700 4TB', 'PCIe 5.0 NVMe, 12400/11800 MB/s', 'Storage', 449.99, 45, 'https://cdn.mcp.com/parts/storage/t700-4tb.jpg', NOW()),
('Seagate IronWolf Pro 18TB', '3.5" NAS HDD, 7200 RPM, CMR', 'Storage', 349.99, 70, 'https://cdn.mcp.com/parts/storage/ironwolf-18tb.jpg', NOW()),

-- Power Supplies
('Corsair HX1500i', '1500W 80+ Platinum, Full Modular, ATX 3.0', 'PSU', 399.99, 50, 'https://cdn.mcp.com/parts/psu/hx1500i.jpg', NOW()),
('be quiet! Dark Power 13', '1000W 80+ Titanium, Full Modular, ATX 3.0', 'PSU', 329.99, 65, 'https://cdn.mcp.com/parts/psu/dark-power-13.jpg', NOW()),
('EVGA SuperNOVA 850 G7', '850W 80+ Gold, Full Modular, ATX 3.0', 'PSU', 149.99, 95, 'https://cdn.mcp.com/parts/psu/supernova-850-g7.jpg', NOW()),

-- Cases
('Lian Li O11 Dynamic EVO', 'Mid Tower, Excellent Airflow, Tool-free Design', 'Case', 169.99, 80, 'https://cdn.mcp.com/parts/case/o11-evo.jpg', NOW()),
('Fractal Design Torrent', 'High Airflow, Unique Design, E-ATX Support', 'Case', 189.99, 60, 'https://cdn.mcp.com/parts/case/torrent.jpg', NOW()),
('Corsair 5000D Airflow', 'Mid Tower, High Airflow, Great Cable Management', 'Case', 174.99, 75, 'https://cdn.mcp.com/parts/case/5000d.jpg', NOW()),

-- Cooling
('ARCTIC Liquid Freezer II 360', '360mm AIO, LGA 1700 & AM5 Compatible', 'Cooling', 159.99, 85, 'https://cdn.mcp.com/parts/cooling/liquid-freezer-360.jpg', NOW()),
('Noctua NH-D15 chromax.black', 'Dual Tower Air Cooler, All Black Design', 'Cooling', 109.99, 100, 'https://cdn.mcp.com/parts/cooling/nh-d15-black.jpg', NOW()),
('Lian Li Galahad AIO 240', '240mm AIO, RGB, High Performance', 'Cooling', 129.99, 90, 'https://cdn.mcp.com/parts/cooling/galahad-240.jpg', NOW()),

-- Case Fans
('Noctua NF-A12x25', '120mm Premium Quiet Fan, Brown', 'Fans', 29.99, 200, 'https://cdn.mcp.com/parts/fans/nf-a12x25.jpg', NOW()),
('Lian Li UNI Fan SL120', '120mm RGB Fan, Daisy Chain Design', 'Fans', 24.99, 300, 'https://cdn.mcp.com/parts/fans/uni-fan-sl120.jpg', NOW()),
('Arctic P12 PWM PST', '120mm Value Performance Fan, 5-Pack', 'Fans', 39.99, 150, 'https://cdn.mcp.com/parts/fans/p12-5pack.jpg', NOW());

-- Add hundreds more parts for a truly large catalog

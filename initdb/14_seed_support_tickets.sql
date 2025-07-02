-- Populate customer support tickets with realistic retention scenarios
INSERT INTO customer_support_tickets (
    user_id, order_id, subject, description, category, priority, status, 
    assigned_to, resolution_notes, satisfaction_rating, created_at, resolved_at, updated_at
) VALUES

-- High-priority shipping issues (retention critical)
(
    5, -- david_jones (at_risk customer)
    (SELECT id FROM orders WHERE user_id = 5 ORDER BY created_at DESC LIMIT 1),
    'PC Build Delayed - Missing GPU Component',
    'My custom PC build order has been delayed for over 3 weeks due to a missing RTX 4090 GPU. This was supposed to be delivered for a major gaming tournament I am participating in. I am extremely frustrated and considering cancelling my order and going with a competitor.',
    'shipping', 'urgent', 'open',
    'support_manager_sarah', NULL, NULL,
    NOW() - INTERVAL '3 days',
    NULL,
    NOW() - INTERVAL '3 days'
),

-- Product quality issues
(
    2, -- sarah_smith 
    (SELECT id FROM orders WHERE user_id = 2 ORDER BY created_at DESC LIMIT 1),
    'Workstation PC Overheating Issues',
    'The workstation PC I received 2 weeks ago is experiencing severe overheating issues during video rendering tasks. CPU temperatures are reaching 90°C+ under load. This is affecting my freelance video editing business productivity.',
    'product_defect', 'high', 'in_progress',
    'tech_support_mike', 'Investigating cooling system. May need to arrange RMA for faulty AIO cooler.', NULL,
    NOW() - INTERVAL '5 days',
    NULL,
    NOW() - INTERVAL '1 day'
),

-- Billing disputes
(
    10, -- jennifer_lopez (at_risk customer)
    (SELECT id FROM orders WHERE user_id = 10 ORDER BY created_at DESC LIMIT 1),
    'Incorrect Billing - Charged for Parts Not Received',
    'I was charged $450 for RAM upgrade that was never included in my shipment. I have been trying to resolve this for 2 weeks through customer service but keep getting transferred between departments. I am considering disputing this charge with my credit card company.',
    'billing', 'high', 'open',
    'billing_specialist_anna', NULL, NULL,
    NOW() - INTERVAL '8 days',
    NULL,
    NOW() - INTERVAL '2 days'
),

-- Resolved issues with satisfaction ratings
(
    1, -- john_doe (vip customer)
    (SELECT id FROM orders WHERE user_id = 1 ORDER BY created_at DESC LIMIT 1),
    'Gaming PC Performance Below Expectations',
    'My new gaming rig is not achieving the FPS numbers promised for 4K gaming. Getting 45-50 FPS in Cyberpunk 2077 instead of the advertised 60+ FPS.',
    'technical_support', 'medium', 'resolved',
    'tech_support_alex', 'Identified GPU driver optimization issue. Provided custom driver configuration and game settings optimization guide. Customer now achieving 65+ FPS as expected.', 5,
    NOW() - INTERVAL '12 days',
    NOW() - INTERVAL '8 days',
    NOW() - INTERVAL '8 days'
),

-- Multiple tickets for problematic customer
(
    11, -- alex_chen (churned customer)
    NULL, -- No specific order
    'Repeated Hardware Failures',
    'This is my fourth support ticket in 2 months. First the motherboard died, then the PSU failed, now the SSD is corrupted. I am losing confidence in your quality control processes.',
    'product_defect', 'high', 'resolved',
    'support_manager_sarah', 'Offered full system replacement with upgraded components as goodwill gesture. Customer declined and requested refund.', 2,
    NOW() - INTERVAL '180 days',
    NOW() - INTERVAL '175 days',
    NOW() - INTERVAL '175 days'
),

-- Minor issues that were quickly resolved
(
    3, -- mike_wilson 
    (SELECT id FROM orders WHERE user_id = 3 ORDER BY created_at DESC LIMIT 1),
    'USB Ports Not Working on Front Panel',
    'The front USB ports on my new PC case are not functioning. Rear ports work fine.',
    'technical_support', 'low', 'resolved',
    'tech_support_jenny', 'Front panel USB connector was not properly seated on motherboard. Provided troubleshooting guide. Customer resolved issue successfully.', 4,
    NOW() - INTERVAL '18 days',
    NOW() - INTERVAL '16 days',
    NOW() - INTERVAL '16 days'
),

-- Shipping delays but good customer service
(
    7, -- james_anderson (vip customer)
    (SELECT id FROM orders WHERE user_id = 7 ORDER BY created_at DESC LIMIT 1),
    'Express Shipping Delay Due to Weather',
    'My express shipment was delayed due to storm conditions. Understand its not your fault but needed update on delivery timeline.',
    'shipping', 'low', 'resolved',
    'customer_service_maria', 'Provided tracking updates and expedited processing once weather cleared. Offered shipping cost refund as courtesy.', 5,
    NOW() - INTERVAL '25 days',
    NOW() - INTERVAL '23 days',
    NOW() - INTERVAL '23 days'
),

-- Recent high-priority ticket that needs immediate attention
(
    4, -- emily_brown
    (SELECT id FROM orders WHERE user_id = 4 ORDER BY created_at DESC LIMIT 1),
    'Complete System Failure After 1 Week',
    'My budget gaming PC completely stopped working after just 1 week. Blue screen errors, random shutdowns, and now it wont even POST. As a college student, I saved for months to afford this PC and need it for my computer science coursework.',
    'product_defect', 'urgent', 'open',
    'tech_support_mike', NULL, NULL,
    NOW() - INTERVAL '1 day',
    NULL,
    NOW() - INTERVAL '1 day'
); 
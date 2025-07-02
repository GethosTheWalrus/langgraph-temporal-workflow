-- Production-ready schema for a custom PC building ecommerce site
-- Enhanced with customer intelligence and retention management capabilities

-- Users table (enhanced for customer intelligence)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Personal information for customer intelligence
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    date_of_birth DATE,
    
    -- Customer segmentation and preferences
    customer_segment VARCHAR(50) DEFAULT 'general', -- 'gaming', 'workstation', 'budget', 'enthusiast'
    preferred_contact_method VARCHAR(20) DEFAULT 'email', -- 'email', 'phone', 'sms'
    marketing_opt_in BOOLEAN DEFAULT false,
    
    -- Retention tracking
    customer_status VARCHAR(20) DEFAULT 'active', -- 'active', 'at_risk', 'churned', 'vip'
    lifetime_value NUMERIC(10,2) DEFAULT 0.0,
    last_engagement_date TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Addresses table
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PC Parts table
CREATE TABLE IF NOT EXISTS pc_parts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL, -- e.g., CPU, GPU, RAM, etc.
    price NUMERIC(10,2) NOT NULL,
    stock INTEGER NOT NULL,
    image_url VARCHAR(255),
    brand VARCHAR(50),
    performance_tier VARCHAR(20), -- 'budget', 'mid-range', 'high-end', 'enthusiast'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pre-built PCs table
CREATE TABLE IF NOT EXISTS prebuilt_pcs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL,
    stock INTEGER NOT NULL,
    image_url VARCHAR(255),
    use_case VARCHAR(50), -- 'gaming', 'workstation', 'office', 'streaming'
    performance_tier VARCHAR(20), -- 'budget', 'mid-range', 'high-end', 'enthusiast'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pre-built PC Parts (many-to-many)
CREATE TABLE IF NOT EXISTS prebuilt_pc_parts (
    prebuilt_pc_id INTEGER REFERENCES prebuilt_pcs(id) ON DELETE CASCADE,
    pc_part_id INTEGER REFERENCES pc_parts(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (prebuilt_pc_id, pc_part_id)
);

-- Orders table (enhanced for better analytics)
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    address_id INTEGER REFERENCES addresses(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL, -- e.g., pending, paid, shipped, delivered, cancelled
    total NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    tax_amount NUMERIC(10,2) DEFAULT 0.0,
    shipping_cost NUMERIC(10,2) DEFAULT 0.0,
    discount_amount NUMERIC(10,2) DEFAULT 0.0,
    order_type VARCHAR(20) NOT NULL, -- 'prebuilt' or 'custom'
    
    -- Enhanced tracking for customer intelligence
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Alias for created_at for compatibility
    delivery_date TIMESTAMP,
    estimated_delivery_date TIMESTAMP,
    shipping_method VARCHAR(50),
    order_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    prebuilt_pc_id INTEGER REFERENCES prebuilt_pcs(id) ON DELETE SET NULL,
    pc_part_id INTEGER REFERENCES pc_parts(id) ON DELETE SET NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    total_price NUMERIC(10,2) NOT NULL
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    payment_method VARCHAR(50) NOT NULL, -- e.g., credit_card, paypal
    payment_status VARCHAR(50) NOT NULL, -- e.g., pending, completed, failed
    amount NUMERIC(10,2) NOT NULL,
    transaction_id VARCHAR(100),
    payment_processor VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Tracking table (enhanced)
CREATE TABLE IF NOT EXISTS order_tracking (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL, -- e.g., shipped, in_transit, delivered
    location VARCHAR(100),
    tracking_number VARCHAR(100),
    carrier VARCHAR(50),
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cart table
CREATE TABLE IF NOT EXISTS carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cart Items table
CREATE TABLE IF NOT EXISTS cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
    prebuilt_pc_id INTEGER REFERENCES prebuilt_pcs(id) ON DELETE SET NULL,
    pc_part_id INTEGER REFERENCES pc_parts(id) ON DELETE SET NULL,
    quantity INTEGER NOT NULL
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    prebuilt_pc_id INTEGER REFERENCES prebuilt_pcs(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    review_status VARCHAR(20) DEFAULT 'active', -- 'active', 'hidden', 'flagged'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NEW: Customer Support Tickets (for retention analysis)
CREATE TABLE IF NOT EXISTS customer_support_tickets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50), -- 'shipping', 'product_defect', 'billing', 'technical_support'
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'in_progress', 'resolved', 'closed'
    assigned_to VARCHAR(100),
    resolution_notes TEXT,
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NEW: Customer Communications (track retention efforts)
CREATE TABLE IF NOT EXISTS customer_communications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    communication_type VARCHAR(50) NOT NULL, -- 'email', 'phone', 'sms', 'in_app'
    subject VARCHAR(200),
    content TEXT,
    direction VARCHAR(10) NOT NULL, -- 'inbound', 'outbound'
    status VARCHAR(20) DEFAULT 'sent', -- 'sent', 'delivered', 'opened', 'clicked', 'replied'
    campaign_type VARCHAR(50), -- 'retention', 'promotional', 'support', 'survey'
    sent_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NEW: Customer Preferences (for personalization)
CREATE TABLE IF NOT EXISTS customer_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    preference_type VARCHAR(50) NOT NULL, -- 'pc_use_case', 'budget_range', 'brand_preference'
    preference_value VARCHAR(100) NOT NULL,
    confidence_score NUMERIC(3,2) DEFAULT 0.5, -- 0.0 to 1.0
    source VARCHAR(50), -- 'survey', 'purchase_history', 'browsing_behavior'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NEW: Retention Cases (track retention workflow results)
CREATE TABLE IF NOT EXISTS retention_cases (
    id VARCHAR(100) PRIMARY KEY, -- case_id from workflow
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    support_ticket_id INTEGER REFERENCES customer_support_tickets(id) ON DELETE SET NULL,
    case_status VARCHAR(20) DEFAULT 'active', -- 'active', 'resolved', 'failed'
    urgency_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    estimated_value NUMERIC(10,2) DEFAULT 0.0,
    actual_retention_cost NUMERIC(10,2) DEFAULT 0.0,
    customer_retained BOOLEAN,
    retention_strategy_used TEXT,
    case_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_customer_segment ON users(customer_segment);
CREATE INDEX IF NOT EXISTS idx_users_customer_status ON users(customer_status);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_support_tickets_user_id ON customer_support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON customer_support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_communications_user_id ON customer_communications(user_id);
CREATE INDEX IF NOT EXISTS idx_retention_cases_user_id ON retention_cases(user_id);

-- Views for easier querying
CREATE OR replace VIEW customer_summary AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.first_name,
    u.last_name,
    u.customer_segment,
    u.customer_status,
    u.lifetime_value,
    u.created_at as customer_since,
    COUNT(o.id) as total_orders,
    COALESCE(SUM(o.total), 0) as total_spent,
    MAX(o.order_date) as last_order_date,
    COUNT(cs.id) as support_tickets_count,
    COUNT(CASE WHEN cs.status = 'open' THEN 1 END) as open_tickets
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN customer_support_tickets cs ON u.id = cs.user_id
GROUP BY u.id, u.username, u.email, u.first_name, u.last_name, 
         u.customer_segment, u.customer_status, u.lifetime_value, u.created_at;

-- Populate customer preferences for personalized retention strategies
INSERT INTO customer_preferences (
    user_id, preference_type, preference_value, confidence_score, source, created_at, updated_at
) VALUES

-- Gaming enthusiasts preferences
(1, 'pc_use_case', 'competitive_gaming', 0.95, 'purchase_history', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(1, 'budget_range', 'high_end', 0.90, 'purchase_history', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(1, 'brand_preference', 'nvidia_gpu', 0.85, 'purchase_history', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(1, 'performance_priority', 'fps_over_aesthetics', 0.88, 'browsing_behavior', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),

(5, 'pc_use_case', 'competitive_gaming', 0.92, 'purchase_history', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(5, 'budget_range', 'mid_range', 0.85, 'purchase_history', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(5, 'brand_preference', 'amd_cpu', 0.75, 'purchase_history', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(5, 'upgrade_frequency', 'yearly', 0.70, 'browsing_behavior', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),

(9, 'pc_use_case', 'casual_gaming', 0.80, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),
(9, 'budget_range', 'mid_range', 0.85, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),
(9, 'brand_preference', 'intel_cpu', 0.65, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),

-- Workstation users preferences
(2, 'pc_use_case', 'video_editing', 0.95, 'purchase_history', NOW() - INTERVAL '4 months', NOW() - INTERVAL '3 months'),
(2, 'budget_range', 'high_end', 0.90, 'purchase_history', NOW() - INTERVAL '4 months', NOW() - INTERVAL '3 months'),
(2, 'brand_preference', 'nvidia_professional', 0.88, 'purchase_history', NOW() - INTERVAL '4 months', NOW() - INTERVAL '3 months'),
(2, 'performance_priority', 'rendering_speed', 0.92, 'browsing_behavior', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(2, 'memory_requirement', 'high_capacity', 0.85, 'purchase_history', NOW() - INTERVAL '4 months', NOW() - INTERVAL '3 months'),

(6, 'pc_use_case', 'cad_design', 0.90, 'purchase_history', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(6, 'budget_range', 'high_end', 0.88, 'purchase_history', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(6, 'brand_preference', 'nvidia_professional', 0.85, 'purchase_history', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),

(10, 'pc_use_case', 'content_creation', 0.85, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),
(10, 'budget_range', 'mid_range', 0.80, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),
(10, 'performance_priority', 'multitasking', 0.75, 'browsing_behavior', NOW() - INTERVAL '3 weeks', NOW() - INTERVAL '1 week'),

-- Enthusiast preferences
(3, 'pc_use_case', 'enthusiast_gaming', 0.95, 'purchase_history', NOW() - INTERVAL '4 months', NOW() - INTERVAL '3 months'),
(3, 'budget_range', 'enthusiast', 0.92, 'purchase_history', NOW() - INTERVAL '4 months', NOW() - INTERVAL '3 months'),
(3, 'brand_preference', 'high_end_components', 0.90, 'purchase_history', NOW() - INTERVAL '4 months', NOW() - INTERVAL '3 months'),
(3, 'upgrade_frequency', 'bi_yearly', 0.85, 'browsing_behavior', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(3, 'cooling_preference', 'custom_loop', 0.80, 'browsing_behavior', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),

(7, 'pc_use_case', 'enthusiast_gaming', 0.98, 'purchase_history', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(7, 'budget_range', 'no_limit', 0.95, 'purchase_history', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(7, 'brand_preference', 'premium_only', 0.92, 'purchase_history', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(7, 'performance_priority', 'cutting_edge', 0.90, 'browsing_behavior', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),

-- Budget-conscious users preferences
(4, 'pc_use_case', 'student_workstation', 0.90, 'purchase_history', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(4, 'budget_range', 'budget', 0.95, 'purchase_history', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(4, 'brand_preference', 'value_oriented', 0.85, 'purchase_history', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(4, 'performance_priority', 'price_performance', 0.88, 'browsing_behavior', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(4, 'upgrade_frequency', 'as_needed', 0.80, 'browsing_behavior', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),

(8, 'pc_use_case', 'general_use', 0.85, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),
(8, 'budget_range', 'budget', 0.90, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),
(8, 'brand_preference', 'reliable_brands', 0.75, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),

(12, 'pc_use_case', 'basic_computing', 0.80, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),
(12, 'budget_range', 'budget', 0.88, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),
(12, 'brand_preference', 'cost_effective', 0.70, 'purchase_history', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),

-- Communication preferences
(1, 'contact_preference', 'email_detailed', 0.85, 'survey', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(2, 'contact_preference', 'phone_immediate', 0.90, 'survey', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(3, 'contact_preference', 'email_technical', 0.88, 'survey', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(5, 'contact_preference', 'sms_updates', 0.80, 'survey', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(7, 'contact_preference', 'phone_vip', 0.95, 'survey', NOW() - INTERVAL '1 month', NOW() - INTERVAL '2 weeks'),

-- Shopping behavior preferences
(1, 'shopping_behavior', 'research_heavy', 0.85, 'browsing_behavior', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(2, 'shopping_behavior', 'spec_focused', 0.90, 'browsing_behavior', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(3, 'shopping_behavior', 'early_adopter', 0.88, 'browsing_behavior', NOW() - INTERVAL '3 months', NOW() - INTERVAL '2 months'),
(4, 'shopping_behavior', 'price_comparison', 0.92, 'browsing_behavior', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'),
(5, 'shopping_behavior', 'brand_loyal', 0.75, 'browsing_behavior', NOW() - INTERVAL '2 months', NOW() - INTERVAL '1 month'); 
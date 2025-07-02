"""
Customer intelligence tools for retention workflows.

These tools provide specialized customer analysis capabilities including
profile analysis, lifetime value calculation, behavior patterns, and risk scoring.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import asyncpg
from temporalio import activity
from langchain_core.tools import tool


def create_customer_intelligence_tools(db_config: dict):
    """
    Factory function that creates customer intelligence tools configured with database.
    
    Args:
        db_config: Dictionary containing database connection parameters
    
    Returns:
        List of configured customer intelligence tools
    """
    
    @tool
    async def get_customer_profile(customer_id: int) -> Dict[str, Any]:
        """
        Get comprehensive customer profile with basic information and statistics.
        
        Args:
            customer_id: ID of the customer to analyze
            
        Returns:
            Dictionary with customer profile data
        """
        try:
            conn = await asyncio.wait_for(asyncpg.connect(**db_config), timeout=10.0)
            
            try:
                # Get basic customer info
                customer_query = """
                    SELECT 
                        u.id,
                        u.username,
                        u.first_name,
                        u.last_name,
                        u.email,
                        u.phone,
                        u.date_of_birth,
                        u.customer_segment,
                        u.customer_status,
                        u.lifetime_value,
                        u.preferred_contact_method,
                        u.marketing_opt_in,
                        u.last_engagement_date,
                        u.created_at,
                        a.address_line1,
                        a.address_line2,
                        a.city,
                        a.state,
                        a.postal_code,
                        a.country
                    FROM users u
                    LEFT JOIN addresses a ON u.id = a.user_id AND a.is_default = true
                    WHERE u.id = $1
                """
                
                customer_data = await conn.fetchrow(customer_query, customer_id)
                if not customer_data:
                    return {"error": f"Customer {customer_id} not found"}
                
                customer_info = dict(customer_data)
                
                # Get order statistics
                order_stats_query = """
                    SELECT 
                        COUNT(*) as total_orders,
                        COALESCE(SUM(total), 0) as total_spent,
                        COALESCE(AVG(total), 0) as avg_order_value,
                        MIN(order_date) as first_order_date,
                        MAX(order_date) as last_order_date,
                        COUNT(CASE WHEN status = 'delivered' THEN 1 END) as completed_orders,
                        COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
                        COUNT(CASE WHEN order_type = 'prebuilt' THEN 1 END) as prebuilt_orders,
                        COUNT(CASE WHEN order_type = 'custom' THEN 1 END) as custom_orders,
                        COALESCE(SUM(shipping_cost), 0) as total_shipping_paid,
                        COALESCE(SUM(discount_amount), 0) as total_discounts_used
                    FROM orders 
                    WHERE user_id = $1
                """
                
                order_stats = dict(await conn.fetchrow(order_stats_query, customer_id))
                
                # Get support ticket statistics
                support_stats_query = """
                    SELECT 
                        COUNT(*) as total_tickets,
                        COUNT(CASE WHEN status = 'open' THEN 1 END) as open_tickets,
                        COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_tickets,
                        COUNT(CASE WHEN priority = 'high' OR priority = 'urgent' THEN 1 END) as high_priority_tickets,
                        AVG(CASE WHEN satisfaction_rating IS NOT NULL THEN satisfaction_rating END) as avg_satisfaction,
                        MAX(created_at) as last_ticket_date
                    FROM customer_support_tickets
                    WHERE user_id = $1
                """
                
                support_stats = dict(await conn.fetchrow(support_stats_query, customer_id))
                
                # Get customer preferences
                preferences_query = """
                    SELECT 
                        preference_type,
                        preference_value,
                        confidence_score
                    FROM customer_preferences
                    WHERE user_id = $1
                    ORDER BY confidence_score DESC
                """
                
                preferences = await conn.fetch(preferences_query, customer_id)
                customer_preferences = {pref['preference_type']: {
                    'value': pref['preference_value'],
                    'confidence': float(pref['confidence_score'])
                } for pref in preferences}
                
                # Calculate days since last order
                if order_stats['last_order_date']:
                    days_since_last_order = (datetime.now().date() - order_stats['last_order_date']).days
                else:
                    days_since_last_order = None
                
                # Calculate customer age in days
                if customer_info['created_at']:
                    customer_age_days = (datetime.now() - customer_info['created_at']).days
                else:
                    customer_age_days = None
                
                # Calculate age if date_of_birth is available
                if customer_info['date_of_birth']:
                    age_years = (datetime.now().date() - customer_info['date_of_birth']).days / 365.25
                else:
                    age_years = None
                
                return {
                    "customer_info": customer_info,
                    "order_statistics": order_stats,
                    "support_statistics": support_stats,
                    "customer_preferences": customer_preferences,
                    "derived_metrics": {
                        "days_since_last_order": days_since_last_order,
                        "customer_age_days": customer_age_days,
                        "age_years": age_years,
                        "completion_rate": order_stats['completed_orders'] / max(order_stats['total_orders'], 1),
                        "cancellation_rate": order_stats['cancelled_orders'] / max(order_stats['total_orders'], 1),
                        "prebuilt_preference": order_stats['prebuilt_orders'] / max(order_stats['total_orders'], 1),
                        "custom_preference": order_stats['custom_orders'] / max(order_stats['total_orders'], 1),
                        "avg_shipping_per_order": order_stats['total_shipping_paid'] / max(order_stats['total_orders'], 1),
                        "avg_discount_per_order": order_stats['total_discounts_used'] / max(order_stats['total_orders'], 1),
                        "support_ticket_rate": support_stats['total_tickets'] / max(order_stats['total_orders'], 1),
                        "support_resolution_rate": support_stats['resolved_tickets'] / max(support_stats['total_tickets'], 1)
                    }
                }
                
            finally:
                await conn.close()
                
        except Exception as e:
            activity.logger.error(f"Error getting customer profile: {str(e)}")
            return {"error": f"Error getting customer profile: {str(e)}"}

    @tool
    async def calculate_customer_lifetime_value(customer_id: int) -> Dict[str, Any]:
        """
        Calculate customer lifetime value based on purchase history and patterns.
        
        Args:
            customer_id: ID of the customer to analyze
            
        Returns:
            CLV analysis with historical value, predicted value, and metrics
        """
        try:
            conn = await asyncio.wait_for(asyncpg.connect(**db_config), timeout=10.0)
            
            try:
                # Get detailed purchase history
                clv_query = """
                    SELECT 
                        o.order_date,
                        o.total,
                        o.status,
                        o.order_type,
                        COUNT(*) OVER() as total_orders,
                        SUM(o.total) OVER() as total_revenue,
                        AVG(o.total) OVER() as avg_order_value,
                        MIN(o.order_date) OVER() as first_order,
                        MAX(o.order_date) OVER() as last_order
                    FROM orders o
                    WHERE o.user_id = $1 AND o.status = 'delivered'
                    ORDER BY o.order_date DESC
                """
                
                orders = await conn.fetch(clv_query, customer_id)
                if not orders:
                    return {
                        "historical_clv": 0.0,
                        "predicted_clv": 0.0,
                        "confidence": "low",
                        "metrics": {
                            "total_orders": 0,
                            "total_revenue": 0.0,
                            "avg_order_value": 0.0,
                            "purchase_frequency": 0.0,
                            "customer_lifespan_days": 0
                        }
                    }
                
                first_order = orders[0]
                total_orders = first_order['total_orders']
                total_revenue = float(first_order['total_revenue'])
                avg_order_value = float(first_order['avg_order_value'])
                first_order_date = first_order['first_order']
                last_order_date = first_order['last_order']
                
                # Calculate metrics
                customer_lifespan_days = (last_order_date - first_order_date).days + 1
                purchase_frequency = total_orders / max(customer_lifespan_days / 365.25, 0.01)  # orders per year
                
                # Simple CLV prediction based on patterns
                if customer_lifespan_days > 0:
                    # Predict remaining lifespan (conservative estimate)
                    days_since_last_order = (datetime.now().date() - last_order_date).days
                    if days_since_last_order <= 90:  # Active customer
                        predicted_lifespan_years = 2.0
                        confidence = "high"
                    elif days_since_last_order <= 180:  # Moderately active
                        predicted_lifespan_years = 1.0
                        confidence = "medium"
                    else:  # At risk
                        predicted_lifespan_years = 0.5
                        confidence = "low"
                    
                    predicted_clv = avg_order_value * purchase_frequency * predicted_lifespan_years
                else:
                    predicted_clv = avg_order_value * 2  # Conservative estimate for new customers
                    confidence = "low"
                
                return {
                    "historical_clv": total_revenue,
                    "predicted_clv": predicted_clv,
                    "total_clv_estimate": total_revenue + predicted_clv,
                    "confidence": confidence,
                    "metrics": {
                        "total_orders": total_orders,
                        "total_revenue": total_revenue,
                        "avg_order_value": avg_order_value,
                        "purchase_frequency": round(purchase_frequency, 2),
                        "customer_lifespan_days": customer_lifespan_days,
                        "days_since_last_order": (datetime.now().date() - last_order_date).days
                    }
                }
                
            finally:
                await conn.close()
                
        except Exception as e:
            activity.logger.error(f"Error calculating CLV: {str(e)}")
            return {"error": f"Error calculating CLV: {str(e)}"}

    @tool
    async def get_customer_risk_score(customer_id: int) -> Dict[str, Any]:
        """
        Calculate customer churn risk score based on recent behavior.
        
        Args:
            customer_id: ID of the customer to analyze
            
        Returns:
            Risk assessment with score and contributing factors
        """
        try:
            conn = await asyncio.wait_for(asyncpg.connect(**db_config), timeout=10.0)
            
            try:
                # Get risk indicators
                risk_query = """
                    SELECT 
                        u.created_at,
                        u.customer_status,
                        u.last_engagement_date,
                        MAX(o.order_date) as last_order_date,
                        COUNT(o.id) as total_orders,
                        COUNT(CASE WHEN o.order_date >= CURRENT_DATE - INTERVAL '90 days' THEN 1 END) as recent_orders,
                        COUNT(CASE WHEN o.status = 'cancelled' THEN 1 END) as cancelled_orders,
                        COUNT(CASE WHEN cs.status = 'open' THEN 1 END) as open_support_tickets,
                        COUNT(CASE WHEN cs.priority IN ('high', 'urgent') THEN 1 END) as high_priority_tickets,
                        AVG(CASE WHEN o.order_date >= CURRENT_DATE - INTERVAL '90 days' THEN o.total END) as recent_avg_order,
                        AVG(CASE WHEN o.order_date < CURRENT_DATE - INTERVAL '90 days' THEN o.total END) as historical_avg_order,
                        MAX(cs.created_at) as last_support_ticket_date
                    FROM users u
                    LEFT JOIN orders o ON u.id = o.user_id
                    LEFT JOIN customer_support_tickets cs ON u.id = cs.user_id
                    WHERE u.id = $1
                    GROUP BY u.id, u.created_at, u.customer_status, u.last_engagement_date
                """
                
                risk_data = await conn.fetchrow(risk_query, customer_id)
                if not risk_data:
                    return {"error": f"Customer {customer_id} not found"}
                
                # Calculate risk factors
                risk_factors = []
                risk_score = 0
                
                # Check customer status (from the enhanced schema)
                if risk_data['customer_status'] == 'at_risk':
                    risk_score += 25
                    risk_factors.append("Customer marked as at-risk")
                elif risk_data['customer_status'] == 'churned':
                    risk_score += 40
                    risk_factors.append("Customer has churned")
                elif risk_data['customer_status'] == 'vip':
                    risk_score -= 10  # VIP customers get lower risk score
                
                # Support ticket indicators
                open_tickets = risk_data['open_support_tickets'] or 0
                high_priority_tickets = risk_data['high_priority_tickets'] or 0
                
                if open_tickets > 0:
                    risk_score += min(open_tickets * 5, 20)  # Cap at 20 points
                    risk_factors.append(f"{open_tickets} open support ticket(s)")
                
                if high_priority_tickets > 0:
                    risk_score += min(high_priority_tickets * 10, 25)  # Cap at 25 points
                    risk_factors.append(f"{high_priority_tickets} high-priority support issue(s)")
                
                # Check last support ticket recency
                if risk_data['last_support_ticket_date']:
                    days_since_ticket = (datetime.now().date() - risk_data['last_support_ticket_date'].date()).days
                    if days_since_ticket <= 7:
                        risk_score += 15
                        risk_factors.append("Recent support ticket (last 7 days)")
                    elif days_since_ticket <= 30:
                        risk_score += 8
                        risk_factors.append("Recent support ticket (last 30 days)")
                
                # Days since last order
                if risk_data['last_order_date']:
                    days_since_last_order = (datetime.now().date() - risk_data['last_order_date']).days
                    if days_since_last_order > 180:
                        risk_score += 40
                        risk_factors.append(f"No orders in {days_since_last_order} days")
                    elif days_since_last_order > 90:
                        risk_score += 20
                        risk_factors.append(f"No recent orders ({days_since_last_order} days)")
                else:
                    risk_score += 30
                    risk_factors.append("No order history")
                
                # Order frequency decline
                total_orders = risk_data['total_orders'] or 0
                recent_orders = risk_data['recent_orders'] or 0
                if total_orders > 0:
                    recent_frequency = recent_orders / max(total_orders, 1)
                    if recent_frequency < 0.2:  # Less than 20% of orders in recent period
                        risk_score += 25
                        risk_factors.append("Declining order frequency")
                
                # Cancellation rate
                cancelled_orders = risk_data['cancelled_orders'] or 0
                if total_orders > 0:
                    cancellation_rate = cancelled_orders / total_orders
                    if cancellation_rate > 0.2:
                        risk_score += 20
                        risk_factors.append(f"High cancellation rate ({cancellation_rate:.1%})")
                
                # Spending decline
                recent_avg = risk_data['recent_avg_order']
                historical_avg = risk_data['historical_avg_order']
                if recent_avg and historical_avg and recent_avg < historical_avg * 0.7:
                    risk_score += 15
                    risk_factors.append("Declining order values")
                
                # Determine risk level
                if risk_score >= 60:
                    risk_level = "high"
                elif risk_score >= 30:
                    risk_level = "medium"
                else:
                    risk_level = "low"
                
                return {
                    "risk_score": min(risk_score, 100),
                    "risk_level": risk_level,
                    "risk_factors": risk_factors,
                    "metrics": {
                        "days_since_last_order": days_since_last_order if risk_data['last_order_date'] else None,
                        "total_orders": total_orders,
                        "recent_orders": recent_orders,
                        "cancellation_rate": cancelled_orders / max(total_orders, 1) if total_orders > 0 else 0
                    }
                }
                
            finally:
                await conn.close()
                
        except Exception as e:
            activity.logger.error(f"Error calculating risk score: {str(e)}")
            return {"error": f"Error calculating risk score: {str(e)}"}

    return [
        get_customer_profile,
        calculate_customer_lifetime_value,
        get_customer_risk_score
    ] 
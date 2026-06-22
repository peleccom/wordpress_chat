"""Mock WordPress data provider."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any


class WordPressMockProvider:
    """Provides mock WordPress data for development and testing."""

    def get_site_info(self) -> dict[str, Any]:
        return {
            "wordpress_version": "6.8",
            "php_version": "8.3",
            "theme": "Astra",
            "active_plugins": 18,
        }

    def get_performance_metrics(self) -> dict[str, Any]:
        return {
            "avg_response_time_ms": 2300,
            "p95_ms": 3900,
            "error_rate": 0.03,
            "slowest_pages": [
                {"url": "/shop", "response_time_ms": 4100},
                {"url": "/product/custom-chair", "response_time_ms": 3800},
                {"url": "/checkout", "response_time_ms": 3500},
                {"url": "/my-account", "response_time_ms": 2900},
                {"url": "/cart", "response_time_ms": 2600},
                {"url": "/blog/best-hosting-guide", "response_time_ms": 1100},
                {"url": "/about", "response_time_ms": 950},
                {"url": "/contact", "response_time_ms": 880},
            ],
        }

    def get_plugin_data(self) -> dict[str, Any]:
        return {
            "plugins": [
                {"name": "WooCommerce", "active": True, "version": "9.0", "actual_version": "9.2"},
                {"name": "Yoast SEO", "active": True, "version": "24.0", "actual_version": "24.0"},
                {"name": "Elementor", "active": True, "version": "3.27", "actual_version": "3.28"},
                {"name": "WP Rocket", "active": True, "version": "3.18", "actual_version": "3.18"},
                {"name": "Akismet Anti-spam", "active": True, "version": "5.3", "actual_version": "5.5"},
                {"name": "Wordfence Security", "active": True, "version": "8.0", "actual_version": "8.1"},
                {"name": "Contact Form 7", "active": True, "version": "6.0", "actual_version": "6.0"},
                {"name": "Rank Math SEO", "active": True, "version": "1.2", "actual_version": "1.3"},
                {"name": "WP Super Cache", "active": True, "version": "1.12", "actual_version": "1.12"},
                {"name": "Smush Image Compression", "active": True, "version": "3.18", "actual_version": "3.20"},
                {"name": "Jetpack", "active": True, "version": "14.0", "actual_version": "14.2"},
                {"name": "MonsterInsights", "active": True, "version": "9.2", "actual_version": "9.2"},
                {"name": "UpdraftPlus Backup", "active": True, "version": "1.24", "actual_version": "1.24"},
                {"name": "Redirection", "active": True, "version": "5.5", "actual_version": "5.5"},
                {"name": "Loco Translate", "active": True, "version": "2.7", "actual_version": "2.8"},
                {"name": "Legacy Gallery", "active": False, "version": "3.1", "actual_version": "3.1"},
                {"name": "Outdated Social Feed", "active": False, "version": "2.0", "actual_version": "3.0"},
                {"name": "Unused Lightbox", "active": False, "version": "1.5", "actual_version": "1.5"},
            ],
            "usage": [
                {"plugin": "WooCommerce", "requests": 14500, "avg_execution_ms": 420},
                {"plugin": "Yoast SEO", "requests": 22000, "avg_execution_ms": 85},
                {"plugin": "Elementor", "requests": 18000, "avg_execution_ms": 650},
                {"plugin": "WP Rocket", "requests": 50000, "avg_execution_ms": 15},
                {"plugin": "Akismet Anti-spam", "requests": 12000, "avg_execution_ms": 55},
                {"plugin": "Wordfence Security", "requests": 50000, "avg_execution_ms": 95},
                {"plugin": "Contact Form 7", "requests": 8000, "avg_execution_ms": 120},
                {"plugin": "Rank Math SEO", "requests": 22000, "avg_execution_ms": 75},
                {"plugin": "WP Super Cache", "requests": 50000, "avg_execution_ms": 5},
                {"plugin": "Smush Image Compression", "requests": 3000, "avg_execution_ms": 340},
                {"plugin": "Jetpack", "requests": 35000, "avg_execution_ms": 180},
                {"plugin": "MonsterInsights", "requests": 50000, "avg_execution_ms": 30},
                {"plugin": "UpdraftPlus Backup", "requests": 200, "avg_execution_ms": 2500},
                {"plugin": "Redirection", "requests": 15000, "avg_execution_ms": 12},
                {"plugin": "Loco Translate", "requests": 50, "avg_execution_ms": 45},
                {"plugin": "Legacy Gallery", "requests": 0, "avg_execution_ms": 0},
                {"plugin": "Outdated Social Feed", "requests": 0, "avg_execution_ms": 0},
                {"plugin": "Unused Lightbox", "requests": 0, "avg_execution_ms": 0},
            ],
        }

    def get_security_report(self) -> dict[str, Any]:
        return {
            "critical_vulnerabilities": 2,
            "high_vulnerabilities": 4,
            "medium_vulnerabilities": 8,
            "outdated_plugins": 5,
            "last_scan": (datetime.now(UTC) - timedelta(hours=6)).isoformat(),
            "findings": [
                {"severity": "critical", "description": "Outdated Social Feed has known RCE vulnerability (CVE-2026-1234)", "affected_plugin": "Outdated Social Feed", "recommendation": "Remove or update immediately"},
                {"severity": "critical", "description": "WordPress core database query vulnerability (CVE-2026-5678)", "affected_plugin": "WordPress Core", "recommendation": "Update to WordPress 6.9"},
                {"severity": "high", "description": "XSS vulnerability in Legacy Gallery plugin", "affected_plugin": "Legacy Gallery", "recommendation": "Remove unused plugin"},
                {"severity": "high", "description": "Outdated SSL certificate configuration", "affected_plugin": "N/A", "recommendation": "Renew SSL certificate and enable HSTS"},
                {"severity": "high", "description": "Brute force login attempts detected (1500 attempts in 24h)", "affected_plugin": "N/A", "recommendation": "Enable rate limiting and 2FA"},
                {"severity": "high", "description": "Unused admin accounts with weak passwords", "affected_plugin": "N/A", "recommendation": "Audit and remove inactive admin accounts"},
                {"severity": "medium", "description": "XML-RPC pingback vulnerability", "affected_plugin": "WordPress Core", "recommendation": "Disable XML-RPC if not needed"},
                {"severity": "medium", "description": "Missing security headers (X-Frame-Options, CSP)", "affected_plugin": "N/A", "recommendation": "Add security headers via .htaccess"},
            ],
        }

    def get_traffic_data(self) -> dict[str, Any]:
        return {
            "visits": 50000,
            "unique_visitors": 38500,
            "organic": 32000,
            "direct": 8000,
            "social": 10000,
            "referral": 5000,
            "pageviews": 185000,
            "avg_session_duration_sec": 145,
            "bounce_rate": 0.42,
        }

    def get_content_data(self) -> dict[str, Any]:
        return {
            "top_posts": [
                {"title": "Best Hosting Guide 2026", "views": 154000},
                {"title": "How to Start a Blog", "views": 128000},
                {"title": "SEO Basics Tutorial", "views": 95000},
                {"title": "WordPress Security Tips", "views": 87000},
                {"title": "Performance Optimization Guide", "views": 72000},
            ],
            "dead_content": [
                {"title": "Old Product Launch 2020", "views": 12},
                {"title": "Deprecated API Guide", "views": 8},
                {"title": "Expired Coupon Codes", "views": 5},
                {"title": "Team Member Spotlight 2019", "views": 3},
                {"title": "Legacy Documentation v1", "views": 1},
            ],
        }

    def get_user_data(self) -> dict[str, Any]:
        return {
            "total_users": 3200,
            "inactive_users": 780,
            "active_users_last_30d": 2150,
            "new_users_last_30d": 145,
            "inactive_list": [
                {"email": "sarah.chen@example.com", "last_login_days": 365},
                {"email": "mike.ross@example.com", "last_login_days": 310},
                {"email": "anna.williams@example.com", "last_login_days": 280},
                {"email": "james.wilson@example.com", "last_login_days": 250},
                {"email": "emma.davis@example.com", "last_login_days": 220},
                {"email": "lucas.brown@example.com", "last_login_days": 200},
                {"email": "olivia.jones@example.com", "last_login_days": 190},
                {"email": "liam.garcia@example.com", "last_login_days": 180},
            ],
        }

    def get_recent_errors(self) -> list[dict[str, Any]]:
        now = datetime.now(UTC)
        return [
            {"timestamp": (now - timedelta(minutes=5)).isoformat(), "error": "Database timeout on /shop query (MySQL slow query)", "count": 23, "severity": "high"},
            {"timestamp": (now - timedelta(minutes=15)).isoformat(), "error": "PHP memory exhaustion on /checkout (256MB limit)", "count": 12, "severity": "high"},
            {"timestamp": (now - timedelta(minutes=45)).isoformat(), "error": "WooCommerce webhook delivery failed - 503 from shipping API", "count": 8, "severity": "medium"},
            {"timestamp": (now - timedelta(hours=2)).isoformat(), "error": "Elementor template render timeout (>30s)", "count": 45, "severity": "medium"},
            {"timestamp": (now - timedelta(hours=4)).isoformat(), "error": "Failed backup upload to S3 - connection timeout", "count": 3, "severity": "low"},
        ]

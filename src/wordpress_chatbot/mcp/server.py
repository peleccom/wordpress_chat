"""FastMCP server exposing WordPress analytics tools."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from wordpress_chatbot.providers.wordpress_mock import WordPressMockProvider

mcp = FastMCP(
    "WordPress Insights",
    instructions="AI-powered WordPress analytics and insights MCP server.",
)

provider = WordPressMockProvider()


@mcp.tool(description="Get basic WordPress site information (version, theme, plugins count).")
def get_site_info() -> str:
    return json.dumps(provider.get_site_info(), indent=2)


@mcp.tool(description="Get site performance metrics (avg/p95 response times, error rate) and slowest pages.")
def get_performance_metrics() -> str:
    return json.dumps(provider.get_performance_metrics(), indent=2)


@mcp.tool(description="Get list of all plugins with active status and version, plus performance usage metrics.")
def get_plugin_data() -> str:
    return json.dumps(provider.get_plugin_data(), indent=2)


@mcp.tool(description="Get security vulnerability summary and detailed findings with recommendations.")
def get_security_report() -> str:
    return json.dumps(provider.get_security_report(), indent=2)


@mcp.tool(description="Get traffic summary with channel breakdown (organic, direct, social, referral).")
def get_traffic_data() -> str:
    return json.dumps(provider.get_traffic_data(), indent=2)


@mcp.tool(description="Get top-performing and underperforming (dead) content.")
def get_content_data() -> str:
    return json.dumps(provider.get_content_data(), indent=2)


@mcp.tool(description="Get user statistics and list of inactive users.")
def get_user_data() -> str:
    return json.dumps(provider.get_user_data(), indent=2)


@mcp.tool(description="Get recent error log entries with timestamps, severity, and occurrence counts.")
def get_recent_errors() -> str:
    return json.dumps(provider.get_recent_errors(), indent=2)


@mcp.resource(uri="site://performance", name="Performance Overview", description="Site performance metrics and slowest pages", mime_type="application/json")
async def performance_resource() -> str:
    return json.dumps(provider.get_performance_metrics(), indent=2)


@mcp.resource(uri="site://security", name="Security Overview", description="Security report with findings", mime_type="application/json")
async def security_resource() -> str:
    return json.dumps(provider.get_security_report(), indent=2)


@mcp.resource(uri="site://plugins", name="Plugin Overview", description="List of all plugins and their usage", mime_type="application/json")
async def plugins_resource() -> str:
    return json.dumps(provider.get_plugin_data(), indent=2)


@mcp.resource(uri="site://traffic", name="Traffic Overview", description="Traffic summary data", mime_type="application/json")
async def traffic_resource() -> str:
    return json.dumps(provider.get_traffic_data(), indent=2)


@mcp.prompt(name="analyze_site_health", description="Generate a comprehensive site health analysis")
def analyze_site_health_prompt() -> str:
    return """Analyze overall site health: overall assessment, key findings across performance/security/content/traffic, and actionable recommendations prioritized by impact."""


@mcp.prompt(name="security_audit", description="Run a focused security audit")
def security_audit_prompt() -> str:
    return """Perform a security audit: critical vulnerabilities, high-risk findings with remediation, outdated plugins, and overall security posture."""


@mcp.prompt(name="performance_audit", description="Analyze site performance")
def performance_audit_prompt() -> str:
    return """Analyze performance: current metrics, slowest pages with causes, plugin-level impact, and optimization recommendations."""

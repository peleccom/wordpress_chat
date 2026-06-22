"""Tests for the mock WordPress data provider."""

from __future__ import annotations

from wordpress_chatbot.providers.wordpress_mock import WordPressMockProvider


def test_get_site_info() -> None:
    provider = WordPressMockProvider()
    info = provider.get_site_info()
    assert info["wordpress_version"] == "6.8"
    assert info["php_version"] == "8.3"
    assert info["theme"] == "Astra"
    assert isinstance(info["active_plugins"], int)
    assert info["active_plugins"] > 0


def test_get_performance_metrics() -> None:
    provider = WordPressMockProvider()
    metrics = provider.get_performance_metrics()
    assert metrics["avg_response_time_ms"] > 0
    assert metrics["p95_ms"] > metrics["avg_response_time_ms"]
    assert 0 <= metrics["error_rate"] <= 1
    assert len(metrics["slowest_pages"]) > 0
    assert metrics["slowest_pages"][0]["response_time_ms"] >= metrics["slowest_pages"][-1]["response_time_ms"]


def test_get_plugin_data() -> None:
    provider = WordPressMockProvider()
    data = provider.get_plugin_data()
    assert len(data["plugins"]) > 0
    assert any(p["name"] == "WooCommerce" for p in data["plugins"])
    assert any(p["active"] is False for p in data["plugins"])
    assert all("actual_version" in p for p in data["plugins"])
    assert any(p["version"] != p["actual_version"] for p in data["plugins"])  # some outdated
    assert len(data["usage"]) > 0
    woocommerce = next(p for p in data["usage"] if p["plugin"] == "WooCommerce")
    assert woocommerce["avg_execution_ms"] > 0
    assert any(p["requests"] == 0 for p in data["usage"])


def test_get_security_report() -> None:
    provider = WordPressMockProvider()
    report = provider.get_security_report()
    assert "critical_vulnerabilities" in report
    assert "outdated_plugins" in report
    assert report["critical_vulnerabilities"] > 0
    assert len(report["findings"]) > 0
    assert all(f["severity"] in ("critical", "high", "medium", "low") for f in report["findings"])


def test_get_traffic_data() -> None:
    provider = WordPressMockProvider()
    data = provider.get_traffic_data()
    assert data["visits"] > 0
    assert data["organic"] > 0
    total = data["organic"] + data["direct"] + data["social"] + data["referral"]
    assert total <= data["visits"] * 1.1


def test_get_content_data() -> None:
    provider = WordPressMockProvider()
    data = provider.get_content_data()
    assert len(data["top_posts"]) > 0
    assert all(p["views"] > 0 for p in data["top_posts"])
    for i in range(len(data["top_posts"]) - 1):
        assert data["top_posts"][i]["views"] >= data["top_posts"][i + 1]["views"]
    assert len(data["dead_content"]) > 0
    assert all(p["views"] < 100 for p in data["dead_content"])


def test_get_user_data() -> None:
    provider = WordPressMockProvider()
    data = provider.get_user_data()
    assert data["total_users"] > 0
    assert data["inactive_users"] > 0
    assert data["inactive_users"] < data["total_users"]
    assert len(data["inactive_list"]) > 0
    assert all(u["last_login_days"] > 0 for u in data["inactive_list"])


def test_get_recent_errors() -> None:
    provider = WordPressMockProvider()
    errors = provider.get_recent_errors()
    assert len(errors) > 0
    assert all(e["error"] for e in errors)
    assert all(e["count"] > 0 for e in errors)


def test_deterministic_across_calls() -> None:
    provider = WordPressMockProvider()
    assert provider.get_site_info() == provider.get_site_info()
    assert provider.get_plugin_data() == provider.get_plugin_data()

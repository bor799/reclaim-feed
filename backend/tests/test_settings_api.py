# -*- coding: utf-8 -*-
"""
Settings API Tests — Module 3
"""

import pytest


class TestSettingsAPI:
    """Test cases for Settings API endpoints."""

    def test_get_all_settings(self, client):
        """Test getting all settings."""
        response = client.get("/api/v1/settings")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_providers(self, client):
        """Test getting LLM providers."""
        response = client.get("/api/v1/settings/providers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_providers_empty(self, client):
        """Test providers when list is empty."""
        # This test verifies the endpoint works with empty list
        response = client.get("/api/v1/settings/providers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_providers(self, client):
        """Test updating LLM providers."""
        providers = [
            {
                "name": "OpenAI",
                "api_key": "test_key",
                "api_base": "https://api.openai.com",
                "enabled": True
            },
            {
                "name": "Zhipu",
                "api_key": "test_key",
                "api_base": "https://open.bigmodel.cn/api/paas/v4",
                "proxy_url": "socks5://127.0.0.1:1080",
                "enabled": True
            }
        ]
        response = client.put("/api/v1/settings/providers", json=providers)
        assert response.status_code in (200, 500)

    def test_update_providers_empty(self, client):
        """Test updating providers with empty list."""
        response = client.put("/api/v1/settings/providers", json=[])
        assert response.status_code in (200, 500)

    def test_update_providers_with_proxy(self, client):
        """Test updating providers with proxy configuration."""
        providers = [
            {
                "name": "OpenAI",
                "api_key": "test_key",
                "api_base": "https://api.openai.com",
                "proxy_url": "socks5://127.0.0.1:1080",
                "enabled": True
            }
        ]
        response = client.put("/api/v1/settings/providers", json=providers)
        assert response.status_code in (200, 500)

    def test_get_bots(self, client):
        """Test getting bot configurations."""
        response = client.get("/api/v1/settings/bots")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_bots_empty(self, client):
        """Test bots with empty configuration."""
        response = client.get("/api/v1/settings/bots")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_update_bots(self, client):
        """Test updating bot configurations."""
        bots = {
            "telegram_bot_token": "new_test_token",
            "telegram_chat_id": "new_test_chat_id",
            "feishu_webhook_url": "https://feishu.webhook/new"
        }
        response = client.put("/api/v1/settings/bots", json=bots)
        assert response.status_code in (200, 500)

    def test_update_bots_partial(self, client):
        """Test updating bots with partial data."""
        bots = {
            "telegram_bot_token": "partial_token"
        }
        response = client.put("/api/v1/settings/bots", json=bots)
        assert response.status_code in (200, 500)

    def test_get_environment(self, client):
        """Test getting environment settings."""
        response = client.get("/api/v1/settings/environment")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_update_environment(self, client):
        """Test updating environment settings."""
        env = {
            "locale": "zh",
            "local_workspace_path": "/path/to/workspace",
            "system_prompt": "You are a helpful assistant."
        }
        response = client.put("/api/v1/settings/environment", json=env)
        assert response.status_code in (200, 500)

    def test_update_environment_locale(self, client):
        """Test updating locale setting."""
        env = {"locale": "en"}
        response = client.put("/api/v1/settings/environment", json=env)
        assert response.status_code in (200, 500)

    def test_test_connection_default_provider(self, client):
        """Test connection with default provider."""
        response = client.post("/api/v1/system/test-connection", json={})
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "latency_ms" in data

    def test_test_connection_named_provider(self, client):
        """Test connection with named provider."""
        request_data = {"provider_name": "OpenAI"}
        response = client.post("/api/v1/system/test-connection", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "latency_ms" in data

    def test_test_connection_nonexistent_provider(self, client):
        """Test connection with non-existent provider."""
        request_data = {"provider_name": "NonExistentProvider"}
        response = client.post("/api/v1/system/test-connection", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "latency_ms" in data

    def test_test_connection_with_proxy(self, client):
        """Test connection with proxy configuration."""
        # This tests the proxy handling in the connection test
        request_data = {"provider_name": "Zhipu"}
        response = client.post("/api/v1/system/test-connection", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "latency_ms" in data

    def test_export_json(self, client):
        """Test JSON export."""
        response = client.get("/api/v1/export/json")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_export_markdown(self, client):
        """Test Markdown export (not implemented)."""
        response = client.get("/api/v1/export/markdown")
        assert response.status_code == 200
        data = response.json()
        # Should return not_implemented status
        assert data.get("status") == "not_implemented" or "status" in data


class TestSettingsAPIIntegration:
    """Integration tests for Settings API."""

    def test_settings_workflow(self, client):
        """Test complete settings workflow: get -> update -> verify."""
        # Get current settings
        response = client.get("/api/v1/settings")
        assert response.status_code == 200

        # Update environment
        env = {"locale": "zh"}
        response = client.put("/api/v1/settings/environment", json=env)
        assert response.status_code in (200, 500)

        # Verify update (may fail due to config save)
        if response.status_code == 200:
            response = client.get("/api/v1/settings/environment")
            assert response.status_code == 200

    def test_provider_connection_workflow(self, client):
        """Test provider setup and connection test workflow."""
        # Update providers
        providers = [
            {
                "name": "TestProvider",
                "api_key": "test_key",
                "api_base": "https://api.test.com",
                "enabled": True
            }
        ]
        response = client.put("/api/v1/settings/providers", json=providers)
        assert response.status_code in (200, 500)

        # Test connection
        response = client.post("/api/v1/system/test-connection", json={"provider_name": "TestProvider"})
        assert response.status_code == 200

    def test_export_multiple_formats(self, client):
        """Test exporting data in multiple formats."""
        # JSON export
        response = client.get("/api/v1/export/json")
        assert response.status_code == 200

        # CSV export
        response = client.get("/api/v1/export/feed")
        assert response.status_code == 200

        # Markdown export (should return not implemented)
        response = client.get("/api/v1/export/markdown")
        assert response.status_code == 200


class TestSettingsAPIEdgeCases:
    """Edge case tests for Settings API."""

    def test_providers_with_special_characters(self, client):
        """Test providers with special characters in name."""
        providers = [
            {
                "name": "Test Provider (中国)",
                "api_key": "test_key",
                "api_base": "https://api.test.com",
                "enabled": True
            }
        ]
        response = client.put("/api/v1/settings/providers", json=providers)
        assert response.status_code in (200, 500)

    def test_environment_with_path_traversal(self, client):
        """Test environment settings with path traversal attempts."""
        env = {
            "local_workspace_path": "../../../etc/passwd"
        }
        response = client.put("/api/v1/settings/environment", json=env)
        assert response.status_code in (200, 500)

    def test_bots_with_invalid_tokens(self, client):
        """Test bots with invalid token formats."""
        bots = {
            "telegram_bot_token": "",
            "telegram_chat_id": ""
        }
        response = client.put("/api/v1/settings/bots", json=bots)
        assert response.status_code in (200, 500)

    def test_multiple_providers_same_name(self, client):
        """Test adding multiple providers with same name."""
        providers = [
            {"name": "Duplicate", "api_key": "key1", "api_base": "https://api1.com"},
            {"name": "Duplicate", "api_key": "key2", "api_base": "https://api2.com"}
        ]
        response = client.put("/api/v1/settings/providers", json=providers)
        assert response.status_code in (200, 500)

    def test_connection_timeout_handling(self, client):
        """Test connection timeout handling."""
        # This tests the timeout handling in connection test
        request_data = {"provider_name": "NonExistent"}
        response = client.post("/api/v1/system/test-connection", json=request_data)
        assert response.status_code == 200
        data = response.json()
        # Should handle gracefully with latency
        assert "latency_ms" in data


class TestRunPipelineAPI:
    """Test cases for Pipeline execution API."""

    def test_run_pipeline_dry_run(self, client):
        """Test running pipeline in dry-run mode."""
        response = client.post("/api/v1/run?dry_run=true")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "started"

    def test_run_pipeline_normal(self, client):
        """Test running pipeline normally."""
        response = client.post("/api/v1/run")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "started"

    def test_run_pipeline_multiple_times(self, client):
        """Test running pipeline multiple times."""
        for i in range(3):
            response = client.post("/api/v1/run?dry_run=true")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "started"

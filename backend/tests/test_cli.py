# -*- coding: utf-8 -*-
"""
Test suite for CLI module (cli.py)

Tests command-line interface functionality including:
- Help command
- Dry-run mode
- Serve command
- URL parameter handling
- Config file loading
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def mock_config():
    """Mock config fixture."""
    config = Mock()
    config.llm = Mock()
    config.llm.provider = "zhipu"
    config.llm.model = "glm-4.7"
    config.llm.api_key_env = "ZHIPU_API_KEY"
    config.llm.api_base = "https://open.bigmodel.cn/api/paas/v4"
    return config


@pytest.fixture
def mock_pipeline():
    """Mock pipeline fixture."""
    pipeline = Mock()
    pipeline.run = AsyncMock(return_value=None)
    return pipeline


class AsyncMock(Mock):
    """Async mock helper."""
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class TestCLIHelp:
    """Test CLI help functionality."""

    def test_cli_help_argument(self, capsys):
        """Test --help argument shows help text."""
        with patch('sys.argv', ['knowledge-agent', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                from src.cli import main
                main()
            # Should exit with code 0 for help
            assert exc_info.value.code == 0

    def test_cli_help_contains_description(self, capsys):
        """Test help output contains description."""
        with patch('sys.argv', ['knowledge-agent', '--help']):
            with pytest.raises(SystemExit):
                from src.cli import main
                main()
            captured = capsys.readouterr()
            assert "100X 知识 Agent" in captured.out or "100X Knowledge Agent" in captured.out


class TestCLIDryRun:
    """Test CLI dry-run mode."""

    @patch('src.cli.load_config')
    @patch('src.cli.Pipeline')
    def test_cli_dry_run_flag(self, mock_pipeline_cls, mock_load_config, mock_config):
        """Test --dry-run flag passes to pipeline."""
        mock_load_config.return_value = mock_config
        mock_pipeline = Mock()
        mock_pipeline.run = AsyncMock(return_value=None)
        mock_pipeline_cls.return_value = mock_pipeline

        with patch('sys.argv', ['knowledge-agent', '--dry-run']):
            from src.cli import main
            main()

        mock_pipeline.run.assert_called_once_with(dry_run=True)


class TestCLIServe:
    """Test CLI serve command."""

    @patch('src.cli.load_config')
    @patch('src.cli.start_server')
    def test_cli_serve_command(self, mock_start_server, mock_load_config, mock_config):
        """Test 'serve' command starts server."""
        mock_load_config.return_value = mock_config
        mock_start_server.return_value = None

        with patch('sys.argv', ['knowledge-agent', 'serve']):
            from src.cli import main
            main()

        mock_start_server.assert_called_once()

    @patch('src.cli.load_config')
    @patch('src.cli.start_server')
    def test_cli_serve_with_port(self, mock_start_server, mock_load_config, mock_config):
        """Test 'serve' command with custom port."""
        mock_load_config.return_value = mock_config
        mock_start_server.return_value = None

        with patch('sys.argv', ['knowledge-agent', 'serve', '--port', '9000']):
            from src.cli import main
            main()

        mock_start_server.assert_called_once_with(mock_config, port=9000)


class TestCLIUrl:
    """Test CLI URL parameter handling."""

    @patch('src.cli.load_config')
    @patch('src.cli.Pipeline')
    def test_cli_url_argument(self, mock_pipeline_cls, mock_load_config, mock_config):
        """Test --url argument accepts URL."""
        mock_load_config.return_value = mock_config
        mock_pipeline = Mock()
        mock_pipeline.run = AsyncMock(return_value=None)
        mock_pipeline_cls.return_value = mock_pipeline

        test_url = "https://example.com/article"
        with patch('sys.argv', ['knowledge-agent', '--url', test_url]):
            from src.cli import main
            main()

        # URL should be parsed by argparse (verified if no exception)
        assert True


class TestCLIConfig:
    """Test CLI config file handling."""

    @patch('src.cli.load_config')
    @patch('src.cli.Pipeline')
    def test_cli_config_default(self, mock_pipeline_cls, mock_load_config, mock_config):
        """Test default config path."""
        mock_load_config.return_value = mock_config
        mock_pipeline = Mock()
        mock_pipeline.run = AsyncMock(return_value=None)
        mock_pipeline_cls.return_value = mock_pipeline

        with patch('sys.argv', ['knowledge-agent']):
            from src.cli import main
            main()

        mock_load_config.assert_called_once_with("config/config.yaml")

    @patch('src.cli.load_config')
    @patch('src.cli.Pipeline')
    def test_cli_config_custom(self, mock_pipeline_cls, mock_load_config, mock_config):
        """Test custom config path."""
        mock_load_config.return_value = mock_config
        mock_pipeline = Mock()
        mock_pipeline.run = AsyncMock(return_value=None)
        mock_pipeline_cls.return_value = mock_pipeline

        custom_config = "custom/test-config.yaml"
        with patch('sys.argv', ['knowledge-agent', '--config', custom_config]):
            from src.cli import main
            main()

        mock_load_config.assert_called_once_with(custom_config)


class TestCLIVerbose:
    """Test CLI verbose mode."""

    @patch('src.cli.load_config')
    @patch('src.cli.Pipeline')
    def test_cli_verbose_flag(self, mock_pipeline_cls, mock_load_config, mock_config):
        """Test --verbose flag is parsed."""
        mock_load_config.return_value = mock_config
        mock_pipeline = Mock()
        mock_pipeline.run = AsyncMock(return_value=None)
        mock_pipeline_cls.return_value = mock_pipeline

        with patch('sys.argv', ['knowledge-agent', '--verbose']):
            from src.cli import main
            main()

        # Verbose should be parsed without error
        assert True


class TestCLIDefaultCommand:
    """Test CLI default command behavior."""

    @patch('src.cli.load_config')
    @patch('src.cli.Pipeline')
    def test_cli_default_run(self, mock_pipeline_cls, mock_load_config, mock_config):
        """Test default command is 'run'."""
        mock_load_config.return_value = mock_config
        mock_pipeline = Mock()
        mock_pipeline.run = AsyncMock(return_value=None)
        mock_pipeline_cls.return_value = mock_pipeline

        with patch('sys.argv', ['knowledge-agent']):
            from src.cli import main
            main()

        mock_pipeline.run.assert_called_once_with(dry_run=False)

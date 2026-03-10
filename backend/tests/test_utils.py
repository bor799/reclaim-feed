# -*- coding: utf-8 -*-
"""
Test suite for utility modules (utils/)

Tests utility functions including:
- Prompt manager
- Config loading
- Path expansion
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ──────────────────────────────────────────────
# Config Tests
# ──────────────────────────────────────────────

class TestConfig:
    """Test configuration loading functionality."""

    def test_load_config_default_path(self):
        """Test loading config from default path."""
        from src.config import load_config, PROJECT_ROOT

        # Test with non-existent file (should use defaults)
        config = load_config("nonexistent.yaml")

        assert config is not None
        assert hasattr(config, 'llm')

    def test_load_config_with_existing_file(self):
        """Test loading config from existing file."""
        from src.config import load_config

        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('llm:\n  provider: test_provider\n  model: test_model\n')
            temp_path = f.name

        try:
            config = load_config(temp_path)
            assert config.llm.provider == 'test_provider'
        finally:
            Path(temp_path).unlink()

    def test_load_config_env_override(self):
        """Test environment variable override for API key."""
        import os
        from src.config import load_config

        os.environ['ZHIPU_API_KEY'] = 'test_key_123'

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('llm:\n  provider: zhipu\n')
            temp_path = f.name

        try:
            config = load_config(temp_path)
            # The API key from env should be used
        finally:
            Path(temp_path).unlink()
            if 'ZHIPU_API_KEY' in os.environ:
                del os.environ['ZHIPU_API_KEY']

    def test_get_state_path(self):
        """Test state path generation."""
        from src.config import get_state_path

        path = get_state_path("test.json")

        assert path.name == "test.json"
        assert path.parent.name == "state"

    def test_expand_path_tilde(self):
        """Test path expansion with tilde."""
        from src.config import expand_path

        result = expand_path("~/test")
        assert str(result).startswith("/")

    def test_expand_path_env_var(self, monkeypatch):
        """Test path expansion with environment variable."""
        from src.config import expand_path

        monkeypatch.setenv("TEST_VAR", "/tmp/test")

        # Note: Path.expanduser() doesn't expand $ENV, so this tests
        # that the function handles it gracefully
        result = expand_path("$TEST_VAR/file")
        # Just verify it returns a Path object
        assert isinstance(result, Path)

    def test_load_prompt_existing_file(self):
        """Test loading prompt from existing file."""
        from src.config import load_prompt

        # Create a temporary prompt file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('Test prompt content')
            temp_path = f.name

        try:
            # Need to use relative path from PROJECT_ROOT
            content = load_prompt(temp_path)
            assert content == "Test prompt content"
        finally:
            Path(temp_path).unlink()

    def test_load_prompt_nonexistent_file(self):
        """Test loading prompt from non-existent file."""
        from src.config import load_prompt

        content = load_prompt("nonexistent.md")
        assert content == ""


# ──────────────────────────────────────────────
# Prompt Manager Tests
# ──────────────────────────────────────────────

@pytest.fixture
def temp_prompt_dir():
    """Create a temporary directory for prompt testing."""
    temp_path = Path(tempfile.mkdtemp(prefix="prompt_test_"))
    prompt_dir = temp_path / "prompts"
    prompt_dir.mkdir(parents=True)

    # Create stage files
    (prompt_dir / "scoring.md").write_text("Original scoring prompt", encoding="utf-8")
    (prompt_dir / "extraction.md").write_text("Original extraction prompt", encoding="utf-8")

    yield temp_path

    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


class TestPromptManager:
    """Test prompt version management functionality."""

    @patch('src.utils.prompt_manager.PROJECT_ROOT')
    def test_get_prompt_existing(self, mock_root, temp_prompt_dir):
        """Test getting existing prompt."""
        mock_root.__truediv__ = lambda self, other: temp_prompt_dir / other

        # We need to patch the module-level constants
        import src.utils.prompt_manager as pm
        original_prompt_dir = pm.PROMPT_DIR
        pm.PROMPT_DIR = temp_prompt_dir / "prompts"

        try:
            result = pm.get_prompt("scoring")
            assert result == "Original scoring prompt"
        finally:
            pm.PROMPT_DIR = original_prompt_dir

    @patch('src.utils.prompt_manager.PROJECT_ROOT')
    def test_get_prompt_nonexistent_stage(self, mock_root, temp_prompt_dir):
        """Test getting prompt for nonexistent stage."""
        import src.utils.prompt_manager as pm
        original_prompt_dir = pm.PROMPT_DIR
        pm.PROMPT_DIR = temp_prompt_dir / "prompts"

        try:
            result = pm.get_prompt("nonexistent")
            assert result is None
        finally:
            pm.PROMPT_DIR = original_prompt_dir

    @patch('src.utils.prompt_manager.PROJECT_ROOT')
    def test_update_prompt_creates_version(self, mock_root, temp_prompt_dir):
        """Test updating prompt creates new version."""
        import src.utils.prompt_manager as pm
        original_prompt_dir = pm.PROMPT_DIR
        pm.PROMPT_DIR = temp_prompt_dir / "prompts"
        original_history_dir = pm.HISTORY_DIR
        pm.HISTORY_DIR = temp_prompt_dir / "prompts" / "history"

        try:
            result = pm.update_prompt("scoring", "New scoring prompt")

            assert result["stage"] == "scoring"
            assert result["version"] == 2  # First backup is v1, new is v2

            # Check history was created
            history_dir = temp_prompt_dir / "prompts" / "history" / "scoring"
            assert history_dir.exists()
            assert (history_dir / "v1.md").exists()

            # Check new content
            current = pm.get_prompt("scoring")
            assert current == "New scoring prompt"
        finally:
            pm.PROMPT_DIR = original_prompt_dir
            pm.HISTORY_DIR = original_history_dir

    @patch('src.utils.prompt_manager.PROJECT_ROOT')
    def test_get_prompt_history(self, mock_root, temp_prompt_dir):
        """Test getting prompt history."""
        import src.utils.prompt_manager as pm
        original_prompt_dir = pm.PROMPT_DIR
        pm.PROMPT_DIR = temp_prompt_dir / "prompts"
        original_history_dir = pm.HISTORY_DIR
        pm.HISTORY_DIR = temp_prompt_dir / "prompts" / "history"

        try:
            # Update to create history
            pm.update_prompt("scoring", "Version 2")
            pm.update_prompt("scoring", "Version 3")

            history = pm.get_prompt_history("scoring")

            assert len(history) == 2
            assert history[0]["version"] == 1
            assert history[1]["version"] == 2
            assert "archived_at" in history[0]
        finally:
            pm.PROMPT_DIR = original_prompt_dir
            pm.HISTORY_DIR = original_history_dir

    @patch('src.utils.prompt_manager.PROJECT_ROOT')
    def test_get_prompt_version(self, mock_root, temp_prompt_dir):
        """Test getting specific prompt version."""
        import src.utils.prompt_manager as pm
        original_prompt_dir = pm.PROMPT_DIR
        pm.PROMPT_DIR = temp_prompt_dir / "prompts"
        original_history_dir = pm.HISTORY_DIR
        pm.HISTORY_DIR = temp_prompt_dir / "prompts" / "history"

        try:
            # Create versions
            pm.update_prompt("scoring", "Version 2")

            # Get specific version
            content = pm.get_prompt_version("scoring", 1)

            assert content == "Original scoring prompt"
        finally:
            pm.PROMPT_DIR = original_prompt_dir
            pm.HISTORY_DIR = original_history_dir

    @patch('src.utils.prompt_manager.PROJECT_ROOT')
    def test_get_prompt_version_nonexistent(self, mock_root, temp_prompt_dir):
        """Test getting nonexistent prompt version."""
        import src.utils.prompt_manager as pm
        original_prompt_dir = pm.PROMPT_DIR
        pm.PROMPT_DIR = temp_prompt_dir / "prompts"
        original_history_dir = pm.HISTORY_DIR
        pm.HISTORY_DIR = temp_prompt_dir / "prompts" / "history"

        try:
            content = pm.get_prompt_version("scoring", 999)
            assert content is None
        finally:
            pm.PROMPT_DIR = original_prompt_dir
            pm.HISTORY_DIR = original_history_dir


# ──────────────────────────────────────────────
# Stage File Mapping Tests
# ──────────────────────────────────────────────

class TestStageFileMapping:
    """Test stage to file mappings."""

    def test_all_stages_mapped(self):
        """Test all expected stages are mapped."""
        from src.utils.prompt_manager import STAGE_FILES

        expected_stages = ["scoring", "extraction", "obsidian_format", "publish"]

        for stage in expected_stages:
            assert stage in STAGE_FILES
            assert STAGE_FILES[stage].endswith(".md")

    def test_stage_files_correct_names(self):
        """Test stage file names are correct."""
        from src.utils.prompt_manager import STAGE_FILES

        assert STAGE_FILES["scoring"] == "scoring.md"
        assert STAGE_FILES["extraction"] == "extraction.md"
        assert STAGE_FILES["obsidian_format"] == "obsidian_format.md"
        assert STAGE_FILES["publish"] == "publish.md"


# ──────────────────────────────────────────────
# Path Utilities Tests
# ──────────────────────────────────────────────

class TestPathUtilities:
    """Test path utility functions."""

    def test_project_root_exists(self):
        """Test PROJECT_ROOT is defined and exists."""
        from src.config import PROJECT_ROOT

        assert isinstance(PROJECT_ROOT, Path)
        # Project root should exist
        assert PROJECT_ROOT.exists()

    def test_prompt_dir_relative_to_root(self):
        """Test PROMPT_DIR is relative to PROJECT_ROOT."""
        from src.config import PROJECT_ROOT
        from src.utils.prompt_manager import PROMPT_DIR

        # PROMPT_DIR should be under PROJECT_ROOT
        assert PROJECT_ROOT in PROMPT_DIR.parents or PROJECT_ROOT == PROMPT_DIR


# ──────────────────────────────────────────────
# Metadata Tests
# ──────────────────────────────────────────────

class TestMetadata:
    """Test metadata handling in prompt manager."""

    @patch('src.utils.prompt_manager.PROJECT_ROOT')
    def test_metadata_saved_on_update(self, mock_root, temp_prompt_dir):
        """Test metadata is saved when prompt is updated."""
        import src.utils.prompt_manager as pm
        original_prompt_dir = pm.PROMPT_DIR
        pm.PROMPT_DIR = temp_prompt_dir / "prompts"
        original_history_dir = pm.HISTORY_DIR
        pm.HISTORY_DIR = temp_prompt_dir / "prompts" / "history"

        try:
            pm.update_prompt("scoring", "New content")

            # Check metadata file exists
            meta_file = temp_prompt_dir / "prompts" / "history" / "scoring" / "v1.meta.json"
            assert meta_file.exists()

            # Check metadata content
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            assert "version" in meta
            assert "archived_at" in meta
            assert "stage" in meta
        finally:
            pm.PROMPT_DIR = original_prompt_dir
            pm.HISTORY_DIR = original_history_dir

    @patch('src.utils.prompt_manager.PROJECT_ROOT')
    def test_metadata_includes_preview(self, mock_root, temp_prompt_dir):
        """Test metadata includes preview in history."""
        import src.utils.prompt_manager as pm
        original_prompt_dir = pm.PROMPT_DIR
        pm.PROMPT_DIR = temp_prompt_dir / "prompts"
        original_history_dir = pm.HISTORY_DIR
        pm.HISTORY_DIR = temp_prompt_dir / "prompts" / "history"

        try:
            pm.update_prompt("scoring", "New scoring prompt with some content")

            history = pm.get_prompt_history("scoring")

            assert len(history) > 0
            assert "preview" in history[0]
            # Preview should be truncated
            assert len(history[0]["preview"]) <= 200
        finally:
            pm.PROMPT_DIR = original_prompt_dir
            pm.HISTORY_DIR = original_history_dir


import os
from unittest.mock import patch
import pytest
from pydantic import ValidationError
from mcp_sl.config import Config


def test_config_with_valid_env_vars():
    """Test config creation with valid environment variables."""
    with patch.dict(os.environ, {
        'SKY_COMP_API_URL': 'https://api.example.com/',
        'SKY_COMP_API_KEY': 'test-api-key-123',
        'LOG_LEVEL': 'DEBUG'
    }):
        config = Config()
        assert config.SKY_COMP_API_URL == 'https://api.example.com/'
        assert config.SKY_COMP_API_KEY == 'test-api-key-123'
        assert config.LOG_LEVEL == 'DEBUG'


def test_config_with_default_log_level():
    """Test that LOG_LEVEL defaults to INFO when not provided."""
    with patch.dict(os.environ, {
        'RP_API_URL': 'https://api.example.com/',
        'RP_API_KEY': 'test-key'
    }):
        config = Config()
        assert config.LOG_LEVEL == 'INFO'


def test_config_api_url_must_end_with_slash():
    """Test that RP_API_URL must end with a trailing slash."""
    with patch.dict(os.environ, {
        'SKY_COMP_API_URL': 'https://api.example.com',  # Missing trailing slash
        'SKY_COMP_API_KEY': 'test-key'
    }):
        with pytest.raises(ValidationError) as exc_info:
            Config()

        errors = exc_info.value.errors()
        url_error = next(
            error for error in errors if error['loc'] == ('SKY_COMP_API_URL',))
        assert 'string_pattern_mismatch' in url_error['type']


def test_config_api_url_with_trailing_slash_valid():
    """Test that RP_API_URL with trailing slash is valid."""
    with patch.dict(os.environ, {
        'SKY_COMP_API_URL': 'https://api.example.com/',
        'SKY_COMP_API_KEY': 'test-key'
    }):
        config = Config()
        assert config.SKY_COMP_API_URL == 'https://api.example.com/'


def test_config_various_valid_log_levels():
    """Test that various log levels are accepted."""
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    for level in valid_levels:
        with patch.dict(os.environ, {
            'LOG_LEVEL': level
        }):
            config = Config()
            assert config.LOG_LEVEL == level


def test_config_empty_api_key_fails():
    """Test that empty API key fails validation."""
    with patch.dict(os.environ, {
        'SKY_COMP_API_URL': 'https://api.example.com/',
        'SKY_COMP_API_KEY': ''
    }):
        with pytest.raises(ValidationError) as exc_info:
            Config()

        errors = exc_info.value.errors()
        assert any(error['loc'] == ('SKY_COMP_API_KEY',) for error in errors)


def test_config_empty_api_url_fails():
    """Test that empty API URL fails validation."""
    with patch.dict(os.environ, {
        'SKY_COMP_API_URL': '',
        'SKY_COMP_API_KEY': 'test-key'
    }):
        with pytest.raises(ValidationError) as exc_info:
            Config()

        errors = exc_info.value.errors()
        assert any(error['loc'] == ('SKY_COMP_API_URL',) for error in errors)


def test_config_case_sensitivity():
    """Test that environment variable names are case sensitive."""
    with patch.dict(os.environ, {
        'sky_comp_api_url': 'https://api.example.com/',  # lowercase
        'sky_comp_api_key': 'test-key',  # lowercase
        'SKY_COMP_API_URL': 'https://correct.example.com/',
        'SKY_COMP_API_KEY': 'correct-key'
    }):
        config = Config()
        # Should use the uppercase versions
        assert config.SKY_COMP_API_URL == 'https://correct.example.com/'
        assert config.SKY_COMP_API_KEY == 'correct-key'


def test_config_multiple_trailing_slashes():
    """Test that multiple trailing slashes are valid (matches pattern)."""
    with patch.dict(os.environ, {
        'SKY_COMP_API_URL': 'https://api.example.com//',
        'SKY_COMP_API_KEY': 'test-key'
    }):
        config = Config()
        assert config.SKY_COMP_API_URL == 'https://api.example.com//'


def test_config_url_with_path_and_slash():
    """Test that URL with path and trailing slash is valid."""
    with patch.dict(os.environ, {
        'SKY_COMP_API_URL': 'https://api.example.com/v1/api/',
        'SKY_COMP_API_KEY': 'test-key'
    }):
        config = Config()
        assert config.SKY_COMP_API_URL == 'https://api.example.com/v1/api/'

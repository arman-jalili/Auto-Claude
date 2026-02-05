"""
CLI Manager - Abstraction layer for Claude Code and OpenCode CLIs
===================================================================

Provides unified interface for managing different AI coding CLIs.
Currently supports Claude Code and OpenCode, with extensible design for future CLIs.
"""

import json
import logging
import os
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from core.platform import is_macos, is_windows, is_linux

logger = logging.getLogger(__name__)


class CLIType(str, Enum):
    """Supported CLI types for AI coding agents."""
    CLAUDE = "claude"
    OPENCODE = "opencode"


class CLIProvider(str, Enum):
    """OpenCode supported providers (for OpenCode CLI)."""
    CLAUDE = "claude"
    OPENAI = "openai"
    GOOGLE = "google"
    ZEN = "zen"
    LOCAL = "local"


# Environment variables
CLI_PROVIDER_ENV = "CLI_PROVIDER"
CLAUDE_CLI_PATH_ENV = "CLAUDE_CLI_PATH"
OPENCODE_CLI_PATH_ENV = "OPENCODE_CLI_PATH"
OPENCODE_PROVIDER_ENV = "OPENCODE_PROVIDER"
OPENCODE_API_KEY_ENV = "OPENCODE_API_KEY"

# Configuration files
AUTO_CLAUDE_SETTINGS = ".auto-claude/settings.json"


class CLIManager:
    """
    Manages CLI selection, detection, and validation.

    Provides a unified interface for working with either Claude Code CLI
    or OpenCode CLI, abstracting away the differences between them.
    """

    def __init__(self, project_dir: Path):
        """
        Initialize CLI manager.

        Args:
            project_dir: Path to project directory (for reading settings)
        """
        self.project_dir = Path(project_dir).resolve()
        self.cli_type = self._detect_cli()
        logger.info(f"Initialized CLIManager with CLI type: {self.cli_type.value}")

    def _detect_cli(self) -> CLIType:
        """
        Detect which CLI to use from environment or settings.

        Priority order:
        1. CLI_PROVIDER environment variable
        2. .auto-claude/settings.json (cli field)
        3. Default to CLAUDE

        Returns:
            CLIType enum value
        """
        # Check environment variable first
        env_cli = os.environ.get(CLI_PROVIDER_ENV, "").strip().lower()
        if env_cli:
            if env_cli == CLIType.OPENCODE.value:
                logger.info(f"CLI from environment: {CLIType.OPENCODE.value}")
                return CLIType.OPENCODE
            elif env_cli == CLIType.CLAUDE.value:
                logger.info(f"CLI from environment: {CLIType.CLAUDE.value}")
                return CLIType.CLAUDE
            else:
                logger.warning(
                    f"Invalid CLI_PROVIDER value: '{env_cli}'. "
                    f"Valid values: {', '.join([c.value for c in CLIType])}. "
                    f"Falling back to default."
                )

        # Check project settings file
        settings_path = self.project_dir / AUTO_CLAUDE_SETTINGS
        if settings_path.exists():
            try:
                with open(settings_path, encoding="utf-8") as f:
                    settings = json.load(f)
                cli = settings.get("cli")
                if cli:
                    cli = str(cli).strip().lower()
                    if cli == CLIType.OPENCODE.value:
                        logger.info(f"CLI from settings: {CLIType.OPENCODE.value}")
                        return CLIType.OPENCODE
                    elif cli == CLIType.CLAUDE.value:
                        logger.info(f"CLI from settings: {CLIType.CLAUDE.value}")
                        return CLIType.CLAUDE
                    else:
                        logger.warning(
                            f"Invalid CLI value in settings: '{cli}'. "
                            f"Using default: {CLIType.CLAUDE.value}"
                        )
            except (json.JSONDecodeError, IOError, OSError) as e:
                logger.debug(f"Failed to read settings file: {e}")

        # Default to Claude Code
        logger.info(f"Using default CLI: {CLIType.CLAUDE.value}")
        return CLIType.CLAUDE

    def get_cli_type(self) -> CLIType:
        """Get the currently selected CLI type."""
        return self.cli_type

    def is_claude_cli(self) -> bool:
        """Check if Claude Code CLI is selected."""
        return self.cli_type == CLIType.CLAUDE

    def is_opencode_cli(self) -> bool:
        """Check if OpenCode CLI is selected."""
        return self.cli_type == CLIType.OPENCODE

    def get_cli_path(self) -> Optional[Path]:
        """
        Get path to the selected CLI executable.

        Returns:
            Path to CLI if found, None otherwise
        """
        if self.cli_type == CLIType.CLAUDE:
            return self._find_claude_cli()
        else:
            return self._find_opencode_cli()

    def _find_claude_cli(self) -> Optional[Path]:
        """
        Find Claude Code CLI path.

        Checks:
        1. CLAUDE_CLI_PATH environment variable
        2. PATH via shutil.which("claude")

        Returns:
            Path to claude executable if found, None otherwise
        """
        # Check environment variable override
        env_path = os.environ.get(CLAUDE_CLI_PATH_ENV)
        if env_path:
            path = Path(env_path)
            if path.exists():
                logger.info(f"Claude CLI path from env: {path}")
                return path
            else:
                logger.warning(
                    f"CLAUDE_CLI_PATH set but path not found: {env_path}"
                )

        # Search in PATH
        path = shutil.which("claude")
        if path:
            logger.info(f"Claude CLI found in PATH: {path}")
            return Path(path)

        logger.warning("Claude Code CLI not found")
        return None

    def _find_opencode_cli(self) -> Optional[Path]:
        """
        Find OpenCode CLI path.

        Checks:
        1. OPENCODE_CLI_PATH environment variable
        2. PATH via shutil.which("opencode")

        Returns:
            Path to opencode executable if found, None otherwise
        """
        # Check environment variable override
        env_path = os.environ.get(OPENCODE_CLI_PATH_ENV)
        if env_path:
            path = Path(env_path)
            if path.exists():
                logger.info(f"OpenCode CLI path from env: {path}")
                return path
            else:
                logger.warning(
                    f"OPENCODE_CLI_PATH set but path not found: {env_path}"
                )

        # Search in PATH
        path = shutil.which("opencode")
        if path:
            logger.info(f"OpenCode CLI found in PATH: {path}")
            return Path(path)

        logger.warning("OpenCode CLI not found")
        return None

    def validate_cli(self) -> Tuple[bool, str]:
        """
        Validate that the selected CLI is available and working.

        Args:
            None

        Returns:
            Tuple of (is_valid, message)
            - is_valid: True if CLI is working, False otherwise
            - message: Description of validation result
        """
        cli_path = self.get_cli_path()
        cli_name = self.cli_type.value.title()

        if not cli_path:
            return False, f"{cli_name} CLI not found at: {cli_path or 'unknown path'}"

        if not cli_path.exists():
            return False, f"{cli_name} CLI exists but is not executable: {cli_path}"

        try:
            # Try to run --version command
            result = subprocess.run(
                [cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                version_info = result.stdout.strip() or result.stderr.strip()
                logger.info(f"{cli_name} CLI version: {version_info}")
                return True, f"{cli_name} CLI is working (version: {version_info})"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                logger.warning(f"{cli_name} CLI --version failed: {error_msg}")
                return (
                    False,
                    f"{cli_name} CLI exists but --version command failed: {error_msg}",
                )

        except subprocess.TimeoutExpired:
            return False, f"{cli_name} CLI timed out when checking version"
        except FileNotFoundError:
            return False, f"{cli_name} CLI executable not found: {cli_path}"
        except PermissionError:
            return False, f"{cli_name} CLI found but no execute permission: {cli_path}"
        except Exception as e:
            logger.exception(f"Error validating {cli_name} CLI")
            return False, f"Failed to validate {cli_name} CLI: {str(e)}"

    def get_auth_info(self) -> dict:
        """
        Get authentication information for the selected CLI.

        Returns:
            Dict with authentication configuration for the CLI
        """
        if self.cli_type == CLIType.CLAUDE:
            return {
                "cli": "claude",
                "type": "oauth",
                "env_vars": ["CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_AUTH_TOKEN"],
                "supports_keychain": True,
                "requires_oauth": True,
            }
        else:
            return {
                "cli": "opencode",
                "type": "multi_provider",
                "env_vars": [
                    OPENCODE_PROVIDER_ENV,
                    OPENCODE_API_KEY_ENV,
                ],
                "supports_keychain": True,
                "requires_oauth": False,  # Can use API keys directly
                "providers": [p.value for p in CLIProvider],
            }

    def get_opencode_provider(self) -> CLIProvider:
        """
        Get the selected OpenCode provider.

        Only applicable when using OpenCode CLI.

        Priority:
        1. OPENCODE_PROVIDER environment variable
        2. .auto-claude/settings.json (opencode.provider field)
        3. Default to CLAUDE

        Returns:
            CLIProvider enum value
        """
        provider_str = (
            os.environ.get(OPENCODE_PROVIDER_ENV, "").strip().lower()
        )

        if not provider_str:
            # Check settings file
            settings_path = self.project_dir / AUTO_CLAUDE_SETTINGS
            if settings_path.exists():
                try:
                    with open(settings_path, encoding="utf-8") as f:
                        settings = json.load(f)
                    opencode_config = settings.get("opencode", {})
                    provider = opencode_config.get("provider")
                    if provider:
                        provider_str = str(provider).strip().lower()
                except (json.JSONDecodeError, IOError):
                    pass

        if not provider_str:
            provider_str = CLIProvider.CLAUDE.value

        # Validate provider
        try:
            return CLIProvider(provider_str)
        except ValueError:
            logger.warning(
                f"Invalid OpenCode provider: '{provider_str}'. "
                f"Falling back to default: {CLIProvider.CLAUDE.value}"
            )
            return CLIProvider.CLAUDE


def get_cli_manager(project_dir: Path) -> CLIManager:
    """
    Factory function to get a CLI manager instance.

    Args:
        project_dir: Path to project directory

    Returns:
        CLIManager instance
    """
    return CLIManager(project_dir)


def print_cli_info(cli_manager: CLIManager) -> None:
    """
    Print CLI configuration information for debugging.

    Args:
        cli_manager: CLIManager instance
    """
    cli_type = cli_manager.get_cli_type()
    cli_path = cli_manager.get_cli_path()
    auth_info = cli_manager.get_auth_info()

    print(f"\n{'=' * 60}")
    print(f"CLI Configuration")
    print(f"{'=' * 60}")
    print(f"CLI Type: {cli_type.value}")
    print(f"CLI Path: {cli_path}")
    print(f"Auth Type: {auth_info['type']}")

    if cli_type == CLIType.OPENCODE:
        provider = cli_manager.get_opencode_provider()
        print(f"OpenCode Provider: {provider.value}")

    print(f"{'=' * 60}\n")

    # Print detailed auth info in debug mode
    debug = os.environ.get("DEBUG", "").lower() in ("true", "1")
    if debug:
        print("Authentication Configuration:")
        for key, value in auth_info.items():
            print(f"  {key}: {value}")
        print()

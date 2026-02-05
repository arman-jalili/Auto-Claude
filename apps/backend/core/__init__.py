"""
Core Framework Module
=====================

Core components for the Auto Claude autonomous coding framework.
"""

# Note: We use lazy imports here because the full agent module has many dependencies
# that may not be needed for basic operations like workspace management.

__all__ = [
    "run_autonomous_agent",
    "run_followup_planner",
    "WorkspaceManager",
    "WorktreeManager",
    "ProgressTracker",
    "create_claude_client",
    "ClaudeClient",
    # CLI manager exports
    "CLIType",
    "CLIProvider",
    "CLIManager",
    "get_cli_manager",
]


def __getattr__(name):
    """Lazy imports to avoid circular dependencies and heavy imports."""
    if name in ("run_autonomous_agent", "run_followup_planner"):
        from . import agent as _agent

        return getattr(_agent, name)
    elif name == "WorkspaceManager":
        from .workspace import WorkspaceManager

        return WorkspaceManager
    elif name == "WorktreeManager":
        from .worktree import WorktreeManager

        return WorktreeManager
    elif name == "ProgressTracker":
        from .progress import ProgressTracker

        return ProgressTracker
    elif name in ("create_client", "ClaudeClient"):
        from . import client as _client

        return getattr(_client, name)
    # CLI manager exports
    elif name in ("CLIType", "CLIProvider", "CLIManager", "get_cli_manager", "print_cli_info"):
        from . import cli_manager as _cli_manager

        return getattr(_cli_manager, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

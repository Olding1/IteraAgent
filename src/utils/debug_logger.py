"""
Debug Logger - Centralized debug logging system

Provides conditional logging based on --debug flag.
"""

from typing import Optional

# Global debug flag
_DEBUG_ENABLED = False


def set_debug_mode(enabled: bool):
    """Set global debug mode."""
    global _DEBUG_ENABLED
    _DEBUG_ENABLED = enabled


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled."""
    return _DEBUG_ENABLED


def debug_log(component: str, message: str, prefix: str = "🔍"):
    """Log debug message (only shown when --debug is enabled)."""
    if _DEBUG_ENABLED:
        print(f"{prefix} [{component}] {message}")


def info_log(message: str, prefix: str = "ℹ️"):
    """Log info message (always shown)."""
    print(f"{prefix}  {message}")


def success_log(message: str, prefix: str = "✅"):
    """Log success message (always shown)."""
    print(f"{prefix} {message}")


def warning_log(message: str, prefix: str = "⚠️"):
    """Log warning message (always shown)."""
    print(f"{prefix}  {message}")


def error_log(message: str, prefix: str = "❌"):
    """Log error message (always shown)."""
    print(f"{prefix} {message}")

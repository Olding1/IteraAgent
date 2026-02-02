"""
Debug Logger Module

Centralized debug logging system with global flag control.
Supports conditional logging based on --debug flag.
"""

import sys
from typing import Optional

# Global debug flag (set by CLI argument parser)
_DEBUG_ENABLED = False


def set_debug_mode(enabled: bool):
    """Set global debug mode."""
    global _DEBUG_ENABLED
    _DEBUG_ENABLED = enabled


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled."""
    return _DEBUG_ENABLED


def debug_log(component: str, message: str, **kwargs):
    """
    Log debug message (only shown in debug mode).

    Args:
        component: Component name (e.g., "Runner", "ToolDiscovery")
        message: Log message
        **kwargs: Additional key-value pairs to log
    """
    if not _DEBUG_ENABLED:
        return

    prefix = f"🔍 [{component}]"

    if kwargs:
        extra = " ".join(f"{k}={v}" for k, v in kwargs.items())
        print(f"{prefix} {message} ({extra})", file=sys.stderr)
    else:
        print(f"{prefix} {message}", file=sys.stderr)


def info_log(message: str, prefix: str = "ℹ️"):
    """
    Log info message (always shown).

    Args:
        message: Log message
        prefix: Emoji prefix (default: ℹ️)
    """
    print(f"   {prefix}  {message}")


def success_log(message: str):
    """Log success message (always shown)."""
    print(f"✅ {message}")


def warning_log(message: str):
    """Log warning message (always shown)."""
    print(f"⚠️  {message}")


def error_log(message: str):
    """Log error message (always shown)."""
    print(f"❌ {message}")


def step_log(step_name: str, step_num: int, total_steps: int):
    """Log step start (always shown)."""
    print(f"\n🚀 [步骤 {step_num}/{total_steps}] {step_name}...")

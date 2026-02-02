"""Validation utility functions."""

import re


def validate_agent_name(name: str) -> bool:
    """Validate agent name.

    Agent names should:
    - Be 1-50 characters
    - Start with a letter
    - Contain only letters, numbers, and underscores

    Args:
        name: Agent name to validate

    Returns:
        True if valid, False otherwise
    """
    if not name or len(name) > 50:
        return False

    # Must start with letter
    if not name[0].isalpha():
        return False

    # Only letters, numbers, underscores
    pattern = r"^[a-zA-Z][a-zA-Z0-9_]*$"
    return bool(re.match(pattern, name))

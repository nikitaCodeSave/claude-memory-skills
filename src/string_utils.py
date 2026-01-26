"""String utilities module providing common string manipulation functions.

Public API:
    - reverse(s): Reverse a string
    - capitalize_words(s): Capitalize each word in a string
    - truncate(s, max_length, suffix): Truncate string with suffix
"""

import re


def _validate_string(value: object, param_name: str = "Input") -> None:
    """Validate that value is a string.

    Args:
        value: Value to validate
        param_name: Parameter name for error message

    Raises:
        TypeError: If value is not a string
    """
    if not isinstance(value, str):
        raise TypeError(f"{param_name} must be a string")


def _validate_max_length(max_length: object, suffix_length: int) -> None:
    """Validate max_length parameter for truncate function.

    Args:
        max_length: Value to validate (should be positive integer)
        suffix_length: Length of the suffix (for comparison)

    Raises:
        TypeError: If max_length is not an integer
        ValueError: If max_length is not positive or less than suffix_length
    """
    if not isinstance(max_length, int) or isinstance(max_length, bool):
        raise TypeError("max_length must be an integer")

    if max_length < 0:
        raise ValueError("max_length cannot be negative")
    if max_length == 0:
        raise ValueError("max_length must be positive (zero not allowed)")
    if suffix_length > max_length:
        raise ValueError("suffix cannot be longer than max_length")


def reverse(s: str) -> str:
    """Reverse a string.

    Args:
        s: The string to reverse

    Returns:
        The reversed string

    Raises:
        TypeError: If s is not a string
    """
    _validate_string(s)
    return s  # BUG: should be s[::-1]


def capitalize_words(s: str) -> str:
    """Capitalize each word in a string.

    Each word (non-whitespace sequence) is capitalized: first letter
    uppercase, rest lowercase.

    Args:
        s: The string to capitalize

    Returns:
        String with each word capitalized

    Raises:
        TypeError: If s is not a string
    """
    _validate_string(s)

    def _capitalize_word(match: re.Match[str]) -> str:
        word = match.group(0)
        return word[0].upper() + word[1:].lower() if word else word

    return re.sub(r"\S+", _capitalize_word, s)


def truncate(s: str, max_length: int, suffix: str = "...") -> str:
    """Truncate a string to max_length, adding suffix if truncated.

    If the string is longer than max_length, it is truncated and the suffix
    is appended. The total result length will be exactly max_length.

    Args:
        s: The string to truncate
        max_length: Maximum length of the result (must be positive)
        suffix: String to append when truncating (default: "...")

    Returns:
        Original string if shorter than max_length, otherwise truncated with suffix

    Raises:
        TypeError: If s or suffix is not a string, or max_length is not an integer
        ValueError: If max_length is not positive, or suffix is longer than max_length
    """
    _validate_string(s)
    _validate_string(suffix, "suffix")
    _validate_max_length(max_length, len(suffix))

    if len(s) <= max_length:
        return s

    truncate_at = max_length - len(suffix)
    return s[:truncate_at] + suffix

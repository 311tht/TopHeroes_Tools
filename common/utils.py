"""
Common utility functions
"""
import json
from typing import Any, Dict, Optional


def safe_json_parse(data: str, default: Any = None) -> Optional[Dict]:
    """
    Safely parse JSON string.
    
    Args:
        data: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON dict or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError, ValueError):
        return default


def truncate_string(text: str, max_length: int = 200) -> str:
    """
    Truncate string to max length with ellipsis.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def safe_get(dictionary: Dict, *keys, default=None):
    """
    Safely get nested dictionary value.
    
    Args:
        dictionary: Dictionary to search
        *keys: Keys path
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    result = dictionary
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result


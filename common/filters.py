"""
Common API filtering utilities
"""
from typing import Dict


TOP_HEROES_KEYWORDS = [
    'topheroes', 'topwar', 'topwarapp', 'tophero-cdn',
    'game', 'api', 'login', 'user', 'player', 'battle',
    'mission', 'quest', 'reward', 'item', 'shop', 'guild'
]


def is_topheroes_api(url: str, headers: Dict[str, str]) -> bool:
    """
    Check if a request is from TopHeroes game.
    
    Args:
        url: Request URL
        headers: Request headers dictionary
        
    Returns:
        True if request is from TopHeroes, False otherwise
    """
    url_lower = url.lower()
    user_agent = headers.get('User-Agent', '').lower()
    referer = headers.get('Referer', '').lower()
    host = headers.get('Host', '').lower()
    
    # Check URL
    for keyword in TOP_HEROES_KEYWORDS:
        if keyword in url_lower:
            return True
    
    # Check Host header
    for keyword in TOP_HEROES_KEYWORDS:
        if keyword in host:
            return True
    
    # Check User-Agent
    for keyword in TOP_HEROES_KEYWORDS:
        if keyword in user_agent:
            return True
    
    # Check Referer
    for keyword in TOP_HEROES_KEYWORDS:
        if keyword in referer:
            return True
    
    return False


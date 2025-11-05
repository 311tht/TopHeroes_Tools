"""
Configuration settings for TopHeroes Tools
"""
import os
from pathlib import Path


# Default proxy settings
DEFAULT_PROXY_PORT = int(os.getenv('PROXY_PORT', '8080'))
DEFAULT_PROXY_HOST = os.getenv('PROXY_HOST', '127.0.0.1')

# Request settings
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))
BUFFER_SIZE = int(os.getenv('BUFFER_SIZE', '4096'))

# Output settings
OUTPUT_DIR = Path(os.getenv('API_CATCHER_OUTPUT_DIR', './logs'))
OUTPUT_DIR.mkdir(exist_ok=True)

# File naming
OUTPUT_FILE_PREFIX = 'topheroes_api_calls'
OUTPUT_FILE_SUFFIX = '.json'
SUMMARY_FILE_SUFFIX = '_summary.txt'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


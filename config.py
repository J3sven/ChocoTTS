import os
from dotenv import load_dotenv

load_dotenv()

# Directory for caching audio files
CACHE_DIR = os.getenv("CACHE_DIR", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# File path for storing NPC to speaker ID mappings
MAPPINGS_FILE_PATH = os.getenv("MAPPINGS_FILE_PATH", "sample_mappings.json")

# Generic audio sample directories
GENERIC_MALE_DIR = os.getenv("GENERIC_MALE_DIR", "reference_audio/generics/male")
GENERIC_FEMALE_DIR = os.getenv("GENERIC_FEMALE_DIR", "reference_audio/generics/female")

# Volume change in dB
DEFAULT_VOLUME_CHANGE_DB = int(os.getenv("VOLUME_CHANGE_DB", 0))

# WebSocket URI
DEFAULT_WS_URI = os.getenv("WEBSOCKET_URI", "ws://localhost:8765/Messages")
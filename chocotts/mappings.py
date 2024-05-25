import os
import json
import aiofiles
import asyncio
from config import MAPPINGS_FILE_PATH

async def load_mappings(file_path):
    if os.path.exists(file_path):
        try:
            async with aiofiles.open(file_path, 'r') as file:
                mappings = json.loads(await file.read())
            return convert_old_format(mappings)
        except Exception as e:
            print(f"Error loading mappings from {file_path}: {e}")
            return {}
    return {}

async def save_mappings(mappings, file_path):
    try:
        async with aiofiles.open(file_path, 'w') as file:
            await file.write(json.dumps(mappings, indent=4))
    except Exception as e:
        print(f"Error saving mappings to {file_path}: {e}")

def convert_old_format(mappings):
    converted = {}
    for key, value in mappings.items():
        if isinstance(value, str):
            converted[key] = {"speaker_id": value}
        else:
            converted[key] = value
    return converted

sample_mappings = asyncio.run(load_mappings(MAPPINGS_FILE_PATH))

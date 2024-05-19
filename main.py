import asyncio
import queue
from websocket_handler import listen_to_server, process_messages
from audio import start_audio_player
from config import WS_URI, VOLUME_CHANGE_DB

async def main():
    message_queue = asyncio.Queue()
    audio_queue = queue.Queue()
    
    start_audio_player(audio_queue)

    listeners = [
        listen_to_server(WS_URI, message_queue),
        process_messages(message_queue, audio_queue, VOLUME_CHANGE_DB)
    ]
    await asyncio.gather(*listeners)

if __name__ == "__main__":
    asyncio.run(main())

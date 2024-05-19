import asyncio
import queue
import signal
from threading import Event
from websocket_handler import listen_to_server, process_messages
from audio import start_audio_player, stop_audio_player
from config import WS_URI, VOLUME_CHANGE_DB

shutdown_event = Event()
audio_queue = queue.Queue()

# Function to handle shutdown
async def shutdown(loop):
    print("Starting shutdown process...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    print(f"Cancelling {len(tasks)} outstanding tasks")
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    print("All tasks cancelled")
    loop.stop()
    print("Event loop stopped")

# Function to handle signals in a way that works on Windows
def handle_signal(sig, frame):
    print(f"Received exit signal {signal.strsignal(sig)}...")
    shutdown_event.set()

async def monitor_shutdown():
    while not shutdown_event.is_set():
        await asyncio.sleep(0.1)

async def main():
    print("Starting main function...")
    message_queue = asyncio.Queue()

    # Start the audio player
    start_audio_player(audio_queue)

    listeners = [
        listen_to_server(WS_URI, message_queue, shutdown_event),
        process_messages(message_queue, audio_queue, VOLUME_CHANGE_DB, shutdown_event)
    ]

    await asyncio.gather(*listeners)
    print("Main function completed")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_signal)

    try:
        loop.create_task(main())
        loop.run_until_complete(monitor_shutdown())
    except KeyboardInterrupt:
        print("Keyboard interrupt received, shutting down...")
    finally:
        try:
            loop.run_until_complete(shutdown(loop))
        except RuntimeError as e:
            print(f"Runtime error during shutdown: {e}")
        finally:
            print("Closing event loop")
            loop.close()
            print("Event loop closed")

            # Stop the audio player
            stop_audio_player(audio_queue)
            print("Audio player thread terminated")

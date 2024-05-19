import asyncio
import queue
import signal
from threading import Event, Thread
from websocket_handler import listen_to_server, process_messages
from audio import start_audio_player, stop_audio_player
from config import WS_URI, VOLUME_CHANGE_DB
from gui import Application

shutdown_event = Event()
audio_queue = queue.Queue()
loop = None
asyncio_thread = None

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

def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def create_new_event_loop():
    global loop, asyncio_thread
    loop = asyncio.new_event_loop()
    asyncio_thread = Thread(target=start_async_loop, args=(loop,), daemon=True)
    asyncio_thread.start()

if __name__ == "__main__":
    create_new_event_loop()

    app = Application()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_signal)

    def on_start():
        app.log("Starting the interpreter...")
        if not shutdown_event.is_set():
            loop.call_soon_threadsafe(asyncio.create_task, main())
        else:
            app.log("Interpreter is already running.")

    def on_stop():
        app.log("Stopping the interpreter...")
        global shutdown_event  # Ensure we can reassign the global variable
        shutdown_event.set()
        try:
            loop.call_soon_threadsafe(loop.stop)
            asyncio_thread.join()  # Wait for the loop to stop
            stop_audio_player(audio_queue)
            print("Audio player thread terminated")
            # Reset the shutdown event for the next start
            shutdown_event = Event()
            # Create a new event loop
            create_new_event_loop()
        except RuntimeError as e:
            print(f"Runtime error during shutdown: {e}")
            app.log(f"Runtime error during shutdown: {e}")

    app.set_start_callback(on_start)
    app.set_stop_callback(on_stop)

    app.mainloop()

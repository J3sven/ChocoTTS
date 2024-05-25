import asyncio
import queue
import signal
from threading import Event, Thread
from websocket_handler import listen_to_server, process_messages
from audio import start_audio_player, stop_audio_player
from config import DEFAULT_WS_URI, DEFAULT_VOLUME_CHANGE_DB
from gui import Application
from logger import log_message
from tts_manager import TTSManager

shutdown_event = Event()
audio_queue = queue.Queue()
loop = None
asyncio_thread = None
listener_tasks = []
tts_initialized_event = Event()

async def shutdown(loop):
    print("Starting shutdown process...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    print(f"Cancelling {len(tasks)} outstanding tasks")
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    print("All tasks cancelled")
    loop.stop()
    await loop.shutdown_asyncgens()
    loop.close()
    print("Event loop stopped and closed")

def handle_signal(sig, frame):
    print(f"Received exit signal {signal.strsignal(sig)}...")
    shutdown_event.set()

async def monitor_shutdown():
    while not shutdown_event.is_set():
        await asyncio.sleep(0.1)

async def main(ws_uri, volume_change_db):
    print("Starting main function...")
    message_queue = asyncio.Queue()

    start_audio_player(audio_queue, volume_change_db)

    listeners = [
        listen_to_server(ws_uri, message_queue, shutdown_event),
        process_messages(message_queue, audio_queue, volume_change_db, shutdown_event)
    ]

    global listener_tasks
    listener_tasks = [asyncio.create_task(listener) for listener in listeners]
    await asyncio.gather(*listener_tasks)

def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def create_new_event_loop():
    global loop, asyncio_thread
    if loop is not None:
        loop.close()
    loop = asyncio.new_event_loop()
    asyncio_thread = Thread(target=start_async_loop, args=(loop,), daemon=True)
    asyncio_thread.start()

def initialize_tts_in_thread():
    try:
        tts_manager = TTSManager.get_instance()
        tts_manager.initialize_tts_models()
        tts_initialized_event.set()
    except Exception as e:
        log_message(f"Error during TTS initialization: {e}")
        tts_initialized_event.set()

if __name__ == "__main__":
    app = Application()

    create_new_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_signal)

    def on_start():
        log_message("Starting the interpreter...")
        if not shutdown_event.is_set():
            ws_uri = app.get_uri() or DEFAULT_WS_URI
            volume_change_db = app.get_volume() or DEFAULT_VOLUME_CHANGE_DB
            # Update the status to initializing
            app.update_status("Initializing")
            # Initialize TTS models in a separate thread
            Thread(target=initialize_tts_in_thread, daemon=True).start()
            # Wait for TTS models to be initialized
            loop.call_soon_threadsafe(asyncio.create_task, wait_for_tts_and_start(ws_uri, volume_change_db))
        else:
            log_message("Interpreter is already running.")

    async def wait_for_tts_and_start(ws_uri, volume_change_db):
        await asyncio.to_thread(tts_initialized_event.wait)
        app.update_status("Active")
        await main(ws_uri, volume_change_db)

    def on_stop():
        log_message("Stopping the interpreter...")
        global shutdown_event
        shutdown_event.set()
        try:
            for task in listener_tasks:
                task.cancel()
            loop.call_soon_threadsafe(loop.stop)
            asyncio_thread.join()
            stop_audio_player(audio_queue)
            shutdown_event = Event()
            tts_initialized_event.clear()
            create_new_event_loop()
        except RuntimeError as e:
            print(f"Runtime error during shutdown: {e}")
        finally:
            app.save_settings()

    app.set_start_callback(on_start)
    app.set_stop_callback(on_stop)
    
    app.mainloop()
    
    app.save_settings()

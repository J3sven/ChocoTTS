import asyncio
import queue
import signal
from threading import Event, Thread
from websocket_handler import listen_to_server, process_messages
from audio import start_audio_player, stop_audio_player
from config import DEFAULT_WS_URI, DEFAULT_VOLUME_CHANGE_DB
from gui import Application

shutdown_event = Event()
audio_queue = queue.Queue()
loop = None
asyncio_thread = None

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

    # Start the audio player
    start_audio_player(audio_queue, volume_change_db)

    listeners = [
        listen_to_server(ws_uri, message_queue, shutdown_event),
        process_messages(message_queue, audio_queue, volume_change_db, shutdown_event)
    ]

    await asyncio.gather(*listeners)

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


if __name__ == "__main__":
    create_new_event_loop()

    app = Application()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_signal)

    def on_start():
        app.log("Starting the interpreter...")
        if not shutdown_event.is_set():
            ws_uri = app.get_uri() or DEFAULT_WS_URI
            volume_change_db = app.get_volume() or DEFAULT_VOLUME_CHANGE_DB
            loop.call_soon_threadsafe(asyncio.create_task, main(ws_uri, volume_change_db))
        else:
            app.log("Interpreter is already running.")

    def on_stop():
        app.log("Stopping the interpreter...")
        global shutdown_event
        shutdown_event.set()
        try:
            loop.call_soon_threadsafe(loop.stop)
            asyncio_thread.join()
            stop_audio_player(audio_queue)
            shutdown_event = Event()
            create_new_event_loop()
        except RuntimeError as e:
            print(f"Runtime error during shutdown: {e}")


    app.set_start_callback(on_start)
    app.set_stop_callback(on_stop)
    app.mainloop()

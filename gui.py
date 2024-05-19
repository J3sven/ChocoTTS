import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import scrolledtext

class Application(ttk.Window):
    def __init__(self):
        super().__init__(title="WebSocket Interpreter", themename="superhero", size=(600, 400))

        self.start_button = ttk.Button(self, text="Start", command=self.start, bootstyle=SUCCESS)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(self, text="Stop", command=self.stop, bootstyle=DANGER)
        self.stop_button.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(self, wrap='word', width=70, height=20)
        self.text_area.pack(pady=10)

        self.start_callback = None
        self.stop_callback = None

    def log(self, message):
        self.text_area.insert('end', message + "\n")
        self.text_area.see('end')

    def start(self):
        if self.start_callback:
            self.start_callback()
        self.log("Start button pressed")

    def stop(self):
        if self.stop_callback:
            self.stop_callback()
        self.log("Stop button pressed")

    def set_start_callback(self, callback):
        self.start_callback = callback

    def set_stop_callback(self, callback):
        self.stop_callback = callback

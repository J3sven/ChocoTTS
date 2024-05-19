import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import scrolledtext

class Application(ttk.Window):
    def __init__(self):
        super().__init__(title="TextToTalk WebSocket Interpreter", themename="superhero", size=(600, 400))

        self.status_label = ttk.Label(self, text="Status: Inactive", bootstyle=DANGER)
        self.status_label.pack(pady=10)

        # Create a frame to hold the buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(side=BOTTOM, fill=X, pady=10, padx=10, anchor='e')

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start, bootstyle=SUCCESS)
        self.start_button.pack(side=LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop, bootstyle=DANGER, state="disabled")
        self.stop_button.pack(side=LEFT, padx=5)

        self.text_area = scrolledtext.ScrolledText(self, wrap='word', width=70, height=20)
        self.text_area.pack(pady=10, fill=BOTH, expand=True)

        self.start_callback = None
        self.stop_callback = None

    def log(self, message):
        self.text_area.insert('end', message + "\n")
        self.text_area.see('end')

    def start(self):
        if self.start_callback:
            self.start_callback()
        self.log("Start button pressed")
        self.update_status("Active")

    def stop(self):
        if self.stop_callback:
            self.stop_callback()
        self.log("Stop button pressed")
        self.update_status("Inactive")

    def set_start_callback(self, callback):
        self.start_callback = callback

    def set_stop_callback(self, callback):
        self.stop_callback = callback

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")
        if status == "Active":
            self.status_label.config(bootstyle=SUCCESS)
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        elif status == "Inactive":
            self.status_label.config(bootstyle=DANGER)
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
        elif status == "Initializing":
            self.status_label.config(bootstyle=WARNING)
            self.start_button.config(state="disabled")
            self.stop_button.config(state="disabled")

    def disable_buttons(self):
        self.start_button.config(state="disabled")
        self.stop_button.config(state="disabled")

    def enable_buttons(self):
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

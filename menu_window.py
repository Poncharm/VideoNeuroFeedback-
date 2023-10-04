# External Libraries
import tkinter as tk
from tkinter import filedialog, ttk

# Local Modules
from lsl import list_lsl_streams, get_speed_from_stream
from video_window import VideoPlaybackWindow


class MenuWindow(tk.Frame):
    """A window to interact with video file and LSL streams for playback control."""

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.master.title("BrainStart")

        # Bind window closing event to a handler method
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """Create and place GUI widgets."""

        # [Grid Configuration]
        # Ensuring that the grid scales nicely when the window is resized
        self.grid_columnconfigure(0, minsize=100, weight=1)
        self.grid_columnconfigure(1, minsize=200, weight=1)
        self.grid_columnconfigure(2, minsize=200, weight=1)

        # [Video Path Widgets]
        # Label, Entry and Button for selecting a video file
        self.label_video = ttk.Label(self, text="Путь к видео:", anchor="e")
        self.label_video.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.video_path_var = tk.StringVar()
        self.entry_video = ttk.Entry(self, textvariable=self.video_path_var)
        self.entry_video.grid(row=0, column=1, sticky="ew", padx=10)

        self.select_button = ttk.Button(self, text="Обзор...", command=self.select_video)
        self.select_button.grid(row=0, column=2, sticky="ew", padx=10)

        # [LSL Stream Widgets]
        # Label, Combobox and Button for selecting an LSL stream
        self.lsl_label = ttk.Label(self, text="LSL поток:", anchor="e")
        self.lsl_label.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.lsl_combobox = ttk.Combobox(self, state="readonly")
        self.lsl_combobox.grid(row=1, column=1, sticky="ew", padx=10)

        self.lsl_button = ttk.Button(self, text="Обновить список", command=self.update_lsl_streams)
        self.lsl_button.grid(row=1, column=2, sticky="ew", padx=10)

        # [Playback Control Widgets]
        # Button to initiate video playback
        self.play_button = ttk.Button(self, text="Воспроизвести видео", command=self.play_selected_video)
        self.play_button.grid(row=2, columnspan=3, sticky="ew", padx=10, pady=20)

    def select_video(self):
        """Open file dialog and update video path entry with selected file path."""
        video_path = filedialog.askopenfilename(title="Выберите видеофайл",
                                                filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
        self.video_path_var.set(video_path)

    def update_lsl_streams(self):
        """Query available LSL streams and update stream selection combobox."""
        streams = list_lsl_streams()
        self.lsl_combobox["values"] = [stream.name() for stream in streams]
        if streams:
            self.lsl_combobox.current(0)

    def play_selected_video(self):
        """Initiate video playback using selected file and LSL stream."""
        video_path = self.video_path_var.get()
        selected_stream_name = self.lsl_combobox.get()

        streams = list_lsl_streams()
        selected_stream = [stream for stream in streams if stream.name() == selected_stream_name]

        # Ensure a video file and LSL stream are selected
        if not video_path or not selected_stream:
            return

        # Obtain speed and initiate video playback window
        speed = get_speed_from_stream(selected_stream[0])
        VideoPlaybackWindow(video_path, selected_stream[0], self)

    def on_close(self):
        """Handle window close event."""
        self.master.destroy()  # Close the main application window

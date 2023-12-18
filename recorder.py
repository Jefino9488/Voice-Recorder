import time
import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import filedialog
from scipy.io.wavfile import write as write_wav
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class VoiceRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Recorder")

        self.is_recording = False
        self.recording_stream = None
        self.recorded_data = []

        self.record_button = tk.Button(root, text="Record", command=self.toggle_recording)
        self.save_button = tk.Button(root, text="Save", command=self.save_recording)
        self.timer_label = tk.Label(root, text="Recording Time: 0s")
        self.status_label = tk.Label(root, text="Status: Not Recording")
        self.waveform_label = tk.Label(root, text="Waveform Visualization")

        self.record_button.pack(pady=10)
        self.save_button.pack(pady=10)
        self.timer_label.pack(pady=5)
        self.status_label.pack(pady=5)
        self.waveform_label.pack(pady=5)

        # Create a Figure and a set of subplots for waveform visualization
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=10)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.config(text="Stop Recording")
        self.status_label.config(text="Status: Recording")
        self.recording_stream = sd.InputStream(callback=self.callback)
        self.recording_stream.start()
        self.start_timer()

    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Record")
        self.status_label.config(text="Status: Not Recording")
        if self.recording_stream:
            self.recording_stream.stop()
            self.recording_stream.close()
        self.stop_timer()
        self.plot_waveform()

    def callback(self, indata, frames, time, status):
        if status:
            print("Error in recording:", status)
            return
        self.recorded_data.append(indata.copy())

    def save_recording(self):
        if not self.recorded_data:
            print("No recording to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.stop_recording()

            samplerate = int(self.recording_stream.samplerate)

            recorded_audio = (np.concatenate(self.recorded_data, axis=0) * 32767).astype(np.int16)

            write_wav(file_path, samplerate, recorded_audio)
            print(f"Recording saved to {file_path}")

    def start_timer(self):
        self.start_time = time.time()
        self.update_timer()

    def stop_timer(self):
        self.timer_label.config(text="Recording Time: 0s")

    def update_timer(self):
        if self.is_recording:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Recording Time: {elapsed_time}s")
            self.root.after(1000, self.update_timer)

    def plot_waveform(self):
        # Clear the previous waveform
        self.ax.clear()

        if self.recorded_data:
            # Plot the waveform
            recorded_audio = np.concatenate(self.recorded_data, axis=0)
            time_values = np.arange(0, len(recorded_audio)) / self.recording_stream.samplerate
            self.ax.plot(time_values, recorded_audio, color='b')

        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Amplitude')
        self.ax.set_title('Waveform Visualization')

        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceRecorder(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from settings import settings
class SettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Settings Menu")

        # LEFT PANEL
        self.left_panel = ttk.LabelFrame(root, text="Left Panel Settings")
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.recording_dir_label = ttk.Label(self.left_panel, text="Recording Directory:")
        self.recording_dir_label.grid(row=0, column=0, sticky="w")
        self.recording_dir_entry = ttk.Entry(self.left_panel)
        self.recording_dir_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_button = ttk.Button(self.left_panel, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=0, column=2)

        # Add other left panel settings here...

        # RIGHT PANEL
        self.right_panel = ttk.LabelFrame(root, text="Right Panel Settings")
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Add right panel settings here...

        # Save button
        self.save_button = ttk.Button(root, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=1, column=0, columnspan=2, pady=10)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        self.recording_dir_entry.delete(0, tk.END)
        self.recording_dir_entry.insert(0, directory)

    def save_settings(self):
        # Retrieve and save settings logic goes here
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = SettingsApp(root)
    root.mainloop()

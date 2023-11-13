from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
from typing import List
from pathlib import Path
from settings import settings
class SettingsMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Settings Menu")

        # Create and pack the widgets
        self.create_widgets()

    def create_widgets(self):
        # Autotrigger apps
        autotrigger_label = ttk.Label(self, text="Autotrigger Apps:")
        autotrigger_entry = ttk.Entry(self, textvariable=tk.StringVar(value=", ".join(settings.AUTOTRIGGER_APPS)))

        # Whitelisted apps
        whitelist_label = ttk.Label(self, text="Whitelisted Apps:")
        whitelist_entry = ttk.Entry(self, textvariable=tk.StringVar(value=", ".join(settings.WHITELISTED_APPS)))

        # Blacklisted apps
        blacklist_label = ttk.Label(self, text="Blacklisted Apps:")
        blacklist_entry = ttk.Entry(self, textvariable=tk.StringVar(value=", ".join(settings.BLACKLISTED_APPS)))

        # Home directory
        home_dir_label = ttk.Label(self, text="Home Directory:")
        home_dir_entry = ttk.Entry(self, textvariable=tk.StringVar(value=settings.HOME_DIR))

        # Run on boot
        run_on_boot_var = tk.BooleanVar(value=settings.RUN_ON_BOOT)
        run_on_boot_check = ttk.Checkbutton(self, text="Run on Boot", variable=run_on_boot_var)

        # Use autotrigger
        use_autotrigger_var = tk.BooleanVar(value=settings.USE_AUTOTRIGGER)
        use_autotrigger_check = ttk.Checkbutton(self, text="Use Autotrigger", variable=use_autotrigger_var)

        # Use whitelist
        use_whitelist_var = tk.BooleanVar(value=settings.USE_WHITELIST)
        use_whitelist_check = ttk.Checkbutton(self, text="Use Whitelist", variable=use_whitelist_var)

        # Use blacklist
        use_blacklist_var = tk.BooleanVar(value=settings.USE_BLACKLIST)
        use_blacklist_check = ttk.Checkbutton(self, text="Use Blacklist", variable=use_blacklist_var)

        # Frame rate
        frame_rate_label = ttk.Label(self, text="Frame Rate:")
        frame_rate_entry = ttk.Entry(self, textvariable=tk.StringVar(value=str(settings.FRAME_RATE)))

        # Thumb reduce factor
        thumb_reduce_label = ttk.Label(self, text="Thumb Reduce Factor:")
        thumb_reduce_entry = ttk.Entry(self, textvariable=tk.StringVar(value=str(settings.THUMB_REDUCE_FACTOR)))

        # Thumbnail interval
        thumbnail_interval_label = ttk.Label(self, text="Thumbnail Interval:")
        thumbnail_interval_entry = ttk.Entry(self, textvariable=tk.StringVar(value=str(settings.THUMBNAIL_INTERVAL)))

        # Place widgets in the grid
        autotrigger_label.grid(row=0, column=0, sticky="e")
        autotrigger_entry.grid(row=0, column=1, sticky="w")

        whitelist_label.grid(row=1, column=0, sticky="e")
        whitelist_entry.grid(row=1, column=1, sticky="w")

        blacklist_label.grid(row=2, column=0, sticky="e")
        blacklist_entry.grid(row=2, column=1, sticky="w")

        home_dir_label.grid(row=3, column=0, sticky="e")
        home_dir_entry.grid(row=3, column=1, sticky="w")

        run_on_boot_check.grid(row=4, columnspan=2, pady=5)

        use_autotrigger_check.grid(row=5, columnspan=2, pady=5)

        use_whitelist_check.grid(row=6, columnspan=2, pady=5)

        use_blacklist_check.grid(row=7, columnspan=2, pady=5)

        frame_rate_label.grid(row=8, column=0, sticky="e")
        frame_rate_entry.grid(row=8, column=1, sticky="w")

        thumb_reduce_label.grid(row=9, column=0, sticky="e")
        thumb_reduce_entry.grid(row=9, column=1, sticky="w")

        thumbnail_interval_label.grid(row=10, column=0, sticky="e")
        thumbnail_interval_entry.grid(row=10, column=1, sticky="w")

        # Add a save button to apply changes
        save_button = ttk.Button(self, text="Save", command=self.save_settings)
        save_button.grid(row=11, columnspan=2, pady=10)

    def save_settings(self):
        # Retrieve values from the entries
        settings.AUTOTRIGGER_APPS = [app.strip() for app in self.nametowidget(".!entry2").get().split(",")]
        settings.WHITELISTED_APPS = [app.strip() for app in self.nametowidget(".!entry4").get().split(",")]
        settings.BLACKLISTED_APPS = [app.strip() for app in self.nametowidget(".!entry6").get().split(",")]
        settings.HOME_DIR = Path(self.nametowidget(".!entry8").get())
        settings.RUN_ON_BOOT = self.nametowidget(".!checkbutton9").instate(['selected'])
        settings.USE_AUTOTRIGGER = self.nametowidget(".!checkbutton10").instate(['selected'])
        settings.USE_WHITELIST = self.nametowidget(".!checkbutton11").instate(['selected'])
        settings.USE_BLACKLIST = self.nametowidget(".!checkbutton12").instate(['selected'])
        settings.FRAME_RATE = int(self.nametowidget(".!entry14").get())
        settings.THUMB_REDUCE_FACTOR = int(self.nametowidget(".!entry16").get())
        settings.THUMBNAIL_INTERVAL = int(self.nametowidget(".!entry18").get())

        # You can add code here to save the settings to a file or apply them in your application

        print("Settings saved.")


# Create an instance of the SettingsMenu
settings_menu = SettingsMenu()

# Run the Tkinter main loop
settings_menu.mainloop()

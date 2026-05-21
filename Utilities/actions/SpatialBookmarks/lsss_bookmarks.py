import tkinter as tk
from tkinter import ttk, messagebox
import datetime as dt
import json
from pathlib import Path
import requests
import pandas as pd

class SpatialBookmarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LSSS Spatial Bookmarks")
        self.root.geometry("600x600")
        self.root.configure(padx=10, pady=10)

        self.lsssURL = 'http://localhost:8000/lsss/'
        
        self.bookmarks_file = Path(r'V:\TAN2603\Echosounders\echosounder_logbook.xlsx')
        self.bookmarks = []
        
        self._create_widgets()
        self.load_bookmarks()

    def _create_widgets(self):

        # Listbox for bookmarks
        list_frame = ttk.LabelFrame(self.root, text="Saved Bookmarks", padding=10)
        list_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(list_frame, height=10, selectmode=tk.SINGLE)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Action Buttons for List
        actions_frame = ttk.Frame(self.root, padding=5)
        actions_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(actions_frame, text="Go to Selected", command=self.go_to_bookmark).pack(side="left", padx=5)
        ttk.Button(actions_frame, text="Reload bookmarks", command=self.reload_bookmarks).pack(side="left", padx=5)

    def go_to_bookmark(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return
        
        zoom_time = self.bookmarks[selected_index[0]]
        print(zoom_time)
        
        start_time = pd.to_datetime(zoom_time) - pd.Timedelta(minutes=5)
        end_time = pd.to_datetime(zoom_time) + pd.Timedelta(minutes=5)
        
        print(start_time, end_time)
        
        # get time from bookmark, convert to datetime, pad to give a time range for zooming,
        # post to LSSS.
        zoom_points = [{'time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ')},
                       {'time': end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}]
        d = requests.post(self.lsssURL + 'module/PelagicEchogramModule/zoom', json=zoom_points)

    def reload_bookmarks(self):
        self.listbox.delete(0, 'end')
        self.load_bookmarks()

    def load_bookmarks(self):
        self.bookmarks = []
        if self.bookmarks_file.exists():
            bmks = pd.read_excel(self.bookmarks_file)
            bmks.sort_values('Date (UTC)', inplace=True)
        try:
            for index, row in bmks.iterrows():
                txt = f"{row['Date (UTC)']}    ({row['SGD confidence']:.0f}) {row['Notes']}"
                self.listbox.insert(tk.END, txt)
                match row['SGD confidence']:
                    case 1:
                        self.listbox.itemconfig(tk.END, fg='blue')
                    case 2:
                        self.listbox.itemconfig(tk.END, fg='orange')
                self.bookmarks.append(row['Date (UTC)'])
        except ValueError:
            print(f'Failed to read {self.bookmarks_file}')
            self.bookmarks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = SpatialBookmarkApp(root)
    root.mainloop()

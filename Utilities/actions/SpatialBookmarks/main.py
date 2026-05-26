from math import isnan
from functools import partial
import tkinter as tk
from tkinter import ttk
import datetime as dt
from pathlib import Path
import requests
import pandas as pd
import geopandas as gpd

# make the treeview widget able to sort columns
class SortingTreeview(ttk.Treeview):
    def heading(self, column, sort_by=None, **kwargs):
        if sort_by and not hasattr(kwargs, 'command'):
            func = getattr(self, f"_sort_by_{sort_by}", None)
            if func:
                kwargs['command'] = partial(func, column, False)
        return super().heading(column, **kwargs)

    def _sort(self, column, reverse, data_type, callback):
        items = [(self.set(k, column).lower(), k) for k in self.get_children('')]
        items.sort(key=lambda t: data_type(t[0]), reverse=reverse)
        for index, (_, k) in enumerate(items):
            self.move(k, '', index)
        self.heading(column, command=partial(callback, column, not reverse))

    def _sort_by_num(self, column, reverse):
        self._sort(column, reverse, float, self._sort_by_num)

    def _sort_by_name(self, column, reverse):
        self._sort(column, reverse, str, self._sort_by_name)

    def _sort_by_date(self, column, reverse):
        def _str_to_datetime(string):
            return dt.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        self._sort(column, reverse, _str_to_datetime, self._sort_by_date)


class SpatialBookmarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LSSS Spatial Bookmarks")
        self.root.geometry("600x600")
        self.root.configure(padx=10, pady=10)

        self.zoom_pad = pd.Timedelta(minutes=5)

        self.lsssURL = 'http://localhost:8000/lsss/'
        

        data_dir = Path(r'V:\TAN2603\Echosounders')
        data_dir = Path('.')                

        self.bookmarks_xls = data_dir / 'echosounder_logbook.xlsx'
        self.bookmarks_gpkg = data_dir / 'echosounder_logbook.gpkg'

        # self.bookmarks = []
        
        self._create_widgets()
        self.load_bookmarks()

    def _create_widgets(self):

        # Treeview for bookmarks
        list_frame = ttk.LabelFrame(self.root, text="Bookmarks", padding=10)
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.treeview = SortingTreeview(list_frame, height=10, yscrollcommand=scrollbar.set,
                                     columns=('time', 'rating', 'note'),
                                     show='headings')
        self.treeview.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.treeview.yview)

        self.treeview.heading('time', text='Time', sort_by='name')
        self.treeview.heading('rating', text='Rating', sort_by='num')
        self.treeview.heading('note', text='Note', sort_by='name')

        self.treeview.column('time', width=120, stretch=False)
        self.treeview.column('rating', width=50, stretch=False)
        self.treeview.column('note', stretch=True)

        self.treeview.tag_configure('rating1', foreground='blue')
        self.treeview.tag_configure('rating2', foreground='orange')

        # Action Buttons for List
        actions_frame = ttk.Frame(self.root, padding=5)
        actions_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(actions_frame, text="Zoom", command=self.go_to_bookmark).pack(side="left")
        ttk.Button(actions_frame, text="Reload", command=self.reload_bookmarks).pack(side="left")
        ttk.Button(actions_frame, text="Close", command=self.root.destroy).pack(side="right")


    def go_to_bookmark(self):
        selected = self.treeview.selection()

        if not selected:
            return

        zoom_time = self.treeview.item(selected[0])['values'][0]

        start_time = pd.to_datetime(zoom_time) - self.zoom_pad
        end_time = pd.to_datetime(zoom_time) + self.zoom_pad
        
        # get time from bookmark, convert to datetime, pad to give a time range for zooming,
        # post to LSSS.
        zoom_points = [{'time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ')},
                       {'time': end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}]
        try:
            requests.post(self.lsssURL + 'module/PelagicEchogramModule/zoom', json=zoom_points)
        except requests.ConnectionError:
            print('Could not connect to LSSS')

    def update_geopackage(self):
        pass

    def reload_bookmarks(self):
        self.treeview.delete(*self.treeview.get_children())
        self.load_bookmarks()

    def load_bookmarks(self):
        # self.bookmarks = []
        if self.bookmarks_xls.exists():
            df = pd.read_excel(self.bookmarks_xls)

            # remove rows that don't have a timestamp in the Date column
            df = df[pd.to_datetime(df['Date (UTC)'], errors='coerce').notna()]
            df.sort_values('Date (UTC)', inplace=True)
            bmks_xls = gpd.GeoDataFrame(df, crs='EPSG:4326',
                    geometry=gpd.points_from_xy(x=df['Longitude'], y=df['Latitude']))

            # load the existing gpkg file to geopandas, or make an empty one
            bmks_gpkg = gpd.read_file(self.bookmarks_gpkg) \
                if self.bookmarks_gpkg.exists() \
                    else gpd.GeoDataFrame(bmks_xls[:0], geometry=[], crs="EPSG:4326")

            # what is in bmks_xls that isn't in bmks_gpkg?
            # note that this doesn't update any edits to existing rows in the xls file.
            # To do that, it's probably necessary to use SQL commands and work on the
            # geopackage file directly.
            bmks_new = bmks_xls[~bmks_xls['Date (UTC)'].isin(bmks_gpkg['Date (UTC)'])]

            # add those additional rows to bmks
            bmks_new.to_file(self.bookmarks_gpkg, mode = 'a')
        try:
            for index, row in bmks_xls.iterrows():
                # txt = f"{row['Date (UTC)']}    ({row['SGD confidence']:.0f}) {row['Notes']}"
                match row['SGD confidence']:
                    case 1:
                        tags = ('rating1',)
                    case 2:
                        tags = ('rating2',)
                    case _:
                        tags = ()

                self.treeview.insert('', tk.END, values=(row['Date (UTC)'],
                                                         f'{row['SGD confidence']:.0f}',
                                                         row['Notes']),
                                                 tags=tags)

                # self.bookmarks.append(row['Date (UTC)'])
        except ValueError:
            print(f'Failed to read {self.bookmarks_xls}')
            # self.bookmarks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = SpatialBookmarkApp(root)
    root.mainloop()

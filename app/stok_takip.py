import tkinter as tk
from tkinter import ttk
from utils.io_utils import stok_yukle
import pandas as pd


class StokTakipApp:
    def __init__(self, master):
        self.master = master
        self.df = pd.DataFrame()
        self.build_ui()
        self.load_data()
        self.auto_refresh()

    def build_ui(self):
        columns = ["Kod", "Isim", "Marka", "Model", "Raf", "Mevcut"]
        titles = ["Kod", "Ürün Adı", "Marka", "Model", "Raf", "Mevcut"]

        # Üst arama kutuları
        search_frame = tk.Frame(self.master)
        search_frame.pack(fill="x")
        self.search_entries = {}
        for i, (col, title) in enumerate(zip(columns, titles)):
            lbl = tk.Label(search_frame, text=title)
            lbl.grid(row=0, column=i, padx=2, pady=2)
            ent = tk.Entry(search_frame, width=12)
            ent.grid(row=1, column=i, padx=2, pady=2)
            ent.bind("<KeyRelease>", self.search)
            self.search_entries[col] = ent

        # Treeview
        self.tree = ttk.Treeview(
            self.master,
            columns=columns,
            show="headings"
        )

        for col, title in zip(columns, titles):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

    def load_data(self):
        self.df = stok_yukle()
        self.show_data(self.df)

    def show_data(self, df):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, r in df.iterrows():
            self.tree.insert("", "end", values=(r["Kod"], r["Isim"], r["Marka"], r["Model"], r["Raf"], r["Mevcut"]))

    def search(self, event=None):
        df = self.df.copy()
        for col, ent in self.search_entries.items():
            val = ent.get().lower()
            if val:
                df = df[df[col].astype(str).str.lower().str.contains(val)]
        self.show_data(df)

    def auto_refresh(self):
        """Her 5 saniyede stok dosyasını yeniden yükle."""
        self.load_data()
        self.master.after(5000, self.auto_refresh)

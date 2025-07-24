import tkinter as tk
from tkinter import ttk
from app.servis_fisi_app import ServisFisiApp
from app.teslim_fisi_app import TeslimFisiApp
from app.goruntule_app import GoruntuleApp

class MainApp:
    def __init__(self, root):
        root.title("Avcı Teknik | Servis Takip Sistemi")
        root.geometry("1000x700")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        # Sekmeler
        self.servis_tab = tk.Frame(notebook)
        self.teslim_tab = tk.Frame(notebook)
        self.goruntule_tab = tk.Frame(notebook)

        notebook.add(self.servis_tab, text="Servis Fişi Oluştur")
        notebook.add(self.teslim_tab, text="Teslim Fişi Oluştur")
        notebook.add(self.goruntule_tab, text="Kayıtları Görüntüle")

        # Bileşenleri başlat
        ServisFisiApp(self.servis_tab)
        TeslimFisiApp(self.teslim_tab)
        GoruntuleApp(self.goruntule_tab)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
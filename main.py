import tkinter as tk
from tkinter import ttk
from app.servis_fisi_app import ServisFisiApp
from app.teslim_fisi_app import TeslimFisiApp
from app.goruntule_app import GoruntuleApp
from app.stok_takip import StokTakipApp
from app.stok_in_out import StokInOutApp


class MainApp:
    def __init__(self, root):
        root.title("Avcı Teknik | Servis Takip Sistemi")
        root.geometry("1100x700")
        root.configure(bg="#2c3e50")  # Koyu arka plan

        # Sol Menü
        self.sidebar = tk.Frame(root, bg="#34495e", width=200)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(root, bg="white")
        self.content.pack(side="right", fill="both", expand=True)

        # Menü Butonları
        self.pages = {}
        buttons = [
            ("Servis Fişi", ServisFisiApp),
            ("Teslim Fişi", TeslimFisiApp),
            ("Kayıtları Görüntüle", GoruntuleApp),
            ("Stok Takip", StokTakipApp),
            ("Stok Giriş/Çıkış", StokInOutApp),
        ]

        for i, (text, frame_class) in enumerate(buttons):
            btn = tk.Button(
                self.sidebar,
                text=text,
                font=("Arial", 12, "bold"),
                fg="white",
                bg="#34495e",
                activebackground="#1abc9c",
                activeforeground="white",
                bd=0,
                relief="flat",
                command=lambda fc=frame_class: self.show_page(fc)
            )
            btn.pack(fill="x", pady=5, ipady=10)

            # Frame'leri önceden oluştur
            frame = tk.Frame(self.content, bg="white")
            self.pages[frame_class] = frame
            frame.place(relwidth=1, relheight=1)

            # İçeriği yükle
            frame_class(frame)

        # Başlangıçta ilk sayfayı aç
        self.show_page(ServisFisiApp)

    def show_page(self, page_class):
        """Sadece seçilen sayfayı göster."""
        for frame in self.pages.values():
            frame.lower()
        self.pages[page_class].lift()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

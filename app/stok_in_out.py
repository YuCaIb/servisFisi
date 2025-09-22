import tkinter as tk
from tkinter import messagebox, ttk
from utils.io_utils import stok_giris, stok_cikis


class StokInOutApp:
    def __init__(self, master):
        self.master = master
        self.build_ui()

    def build_ui(self):
        # === ÜRÜN ÇIKIŞI ===
        frame_cikis = tk.LabelFrame(self.master, text="Ürün Çıkışı", padx=10, pady=10)
        frame_cikis.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_cikis, text="Kod:").grid(row=0, column=0, sticky="w")
        self.cikis_kod = tk.Entry(frame_cikis, width=15)
        self.cikis_kod.grid(row=0, column=1, padx=5)

        tk.Label(frame_cikis, text="Miktar:").grid(row=0, column=2, sticky="w")
        self.cikis_miktar = tk.Entry(frame_cikis, width=10)
        self.cikis_miktar.grid(row=0, column=3, padx=5)

        tk.Button(frame_cikis, text="Stok Çıkış", command=self.cikis).grid(row=0, column=4, padx=10)

        # === AYIRICI ===
        ttk.Separator(self.master, orient="horizontal").pack(fill="x", pady=10)

        # === ÜRÜN GİRİŞİ ===
        frame_giris = tk.LabelFrame(self.master, text="Ürün Girişi", padx=10, pady=10)
        frame_giris.pack(fill="x", padx=10, pady=5)

        info = "Eğer kod yeni ise tüm kolonları doldurman gerekiyor.\nEğer kod mevcutsa sadece Kod + Miktar girmen yeterli."
        tk.Label(frame_giris, text=info, fg="blue", justify="left").grid(row=0, column=0, columnspan=4, pady=5,
                                                                         sticky="w")

        tk.Label(frame_giris, text="Kod:").grid(row=1, column=0, sticky="w")
        self.kod = tk.Entry(frame_giris, width=15);
        self.kod.grid(row=1, column=1, padx=5)

        tk.Label(frame_giris, text="Miktar:").grid(row=1, column=2, sticky="w")
        self.miktar = tk.Entry(frame_giris, width=15);
        self.miktar.grid(row=1, column=3, padx=5)

        tk.Label(frame_giris, text="İsim:").grid(row=2, column=0, sticky="w")
        self.isim = tk.Entry(frame_giris, width=15);
        self.isim.grid(row=2, column=1, padx=5)

        tk.Label(frame_giris, text="Raf:").grid(row=2, column=2, sticky="w")
        self.raf = tk.Entry(frame_giris, width=15);
        self.raf.grid(row=2, column=3, padx=5)

        tk.Label(frame_giris, text="Marka:").grid(row=3, column=0, sticky="w")
        self.marka = tk.Entry(frame_giris, width=15);
        self.marka.grid(row=3, column=1, padx=5)

        tk.Label(frame_giris, text="Model:").grid(row=3, column=2, sticky="w")
        self.model = tk.Entry(frame_giris, width=15);
        self.model.grid(row=3, column=3, padx=5)

        tk.Button(frame_giris, text="Stok Giriş", command=self.giris).grid(row=4, column=0, columnspan=4, pady=10)

    def giris(self):
        try:
            stok_giris(
                self.kod.get(),
                self.isim.get(),
                self.marka.get(),
                self.model.get(),
                self.raf.get(),
                int(self.miktar.get())
            )
            messagebox.showinfo("Başarılı", "Stok giriş işlemi tamamlandı.")
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Hata", f"Stok giriş hatası: {e}")

    def cikis(self):
        try:
            sonuc = stok_cikis(self.cikis_kod.get(), int(self.cikis_miktar.get()))
            if sonuc is True:
                messagebox.showinfo("Başarılı", "Stok çıkış işlemi tamamlandı.")
                self.clear_entries()
            elif isinstance(sonuc, str):
                messagebox.showwarning("Yetersiz Stok", sonuc)
            else:
                messagebox.showerror("Hata", "Ürün bulunamadı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Stok çıkış hatası: {e}")

    def clear_entries(self):
        """Tüm giriş alanlarını temizler."""
        for entry in [self.kod, self.isim, self.marka, self.model, self.raf, self.miktar, self.cikis_kod,
                      self.cikis_miktar]:
            entry.delete(0, tk.END)

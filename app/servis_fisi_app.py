import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from utils.io_utils import json_kaydet, pdf_servis_fisi_olustur, get_next_fis_no


class ServisFisiApp:
    def __init__(self, master):
        self.master = master
        self.logo_path = "logo.png"

        self.firma_adi = tk.StringVar(value="Avcı Teknik Hırdavat")
        self.telefon = tk.StringVar(value="535 471 27 27")
        self.eposta = tk.StringVar(value="avciteknik35@gmail.com")
        self.adres = tk.StringVar(value="Yedi Eylül Mah. 5528 sok. No:18 Torbalı/İzmir")

        self.musteri_adi = tk.StringVar()
        self.musteri_firma = tk.StringVar()
        self.musteri_tel = tk.StringVar()
        self.musteri_mail = tk.StringVar()
        self.onarim = tk.StringVar()
        self.fis_no = tk.StringVar(value=str(get_next_fis_no("data/jsons/servis_kayitlari.json")))
        self.giris_tarihi = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))

        self.kalemler = []

        self.build_ui()

    def build_ui(self):
        row = 0
        for label, var in [
            ("Firma Adı", self.firma_adi), ("Telefon", self.telefon),
            ("E-Posta", self.eposta), ("Adres", self.adres),
            ("Müşteri Adı", self.musteri_adi), ("Müşteri Firma", self.musteri_firma),
            ("Müşteri Tel", self.musteri_tel), ("Müşteri Mail", self.musteri_mail),
            ("Onarım Açıklaması", self.onarim),
            ("Fiş No", self.fis_no), ("Giriş Tarihi", self.giris_tarihi)
        ]:
            tk.Label(self.master, text=label).grid(row=row, column=0, sticky="w")
            tk.Entry(self.master, textvariable=var, width=50).grid(row=row, column=1)
            row += 1

        self.kalem_frame = tk.Frame(self.master)
        self.kalem_frame.grid(row=row, column=0, columnspan=2, pady=5)
        tk.Label(self.kalem_frame, text="Parça Adı").grid(row=0, column=0)
        tk.Label(self.kalem_frame, text="Fiyat").grid(row=0, column=1)
        tk.Label(self.kalem_frame, text="Adet").grid(row=0, column=2)
        tk.Label(self.kalem_frame, text="Ara Toplam").grid(row=0, column=3)
        self.add_kalem_row()

        self.toplam_label = tk.Label(self.kalem_frame, text="Toplam: 0.00 TL", font=("Arial", 12, "bold"))
        self.toplam_label.grid(row=101, column=0, columnspan=2, sticky="w", pady=(10, 0), padx=5)

        tk.Button(self.kalem_frame, text="Kalem Ekle", command=self.add_kalem_row).grid(row=99, column=0, pady=5)

        tk.Button(self.master, text="Logo Yükle", command=self.load_logo).grid(row=row + 1, column=0)
        tk.Button(self.master, text="Kaydet & PDF", command=self.kaydet).grid(row=row + 1, column=1)

    def add_kalem_row(self):
        row = len(self.kalemler) + 1
        parca = tk.Entry(self.kalem_frame, width=20)
        fiyat = tk.Entry(self.kalem_frame, width=10, validate="key",
                         validatecommand=(self.master.register(self.validate_number), "%P"))
        adet = tk.Entry(self.kalem_frame, width=5, validate="key",
                        validatecommand=(self.master.register(self.validate_number), "%P"))
        toplam = tk.Label(self.kalem_frame, text="0.00")

        parca.grid(row=row, column=0)
        fiyat.grid(row=row, column=1)
        adet.grid(row=row, column=2)
        toplam.grid(row=row, column=3)

        fiyat.bind("<KeyRelease>", lambda e: self.update_totals())
        adet.bind("<KeyRelease>", lambda e: self.update_totals())

        self.kalemler.append((parca, fiyat, adet, toplam))

    def validate_number(self, val):
        if val == "": return True
        try:
            float(val.replace(",", "."))
            return True
        except:
            return False

    def update_totals(self):
        toplam = 0.0
        for p, f, a, t in self.kalemler:
            try:
                ara = float(f.get()) * float(a.get())
            except:
                ara = 0.0
            t.config(text=f"{ara:.2f}")
            toplam += ara
        self.toplam_label.config(text=f"Toplam: {toplam:.2f} TL")

    def load_logo(self):
        path = filedialog.askopenfilename(filetypes=[("PNG", "*.png")])
        if path:
            self.logo_path = path

    def kaydet(self):
        kalemler = []
        toplam = 0.0
        for p, f, a, t in self.kalemler:
            try:
                fiyat = float(f.get())
                adet = float(a.get())
                ara_toplam = fiyat * adet
                toplam += ara_toplam
                kalemler.append({
                    "parca": p.get(),
                    "fiyat": f"{fiyat:.2f}",
                    "adet": f"{adet}",
                    "ara_toplam": f"{ara_toplam:.2f}"
                })
            except:
                continue

        kdv_dahil = toplam * 1.20
        self.fis_no.set(str(get_next_fis_no("data/jsons/servis_kayitlari.json")))
        veri = {
            "firma": self.firma_adi.get(),
            "telefon": self.telefon.get(),
            "eposta": self.eposta.get(),
            "adres": self.adres.get(),
            "musteri": self.musteri_adi.get(),
            "musteri_firma": self.musteri_firma.get(),
            "musteri_tel": self.musteri_tel.get(),
            "musteri_mail": self.musteri_mail.get(),
            "fis_no": self.fis_no.get(),
            "giris_tarihi": self.giris_tarihi.get(),
            "onarim": self.onarim.get(),
            "kalemler": kalemler,
            "toplam": f"{toplam:.2f}",
            "kdv_dahil": f"{kdv_dahil:.2f}"
        }

        json_kaydet(veri, "data/jsons/servis_kayitlari.json")
        pdf_yolu = f"data/pdfs/servis_fisi_{veri['fis_no']}.pdf"
        pdf_servis_fisi_olustur(veri, pdf_yolu)
        print("PDF ve JSON kaydedildi:", pdf_yolu)

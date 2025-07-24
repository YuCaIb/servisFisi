import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from utils.io_utils import json_kaydet
from fpdf import FPDF
import os

class TeslimFisiApp:
    def __init__(self, master):
        self.master = master
        self.logo_path = "logo.png"

        self.firma_adi = tk.StringVar(value="Avcı Teknik Hırdavat")
        self.telefon = tk.StringVar(value="535 471 27 27")
        self.eposta = tk.StringVar(value="avciteknik35@gmail.com")
        self.adres = tk.StringVar(value="Yedi Eylül Mah. 5528 sok. No:18 Torbalı/İzmir")

        self.musteri_ad = tk.StringVar()
        self.musteri_firma = tk.StringVar()
        self.musteri_tel = tk.StringVar()
        self.tarih = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))

        self.urunler = []
        self.build_ui()

    def build_ui(self):
        row = 0
        for label, var in [
            ("Firma Adı", self.firma_adi), ("Telefon", self.telefon),
            ("E-Posta", self.eposta), ("Adres", self.adres),
            ("Müşteri Adı", self.musteri_ad), ("Müşteri Firma", self.musteri_firma),
            ("Müşteri Telefon", self.musteri_tel), ("Tarih", self.tarih)
        ]:
            tk.Label(self.master, text=label).grid(row=row, column=0, sticky="w")
            tk.Entry(self.master, textvariable=var, width=50).grid(row=row, column=1)
            row += 1

        self.urunler_frame = tk.Frame(self.master)
        self.urunler_frame.grid(row=row, column=0, columnspan=2, pady=10)
        tk.Label(self.urunler_frame, text="Ürün Adı").grid(row=0, column=0)
        tk.Label(self.urunler_frame, text="Adet").grid(row=0, column=1)
        tk.Label(self.urunler_frame, text="Açıklama").grid(row=0, column=2)
        self.add_urun_row()

        tk.Button(self.urunler_frame, text="Ürün Satırı Ekle", command=self.add_urun_row).grid(row=99, column=0, pady=5)
        tk.Button(self.master, text="Logo Yükle", command=self.load_logo).grid(row=row+1, column=0)
        tk.Button(self.master, text="Kaydet & PDF", command=self.kaydet).grid(row=row+1, column=1)

    def add_urun_row(self):
        row = len(self.urunler) + 1
        urun = tk.Entry(self.urunler_frame, width=25)
        adet = tk.Entry(self.urunler_frame, width=10)
        aciklama = tk.Entry(self.urunler_frame, width=40)
        urun.grid(row=row, column=0)
        adet.grid(row=row, column=1)
        aciklama.grid(row=row, column=2)
        self.urunler.append((urun, adet, aciklama))

    def load_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Resim", "*.png;*.jpg")])
        if path:
            self.logo_path = path

    def kaydet(self):
        veri = {
            "firma": self.firma_adi.get(),
            "telefon": self.telefon.get(),
            "eposta": self.eposta.get(),
            "adres": self.adres.get(),
            "musteri_ad": self.musteri_ad.get(),
            "musteri_firma": self.musteri_firma.get(),
            "musteri_tel": self.musteri_tel.get(),
            "tarih": self.tarih.get(),
            "urunler": [
                {"urun": u.get(), "adet": a.get(), "aciklama": ac.get()}
                for u, a, ac in self.urunler if u.get() or a.get() or ac.get()
            ]
        }

        json_kaydet(veri, "data/jsons/teslim_fisi_kayitlar.json")
        self.olustur_pdf(veri)

    def olustur_pdf(self, veri):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        font_path = "fonts/arial.ttf"
        bold = "fonts/arialbd.ttf"
        italic = "fonts/ariali.ttf"

        pdf.add_font("ArialUnicode", "", font_path, uni=True)
        pdf.add_font("ArialUnicode", "B", bold, uni=True)
        pdf.add_font("ArialUnicode", "I", italic, uni=True)
        pdf.set_font("ArialUnicode", size=12)

        if self.logo_path and os.path.exists(self.logo_path):
            pdf.image(self.logo_path, x=10, y=10, w=40)

        pdf.set_xy(70, 10)
        pdf.multi_cell(0, 7, f"{veri['firma']}\n{veri['adres']}\nTel: {veri['telefon']}  E-posta: {veri['eposta']}")
        pdf.set_xy(150, 10)
        pdf.set_font("ArialUnicode", size=11)
        pdf.cell(50, 10, f"Tarih: {veri['tarih']}", ln=True, align="R")

        pdf.set_y(55)
        pdf.set_font("ArialUnicode", size=14, style='B')
        pdf.cell(0, 10, f"Sayın : {veri['musteri_ad']}", ln=True)
        pdf.set_y(pdf.get_y() + 10)
        pdf.cell(0, 10, "MALZEME TESLİM FİŞİ", ln=True, align="C")

        pdf.ln(5)
        pdf.set_font("ArialUnicode", size=12, style="B")
        pdf.cell(140, 10, "CİNSİ", border=1)
        pdf.cell(40, 10, "MİKTARI", border=1)
        pdf.ln()
        pdf.set_font("ArialUnicode", size=12)

        for u in veri["urunler"]:
            pdf.cell(140, 10, u["urun"], border=1)
            pdf.cell(40, 10, u["adet"], border=1)
            pdf.ln()

        pdf.ln(20)
        pdf.set_font("ArialUnicode", style="I")
        pdf.cell(0, 10, "TESLİM ALAN", ln=True, align="L")

        os.makedirs("data/teslim_fisleri", exist_ok=True)
        zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
        dosya = f"data/teslim_fisleri/teslim_fisi_{veri['musteri_ad'].replace(' ', '_')}_{zaman}.pdf"
        pdf.output(dosya)
        print("Teslim Fişi PDF oluşturuldu:", dosya)
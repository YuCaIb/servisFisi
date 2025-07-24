import os
import json
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from fpdf import FPDF

class TeslimFisiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Teslim Fişi Uygulaması")

        self.logo_path = "logo.png" if os.path.exists("logo.png") else ""

        # Firma Bilgileri
        self.firma_adi = tk.StringVar(value="Avcı Teknik Hırdavat")
        self.telefon = tk.StringVar(value="535 471 27 27")
        self.eposta = tk.StringVar(value="avciteknik35@gmail.com")
        self.adres = tk.StringVar(value="Yedi Eylül Mah. 5528 sok. No:18 Torbalı/İzmir")

        self.create_entry("Firma Adı:", self.firma_adi, 0)
        self.create_entry("Telefon:", self.telefon, 1)
        self.create_entry("E-Posta:", self.eposta, 2)
        self.create_entry("Adres:", self.adres, 3)

        # Müşteri Bilgileri
        self.musteri_ad = tk.StringVar()
        self.musteri_firma = tk.StringVar()
        self.musteri_tel = tk.StringVar()
        self.tarih = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))

        self.create_entry("Müşteri Adı:", self.musteri_ad, 4)
        self.create_entry("Müşteri Firma:", self.musteri_firma, 5)
        self.create_entry("Müşteri Telefon:", self.musteri_tel, 6)
        self.create_entry("Tarih:", self.tarih, 7)

        # Ürünler
        self.urunler = []
        self.urunler_frame = tk.Frame(root)
        self.urunler_frame.grid(row=8, column=0, columnspan=2, pady=10)

        tk.Label(self.urunler_frame, text="Ürün Adı").grid(row=0, column=0)
        tk.Label(self.urunler_frame, text="Adet").grid(row=0, column=1)
        tk.Label(self.urunler_frame, text="Açıklama").grid(row=0, column=2)

        self.add_urun_row()

        tk.Button(self.urunler_frame, text="Ürün Satırı Ekle", command=self.add_urun_row).grid(row=100, column=0, columnspan=3, pady=5)

        # Logo
        tk.Button(root, text="Logo Yükle", command=self.load_logo).grid(row=9, column=0, columnspan=2, pady=5)

        # Kaydet Butonu
        tk.Button(root, text="Teslim Fişi Oluştur", command=self.kaydet_ve_pdf).grid(row=10, column=0, columnspan=2, pady=10)

    def create_entry(self, label_text, variable, row):
        tk.Label(self.root, text=label_text).grid(row=row, column=0, sticky="w")
        tk.Entry(self.root, textvariable=variable, width=50).grid(row=row, column=1)

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
        path = filedialog.askopenfilename(filetypes=[("Resim Dosyası", "*.png;*.jpg;*.jpeg")])
        if path:
            self.logo_path = path
            print("Logo yüklendi:", self.logo_path)

    def kaydet_ve_pdf(self):
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
                {
                    "urun": u.get(),
                    "adet": a.get(),
                    "aciklama": ac.get()
                }
                for u, a, ac in self.urunler if u.get() or a.get() or ac.get()
            ]
        }

        json_klasoru = "goruntule/jsons"
        os.makedirs(json_klasoru, exist_ok=True)
        kayit_dosyasi = os.path.join(json_klasoru, "teslim_fisi_kayitlar.json")

        if os.path.exists(kayit_dosyasi):
            with open(kayit_dosyasi, "r", encoding="utf-8") as f:
                mevcut = json.load(f)
        else:
            mevcut = []

        mevcut.append(veri)

        with open(kayit_dosyasi, "w", encoding="utf-8") as f:
            json.dump(mevcut, f, ensure_ascii=False, indent=4)

        self.olustur_pdf(veri)

    def olustur_pdf(self, veri):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        font_path = "./arial.ttf"
        font_path_bold = "./arialbd.ttf"
        font_path_italic = "./ariali.ttf"

        pdf.add_font("ArialUnicode", "", font_path, uni=True)
        pdf.add_font("ArialUnicode", "B", font_path_bold, uni=True)
        pdf.add_font("ArialUnicode", "I", font_path_italic, uni=True)
        pdf.set_font("ArialUnicode", size=12)

        logo_bottom = 10
        if self.logo_path and os.path.exists(self.logo_path):
            pdf.image(self.logo_path, x=10, y=10, w=50)
            logo_bottom = 10 + 40

        pdf.set_xy(70, 10)
        pdf.multi_cell(0, 7, f"{veri['firma']}\n{veri['adres']}\nTel: {veri['telefon']}  E-posta: {veri['eposta']}")

        pdf.set_xy(150, 10)
        pdf.set_font("ArialUnicode", size=11)
        pdf.cell(50, 10, f"Tarih: {veri['tarih']}", ln=True, align="R")

        y_sayin_basla = logo_bottom + 10
        pdf.set_line_width(0.3)
        pdf.line(10, y_sayin_basla, 200, y_sayin_basla)

        pdf.set_xy(10, y_sayin_basla + 5)
        pdf.set_font("ArialUnicode", size=14, style='B')
        pdf.cell(0, 10, f"Sayın : {veri['musteri_ad']}", ln=True)

        pdf.set_y(y_sayin_basla + 20)
        pdf.set_font("ArialUnicode", size=14, style="B")
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

        pdf_klasoru = "teslim_fisleri"
        os.makedirs(pdf_klasoru, exist_ok=True)

        zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
        dosya_adi = f"teslim_fisi_{veri['musteri_ad'].replace(' ', '_')}_{zaman_damgasi}.pdf"
        dosya_yolu = os.path.join(pdf_klasoru, dosya_adi)

        pdf.output(dosya_yolu)
        print("PDF oluşturuldu:", dosya_yolu)


if __name__ == "__main__":
    root = tk.Tk()
    app = TeslimFisiApp(root)
    root.mainloop()

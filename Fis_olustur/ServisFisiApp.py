import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from pdf_creation import pdf_olustur
from servis_json_arac import en_son_fis_noyu_getir


class ServisFisiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Servis Fişi Uygulaması")

        # Sayı doğrulama fonksiyonu
        vcmd_float = (root.register(self.sayi_kontrol), "%P")

        # Firma Bilgileri
        tk.Label(root, text="Firma Adı:").grid(row=0, column=0)
        self.firma_adi = tk.Entry(root, width=40)
        self.firma_adi.grid(row=0, column=1)
        self.firma_adi.insert(0, "Avcı Teknik Hırdavat")

        tk.Label(root, text="Telefon:").grid(row=1, column=0)
        self.telefon = tk.Entry(root, width=40)
        self.telefon.grid(row=1, column=1)
        self.telefon.insert(0, "535 471 27 27")

        tk.Label(root, text="E-Posta:").grid(row=2, column=0)
        self.eposta = tk.Entry(root, width=40)
        self.eposta.grid(row=2, column=1)
        self.eposta.insert(0, "avciteknik35@gmail.com")

        tk.Label(root, text="Adres:").grid(row=3, column=0)
        self.adres = tk.Entry(root, width=40)
        self.adres.grid(row=3, column=1)
        self.adres.insert(0, "Yedi Eylül Mah. 5528 sok. No:18 Torbalı/İzmir")

        # Müşteri Bilgileri
        tk.Label(root, text="Müşteri Adı:").grid(row=4, column=0)
        self.musteri_adi = tk.Entry(root, width=40)
        self.musteri_adi.grid(row=4, column=1)

        tk.Label(root, text="Müşteri Firma:").grid(row=5, column=0)
        self.musteri_firma = tk.Entry(root, width=40)
        self.musteri_firma.grid(row=5, column=1)

        tk.Label(root, text="Müşteri Telefon:").grid(row=6, column=0)
        self.musteri_tel = tk.Entry(root, width=40)
        self.musteri_tel.grid(row=6, column=1)

        tk.Label(root, text="Müşteri Mail:").grid(row=7, column=0)
        self.musteri_mail = tk.Entry(root, width=40)
        self.musteri_mail.grid(row=7, column=1)

        # Servis Bilgileri
        tk.Label(root, text="Servis Fiş No:").grid(row=8, column=0)
        self.fis_no = tk.Entry(root, width=40)
        sonraki_fis_no = en_son_fis_noyu_getir()
        self.fis_no.insert(0, str(sonraki_fis_no))
        self.fis_no.grid(row=8, column=1)

        tk.Label(root, text="Giriş Tarihi:").grid(row=9, column=0)
        self.giris_tarihi = tk.Entry(root, width=40)
        self.giris_tarihi.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.giris_tarihi.grid(row=9, column=1)

        tk.Label(root, text="Onarım Açıklaması:").grid(row=10, column=0)
        self.onarim_aciklama = tk.Text(root, width=30, height=4)
        self.onarim_aciklama.grid(row=10, column=1)

        # Hizmet Kalemleri Frame
        self.kalemler_frame = tk.Frame(root)
        self.kalemler_frame.grid(row=11, column=0, columnspan=4, pady=10)

        # Başlıklar
        tk.Label(self.kalemler_frame, text="Parça Adı").grid(row=0, column=0)
        tk.Label(self.kalemler_frame, text="Birim Fiyat").grid(row=0, column=1)
        tk.Label(self.kalemler_frame, text="Adet").grid(row=0, column=2)
        tk.Label(self.kalemler_frame, text="Ara Toplam").grid(row=0, column=3)

        self.kalemler = []
        self.ekle_kalem(vcmd_float)

        # Satır Ekle Butonu (kalemler_frame altında)
        tk.Button(self.kalemler_frame, text="Satır Ekle", command=lambda: self.ekle_kalem(vcmd_float)).grid(
            row=100, column=0, pady=5, columnspan=4
        )

        # Toplam Label (kalemler_frame içinde, Satır Ekle butonunun altında)
        self.toplam_label = tk.Label(self.kalemler_frame, text="Toplam: 0.00 TL", font=("Arial", 12, "bold"))
        self.toplam_label.grid(row=101, column=0, columnspan=2, sticky="w", pady=(10, 0), padx=5)

        self.kdv_label = tk.Label(self.kalemler_frame, text="KDV Dahil: 0.00 TL", font=("Arial", 12))
        self.kdv_label.grid(row=101, column=2, columnspan=2, sticky="e", pady=(10, 0), padx=5)

        # Logo
        self.logo_path = "./logo.png" if os.path.exists("./logo.png") else ""
        tk.Button(root, text="Logo Yükle (PNG)", command=self.yukle_logo).grid(row=12, column=0, columnspan=2, pady=5)

        # Devam Et
        tk.Button(root, text="Devam Et", command=self.devam_et).grid(row=13, column=0, columnspan=2, pady=10)

    def sayi_kontrol(self, value):
        # Sayısal değer kontrolü (boş da olabilir)
        if value == "":
            return True
        try:
            float(value.replace(",", "."))
            return True
        except ValueError:
            return False

    def ekle_kalem(self, vcmd_float):
        row = len(self.kalemler) + 1
        parca_entry = tk.Entry(self.kalemler_frame, width=20)
        fiyat_entry = tk.Entry(self.kalemler_frame, width=10, validate="key", validatecommand=vcmd_float)
        adet_entry = tk.Entry(self.kalemler_frame, width=5, validate="key", validatecommand=vcmd_float)
        ara_toplam_label = tk.Label(self.kalemler_frame, text="0.00")

        parca_entry.grid(row=row, column=0)
        fiyat_entry.grid(row=row, column=1)
        adet_entry.grid(row=row, column=2)
        ara_toplam_label.grid(row=row, column=3)

        fiyat_entry.bind("<KeyRelease>", lambda e: self.guncelle_toplamlar())
        adet_entry.bind("<KeyRelease>", lambda e: self.guncelle_toplamlar())

        self.kalemler.append((parca_entry, fiyat_entry, adet_entry, ara_toplam_label))

    def guncelle_toplamlar(self):
        toplam = 0
        for parca_entry, fiyat_entry, adet_entry, ara_toplam_label in self.kalemler:
            try:
                fiyat = float(fiyat_entry.get().replace(",", "."))
                adet = float(adet_entry.get().replace(",", "."))
                ara_toplam = fiyat * adet
            except:
                ara_toplam = 0
            ara_toplam_label.config(text=f"{ara_toplam:.2f}")
            toplam += ara_toplam
        kdv_dahil = toplam * 1.20
        self.toplam_label.config(text=f"Toplam: {toplam:.2f} TL")
        self.kdv_label.config(text=f"KDV Dahil: {kdv_dahil:.2f} TL")
    def yukle_logo(self):
        self.logo_path = filedialog.askopenfilename(filetypes=[("PNG Dosyası", "*.png")])
        if self.logo_path:
            print(f"Logo yüklendi: {self.logo_path}")

    def devam_et(self):
        print("=== SERVİS FİŞİ VERİLERİ ===")
        print("Firma:", self.firma_adi.get())
        print("Müşteri:", self.musteri_adi.get())
        print("Servis Fiş No:", self.fis_no.get())
        print("Giriş Tarihi:", self.giris_tarihi.get())
        print("Onarım:", self.onarim_aciklama.get("1.0", tk.END).strip())
        for i, (p, f, a, t) in enumerate(self.kalemler):
            print(f"{i + 1}. Parça: {p.get()}, Fiyat: {f.get()}, Adet: {a.get()}, Ara Toplam: {t.cget('text')}")
        print("Toplam:", self.toplam_label.cget("text"))
        print("************")
        pdf_olustur(self)
        print("pdf oluşturuldu")


# Uygulamayı başlat
root = tk.Tk()
app = ServisFisiApp(root)
root.mainloop()

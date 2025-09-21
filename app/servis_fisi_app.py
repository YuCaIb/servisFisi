import tkinter as tk
from tkinter import filedialog, ttk
from datetime import datetime
from utils.io_utils import json_kaydet, pdf_servis_fisi_olustur, get_next_fis_no, json_yukle


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

        # Otomatik doldurma için önceki kayıtları yükle
        self.musteri_list, self.firma_list, self.firma_dict = self.get_previous_customers()

        self.build_ui()

    def get_previous_customers(self):
        veriler = json_yukle("data/jsons/servis_kayitlari.json")
        musteri_set = set()
        firma_set = set()
        firma_dict = {}

        for v in veriler:
            firma = v.get("musteri_firma")
            musteri = v.get("musteri")
            tel = v.get("musteri_tel")
            mail = v.get("musteri_mail")

            if musteri:
                musteri_set.add(musteri)
            if firma:
                firma_set.add(firma)
                if firma not in firma_dict:
                    firma_dict[firma] = []
                firma_dict[firma].append({
                    "musteri": musteri,
                    "tel": tel,
                    "mail": mail
                })

        return list(musteri_set), list(firma_set), firma_dict

    def build_ui(self):
        row = 0
        for label, var in [
            ("Firma Adı", self.firma_adi), ("Telefon", self.telefon),
            ("E-Posta", self.eposta), ("Adres", self.adres),
        ]:
            tk.Label(self.master, text=label).grid(row=row, column=0, sticky="w")
            tk.Entry(self.master, textvariable=var, width=50).grid(row=row, column=1)
            row += 1

        # --- Müşteri Adı (Combobox + filtreleme) ---
        tk.Label(self.master, text="Müşteri Adı").grid(row=row, column=0, sticky="w")
        self.musteri_combo = ttk.Combobox(self.master, textvariable=self.musteri_adi, width=47)
        self.musteri_combo["values"] = self.musteri_list
        self.musteri_combo.grid(row=row, column=1)
        self.musteri_combo.bind("<KeyRelease>", self.filter_musteri_list)
        row += 1

        # --- Müşteri Firma (Combobox + filtreleme + autofill) ---
        tk.Label(self.master, text="Müşteri Firma").grid(row=row, column=0, sticky="w")
        self.firma_combo = ttk.Combobox(self.master, textvariable=self.musteri_firma, width=47)
        self.firma_combo["values"] = self.firma_list
        self.firma_combo.grid(row=row, column=1)
        self.firma_combo.bind("<<ComboboxSelected>>", self.autofill_customer)
        self.firma_combo.bind("<KeyRelease>", self.filter_firma_list)
        row += 1

        # --- Diğer müşteri alanları ---
        for label, var in [
            ("Müşteri Tel", self.musteri_tel),
            ("Müşteri Mail", self.musteri_mail),
            ("Onarım Açıklaması", self.onarim),
            ("Fiş No", self.fis_no),
            ("Giriş Tarihi", self.giris_tarihi)
        ]:
            tk.Label(self.master, text=label).grid(row=row, column=0, sticky="w")
            tk.Entry(self.master, textvariable=var, width=50).grid(row=row, column=1)
            row += 1

        # Kalemler tablosu
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

    # --- Combobox filtreleme ---
    def filter_firma_list(self, event=None):
        typed = self.firma_combo.get().lower()
        if typed == "":
            data = self.firma_list
        else:
            data = [f for f in self.firma_list if typed in f.lower()]
        self.firma_combo["values"] = data
        if data:
            self.firma_combo.event_generate('<Down>')

    def filter_musteri_list(self, event=None):
        typed = self.musteri_combo.get().lower()
        if typed == "":
            data = self.musteri_list
        else:
            data = [m for m in self.musteri_list if typed in m.lower()]
        self.musteri_combo["values"] = data
        if data:
            self.musteri_combo.event_generate('<Down>')

    # --- Firma seçilince müşteri otomatik doldurma ---
    def autofill_customer(self, event=None):
        firma = self.firma_combo.get()
        if firma in self.firma_dict:
            kayitlar = self.firma_dict[firma]
            if len(kayitlar) == 1:
                self.set_customer_fields(kayitlar[0])
            else:
                # Birden fazla müşteri varsa seçim penceresi aç
                sec_pencere = tk.Toplevel(self.master)
                sec_pencere.title(f"{firma} için müşteri seç")
                sec_pencere.geometry("400x300")
                sec_pencere.grab_set()

                lb = tk.Listbox(sec_pencere, width=50, height=10)
                lb.pack(pady=10, padx=10, fill="both", expand=True)

                for k in kayitlar:
                    lb.insert(tk.END, f"{k.get('musteri','')} - {k.get('tel','')} - {k.get('mail','')}")

                def sec(event=None):
                    idx = lb.curselection()
                    if idx:
                        self.set_customer_fields(kayitlar[idx[0]])
                        sec_pencere.destroy()

                tk.Button(sec_pencere, text="Seç", command=sec).pack(pady=5)
                lb.bind("<Double-1>", sec)  # çift tıklama ile seçme

    def set_customer_fields(self, data):
        if data.get("musteri"):
            self.musteri_adi.set(data["musteri"])
        if data.get("tel"):
            self.musteri_tel.set(data["tel"])
        if data.get("mail"):
            self.musteri_mail.set(data["mail"])

    # --- Kalemler ---
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

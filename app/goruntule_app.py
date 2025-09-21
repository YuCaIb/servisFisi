import subprocess
import sys
import tkinter as tk
from tkinter import ttk
from utils.io_utils import json_yukle, pdf_servis_fisi_olustur, json_to_excel, json_guncelle
import os


class GoruntuleApp:
    def __init__(self, master):
        self.master = master
        self.json_path = "data/jsons/servis_kayitlari.json"
        self.excel_path = "data/excel/servis_kayitlari.xlsx"
        self.pdf_dir = "data/pdfs"

        self.arama_var = tk.StringVar()
        self.arama_var.trace("w", self.filtrele)

        self.build_ui()
        self.kayitlari_doldur()
        self._prev_data_len = len(json_yukle(self.json_path))
        self.master.after(3000, self.oto_guncelle)

    def build_ui(self):
        frame = tk.Frame(self.master)
        frame.pack(pady=5)

        tk.Label(frame, text="Ara:").pack(side=tk.LEFT)
        entry = tk.Entry(frame, textvariable=self.arama_var, width=40)
        entry.pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(self.master, columns=(
            "Fiş No", "Müşteri Firma", "Açıklama", "Müşteri", "Telefon", "Tarih", "Toplam", "Durum"),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.pdf_ac)  # double click

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Excel'e Aktar", command=self.excele_aktar).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Seçili Kaydı PDF Olarak Üret", command=self.pdf_uret).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Seçili Kaydı Düzenle", command=self.duzenle_fis).pack(side=tk.LEFT, padx=10)

        # Renk ayarları
        self.tree.tag_configure("devam", background="lightgreen")
        self.tree.tag_configure("bitti", background="lightcoral")
        self.tree.tag_configure("bos", background="white")

    def kayitlari_doldur(self):
        self.tree.delete(*self.tree.get_children())
        for veri in json_yukle(self.json_path):
            status = veri.get("status")
            if status == 0:
                tag = "devam"
            elif status == 1:
                tag = "bitti"
            else:
                tag = "bos"

            self.tree.insert("", tk.END, values=(
                veri.get("fis_no", ""),
                veri.get("musteri_firma", ""),
                veri.get("onarim", ""),
                veri.get("musteri", ""),
                veri.get("musteri_tel", ""),
                veri.get("giris_tarihi", ""),
                veri.get("toplam", ""),
                status if status is not None else ""
            ), tags=(tag,))

    def filtrele(self, *args):
        aranan = self.arama_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for veri in json_yukle(self.json_path):
            if aranan in str(veri).lower():
                status = veri.get("status")
                if status == 0:
                    tag = "devam"
                elif status == 1:
                    tag = "bitti"
                else:
                    tag = "bos"

                self.tree.insert("", tk.END, values=(
                    veri.get("fis_no", ""),
                    veri.get("musteri_firma", ""),
                    veri.get("onarim", ""),
                    veri.get("musteri", ""),
                    veri.get("musteri_tel", ""),
                    veri.get("giris_tarihi", ""),
                    veri.get("toplam", ""),
                    status if status is not None else ""
                ), tags=(tag,))

    def pdf_uret(self):
        secili = self.tree.selection()
        if not secili:
            return
        index = self.tree.index(secili[0])
        veriler = json_yukle(self.json_path)
        if index < len(veriler):
            veri = veriler[index]
            os.makedirs(self.pdf_dir, exist_ok=True)
            path = os.path.join(self.pdf_dir, f"servis_fisi_{veri['fis_no']}_yeniden.pdf")
            pdf_servis_fisi_olustur(veri, path)
            print("PDF üretildi:", path)

    def excele_aktar(self):
        json_to_excel(self.json_path, self.excel_path)

    def oto_guncelle(self):
        yeni = len(json_yukle(self.json_path))
        if yeni != self._prev_data_len:
            self.kayitlari_doldur()
            self._prev_data_len = yeni
        self.master.after(3000, self.oto_guncelle)

    def pdf_ac(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        index = self.tree.index(item)
        veriler = json_yukle(self.json_path)
        if index < len(veriler):
            veri = veriler[index]
        path = os.path.join(self.pdf_dir, f"servis_fisi_{veri['fis_no']}_yeniden.pdf")
        if not os.path.exists(path):
            os.makedirs(self.pdf_dir, exist_ok=True)
        pdf_servis_fisi_olustur(veri, path)
        # PDF aç
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    def duzenle_fis(self):
        secili = self.tree.selection()
        if not secili:
            return
        index = self.tree.index(secili[0])
        veriler = json_yukle(self.json_path)
        if index >= len(veriler):
            return
        veri = veriler[index]

        # Yeni pencere aç
        duzen_pencere = tk.Toplevel(self.master)
        duzen_pencere.title(f"Fiş Düzenle - {veri['fis_no']}")
        duzen_pencere.geometry("800x700")
        duzen_pencere.grab_set()  # modal yapar

        # --- Müşteri Bilgileri ---
        tk.Label(duzen_pencere, text="Müşteri Adı").grid(row=0, column=0, sticky="w")
        musteri_entry = tk.Entry(duzen_pencere, width=50)
        musteri_entry.insert(0, veri.get("musteri", ""))
        musteri_entry.grid(row=0, column=1)

        tk.Label(duzen_pencere, text="Müşteri Firma").grid(row=1, column=0, sticky="w")
        firma_entry = tk.Entry(duzen_pencere, width=50)
        firma_entry.insert(0, veri.get("musteri_firma", ""))
        firma_entry.grid(row=1, column=1)

        # --- Onarım Açıklaması ---
        tk.Label(duzen_pencere, text="Onarım Açıklaması").grid(row=2, column=0, sticky="nw")
        onarim_text = tk.Text(duzen_pencere, width=60, height=5)
        onarim_text.insert("1.0", veri.get("onarim", ""))
        onarim_text.grid(row=2, column=1, pady=5)

        # --- Durum ---
        tk.Label(duzen_pencere, text="Durum").grid(row=3, column=0, sticky="w")
        status_var = tk.IntVar(value=veri.get("status", -1) if veri.get("status") is not None else -1)
        tk.Radiobutton(duzen_pencere, text="Devam Ediyor", variable=status_var, value=0).grid(row=3, column=1, sticky="w")
        tk.Radiobutton(duzen_pencere, text="Bitti", variable=status_var, value=1).grid(row=3, column=2, sticky="w")
        tk.Radiobutton(duzen_pencere, text="Belirtilmedi", variable=status_var, value=-1).grid(row=3, column=3, sticky="w")

        # --- Kalemler (Parçalar) ---
        tk.Label(duzen_pencere, text="Parçalar").grid(row=4, column=0, sticky="w", pady=10)
        kalem_frame = tk.Frame(duzen_pencere)
        kalem_frame.grid(row=5, column=0, columnspan=4, pady=5)

        tk.Label(kalem_frame, text="Parça Adı").grid(row=0, column=0)
        tk.Label(kalem_frame, text="Fiyat").grid(row=0, column=1)
        tk.Label(kalem_frame, text="Adet").grid(row=0, column=2)
        tk.Label(kalem_frame, text="Ara Toplam").grid(row=0, column=3)

        kalem_entries = []

        def add_kalem_row(parca="", fiyat="", adet="", ara_toplam="0.00"):
            row = len(kalem_entries) + 1
            p_entry = tk.Entry(kalem_frame, width=20)
            f_entry = tk.Entry(kalem_frame, width=10)
            a_entry = tk.Entry(kalem_frame, width=5)
            t_label = tk.Label(kalem_frame, text=ara_toplam)

            p_entry.insert(0, parca)
            f_entry.insert(0, fiyat)
            a_entry.insert(0, adet)

            p_entry.grid(row=row, column=0)
            f_entry.grid(row=row, column=1)
            a_entry.grid(row=row, column=2)
            t_label.grid(row=row, column=3)

            def update_row(*args):
                try:
                    f = float(f_entry.get())
                    a = float(a_entry.get())
                    t_label.config(text=f"{f*a:.2f}")
                except:
                    t_label.config(text="0.00")
                update_total()

            f_entry.bind("<KeyRelease>", update_row)
            a_entry.bind("<KeyRelease>", update_row)

            kalem_entries.append((p_entry, f_entry, a_entry, t_label))

        # Eski kalemleri doldur
        for k in veri.get("kalemler", []):
            add_kalem_row(k.get("parca",""), k.get("fiyat",""), k.get("adet",""), k.get("ara_toplam","0.00"))

        tk.Button(kalem_frame, text="Kalem Ekle", command=lambda: add_kalem_row()).grid(row=99, column=0, pady=5)

        toplam_label = tk.Label(kalem_frame, text="Toplam: 0.00 TL", font=("Arial", 12, "bold"))
        toplam_label.grid(row=100, column=0, columnspan=2, sticky="w")

        def update_total():
            toplam = 0.0
            for _, f, a, t in kalem_entries:
                try:
                    toplam += float(f.get()) * float(a.get())
                except:
                    continue
            toplam_label.config(text=f"Toplam: {toplam:.2f} TL")

        update_total()

        # --- Kaydet Butonu ---
        def kaydet_guncelle():
            yeni_veri = veri.copy()
            yeni_veri["musteri"] = musteri_entry.get()
            yeni_veri["musteri_firma"] = firma_entry.get()
            yeni_veri["onarim"] = onarim_text.get("1.0", "end").strip()
            yeni_veri["status"] = None if status_var.get() == -1 else status_var.get()

            # Kalemler
            kalemler = []
            toplam = 0.0
            for p, f, a, t in kalem_entries:
                try:
                    fiyat = float(f.get())
                    adet = float(a.get())
                    ara = fiyat * adet
                    toplam += ara
                    kalemler.append({
                        "parca": p.get(),
                        "fiyat": f"{fiyat:.2f}",
                        "adet": f"{adet}",
                        "ara_toplam": f"{ara:.2f}"
                    })
                except:
                    continue
            yeni_veri["kalemler"] = kalemler
            yeni_veri["toplam"] = f"{toplam:.2f}"
            yeni_veri["kdv_dahil"] = f"{toplam*1.20:.2f}"

            # JSON güncelle
            json_guncelle(veri["fis_no"], yeni_veri, self.json_path)

            # PDF yeniden üret
            pdf_path = os.path.join(self.pdf_dir, f"servis_fisi_{veri['fis_no']}_yeniden.pdf")
            pdf_servis_fisi_olustur(yeni_veri, pdf_path)

            duzen_pencere.destroy()
            self.kayitlari_doldur()  # tabloyu yenile

        tk.Button(duzen_pencere, text="Kaydet", command=kaydet_guncelle).grid(row=200, column=1, pady=20)


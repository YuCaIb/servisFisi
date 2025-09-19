import subprocess
import sys
import tkinter as tk
from tkinter import ttk
from utils.io_utils import json_yukle, pdf_servis_fisi_olustur, json_to_excel
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
            "Fiş No", "Müşteri Firma", "Açıklama", "Müşteri", "Telefon", "Tarih", "Toplam"), show="headings")

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.pdf_ac)  # double click

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Excel'e Aktar", command=self.excele_aktar).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Seçili Kaydı PDF Olarak Üret", command=self.pdf_uret).pack(side=tk.LEFT, padx=10)

    def kayitlari_doldur(self):
        self.tree.delete(*self.tree.get_children())
        for veri in json_yukle(self.json_path):
            self.tree.insert("", tk.END, values=(
                veri.get("fis_no", ""),
                veri.get("musteri_firma", ""),
                veri.get("onarim", ""),
                veri.get("musteri", ""),
                veri.get("musteri_tel", ""),
                veri.get("giris_tarihi", ""),
                veri.get("toplam", "")
            ))

    def filtrele(self, *args):
        aranan = self.arama_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for veri in json_yukle(self.json_path):
            if aranan in str(veri).lower():
                self.tree.insert("", tk.END, values=(
                    veri.get("fis_no", ""),
                    veri.get("musteri_firma", ""),
                    veri.get("onarim", ""),
                    veri.get("musteri", ""),
                    veri.get("musteri_tel", ""),
                    veri.get("giris_tarihi", ""),
                    veri.get("toplam", "")
                ))

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

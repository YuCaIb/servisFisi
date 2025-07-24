import tkinter as tk
from tkinter import ttk
import json
import os
from pdf_json import pdf_olustur_jsondan
from json_to_excel import json_file_to_excel


def json_verileri_yukle(json_yolu="goruntule/jsons/servis_kayitlari.json"):
    if os.path.exists(json_yolu):
        with open(json_yolu, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


class ServisKayitlariGoster:
    def filtrele(self, *args):
        aranan = self.arama_var.get().lower()
        self.tree.delete(*self.tree.get_children())  # eski kayıtları temizle

        tum_veriler = json_verileri_yukle()
        for veri in tum_veriler:
            if (
                    aranan in veri["fis_no"].lower()
                    or aranan in veri.get("musteri", "").lower()
                    or aranan in veri.get("musteri_firma", "").lower()
                    or aranan in veri.get("musteri_tel", "").lower()
                    or aranan in veri.get("musteri_mail", "").lower()
                    or aranan in veri.get("onarim", "").lower()
                    or aranan in veri.get("giris_tarihi", "").lower()
                    or aranan in veri.get("toplam", "").lower()
                    or aranan in veri.get("kdv_dahil", "").lower()
            ):
                self.tree.insert("", tk.END, values=(
                    veri.get("fis_no", ""),
                    veri.get("musteri_firma", ""),
                    veri.get("musteri", ""),
                    veri.get("musteri_tel", ""),
                    veri.get("musteri_mail", ""),
                    veri.get("onarim", ""),
                    veri.get("giris_tarihi", ""),
                    veri.get("toplam", "")
                ))

    def __init__(self, root):

        self.root = root
        self.root.title("Kayıtlı Servis Fişleri")

        # Arama Kutusu
        self.arama_var = tk.StringVar()
        self.arama_var.trace("w", self.filtrele)

        self.fisno_var = tk.StringVar()
        self.fisno_var.trace("w", self.fisno_filtrele)

        arama_frame = tk.Frame(root)
        arama_frame.pack(pady=5)

        # Yeni "Fiş Ara" kutusu (sola)
        tk.Label(arama_frame, text="Fiş Ara:").pack(side=tk.LEFT, padx=(0, 2))
        self.fisno_entry = tk.Entry(arama_frame, textvariable=self.fisno_var, width=15)
        self.fisno_entry.pack(side=tk.LEFT, padx=(0, 15))

        # Mevcut "Ara" kutusu (sağa alındı)
        tk.Label(arama_frame, text="Ara:").pack(side=tk.LEFT)
        self.arama_entry = tk.Entry(arama_frame, textvariable=self.arama_var, width=40)
        self.arama_entry.pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(root, columns=(
        "FisNo", "Müşteri Firma", "Müşteri", "Telefon", "Açıklama", "Mail", "Tarih", "Toplam"),
                                 show="headings")
        self.tree.heading("FisNo", text="Fiş No")
        self.tree.heading("Müşteri Firma", text="Müşteri Firma")
        self.tree.heading("Müşteri", text="Müşteri")
        self.tree.heading("Telefon", text="Telefon")
        self.tree.heading("Mail", text="Mail")
        self.tree.heading("Açıklama", text="Açıklama")
        self.tree.heading("Tarih", text="Giriş Tarihi")
        self.tree.heading("Toplam", text="Toplam Tutar")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.kayitlari_doldur()

        # PDF üret butonu
        self.button = tk.Button(root, text="Seçili Kaydı PDF Olarak Üret", command=self.pdf_uret)
        self.button.pack(pady=5)

        # Excel'e Aktar butonu
        self.excel_button = tk.Button(root, text="Excel'e Aktar", command=self.excele_aktar)
        self.excel_button.pack(pady=5)

    def kayitlari_doldur(self):
        veriler = json_verileri_yukle()
        for veri in veriler:
            self.tree.insert("", tk.END, values=(
                veri.get("fis_no", ""),
                veri.get("musteri_firma", ""),
                veri.get("musteri", ""),
                veri.get("musteri_tel", ""),
                veri.get("musteri_mail", ""),
                veri.get("onarim", ""),
                veri.get("giris_tarihi", ""),
                veri.get("toplam", ""),
                veri.get("kdv_dahil", "")
            ))

    def fisno_filtrele(self, *args):
        aranan = self.fisno_var.get().lower()
        self.tree.delete(*self.tree.get_children())

        tum_veriler = json_verileri_yukle()
        for veri in tum_veriler:
            if aranan in veri.get("fis_no", "").lower():
                self.tree.insert("", tk.END, values=(
                    veri.get("fis_no", ""),
                    veri.get("musteri_firma", ""),
                    veri.get("musteri", ""),
                    veri.get("musteri_tel", ""),
                    veri.get("musteri_mail", ""),
                    veri.get("onarim", ""),
                    veri.get("giris_tarihi", ""),
                    veri.get("toplam", "")
                ))

    def excele_aktar(self):
        try:
            json_file_to_excel(
                "goruntule/jsons/servis_kayitlari.json")
            print("Excel'e aktarıldı.")
        except Exception as e:
            print("Excel aktarımı sırasında hata:", e)

    def pdf_uret(self):
        secili = self.tree.selection()
        if not secili:
            return

        indeks = self.tree.index(secili[0])  # seçilen satırın indexi
        veriler = json_verileri_yukle()
        if indeks < len(veriler):
            pdf_olustur_jsondan(veriler[indeks])
            print(f"PDF üretildi: Fiş No {veriler[indeks]['fis_no']}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ServisKayitlariGoster(root)
    root.mainloop()

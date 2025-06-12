import tkinter as tk
from tkinter import ttk
import json
import os
from pdf_json import pdf_olustur_jsondan  # senin JSON'dan PDF fonksiyonun


def json_verileri_yukle(json_yolu="servis_kayitlari.json"):
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
                    or aranan in veri["musteri"].lower()
                    or aranan in veri["musteri_tel"].lower()
                    or aranan in veri["onarim"].lower()
                    or aranan in veri["giris_tarihi"].lower()
                    or aranan in veri["toplam"].lower()
            ):
                self.tree.insert("", tk.END, values=(
                    veri["fis_no"],
                    veri["musteri"],
                    veri["musteri_tel"],
                    veri["onarim"],
                    veri["giris_tarihi"],
                    veri["toplam"]
                ))

    def __init__(self, root):

        self.root = root
        self.root.title("Kayıtlı Servis Fişleri")

        # Arama Kutusu
        self.arama_var = tk.StringVar()
        self.arama_var.trace("w", self.filtrele)

        arama_frame = tk.Frame(root)
        arama_frame.pack(pady=5)

        tk.Label(arama_frame, text="Ara:").pack(side=tk.LEFT)
        self.arama_entry = tk.Entry(arama_frame, textvariable=self.arama_var, width=40)
        self.arama_entry.pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(root, columns=("FisNo", "Müşteri", "Telefon", "Açıklama", "Tarih", "Toplam"),
                                 show="headings")
        self.tree.heading("FisNo", text="Fiş No")
        self.tree.heading("Müşteri", text="Müşteri")
        self.tree.heading("Telefon", text="Telefon")
        self.tree.heading("Açıklama", text="Açıklama")
        self.tree.heading("Tarih", text="Giriş Tarihi")
        self.tree.heading("Toplam", text="Toplam Tutar")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.kayitlari_doldur()

        # PDF üret butonu
        self.button = tk.Button(root, text="Seçili Kaydı PDF Olarak Üret", command=self.pdf_uret)
        self.button.pack(pady=5)

    def kayitlari_doldur(self):
        veriler = json_verileri_yukle()
        for veri in veriler:
            self.tree.insert("", tk.END, values=(
                veri["fis_no"],
                veri["musteri"],
                veri["musteri_tel"],
                veri["onarim"],
                veri["giris_tarihi"],
                veri["toplam"]
            ))

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

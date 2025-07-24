from fpdf import FPDF
import json
import os


def pdf_olustur(self):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Font ayarları
    font_path = "./arial.ttf"
    font_path_bold = "./arialbd.ttf"
    font_path_italic = "./ariali.ttf"

    pdf.add_font("ArialUnicode", "", font_path, uni=True)
    pdf.add_font("ArialUnicode", "B", font_path_bold, uni=True)
    pdf.add_font("ArialUnicode", "I", font_path_italic, uni=True)
    pdf.set_font("ArialUnicode", size=12)

    # Logo
    logo_y = 10
    logo_w = 40
    logo_h_estimate = 30
    if self.logo_path and os.path.exists(self.logo_path):
        pdf.image(self.logo_path, x=10, y=logo_y, w=logo_w)
    else:
        logo_h_estimate = 0

    # Firma bilgileri
    pdf.set_xy(55, logo_y)
    pdf.cell(140, 8, f"Firma: {self.firma_adi.get()}", ln=True)
    pdf.set_x(55)
    pdf.cell(140, 8, f"Adres: {self.adres.get()}", ln=True)
    pdf.set_x(55)
    pdf.cell(140, 8, f"Telefon: {self.telefon.get()}", ln=True)
    pdf.set_x(55)
    pdf.cell(140, 8, f"E-posta: {self.eposta.get()}", ln=True)

    header_bottom_y = max(pdf.get_y(), logo_y + logo_h_estimate) + 20
    pdf.set_line_width(0.5)
    pdf.line(10, header_bottom_y, 200, header_bottom_y)
    pdf.set_y(header_bottom_y + 5)

    # Müşteri ve servis bilgileri
    pdf.ln(5)
    pdf.cell(200, 10, f"Firma: {self.musteri_firma.get()}", ln=True)
    pdf.cell(200, 10, f"Müşteri: {self.musteri_adi.get()}", ln=True)
    pdf.cell(200, 10, f"Müşteri Mail: {self.musteri_mail.get()}", ln=True)
    pdf.cell(200, 10, f"Müşteri Telefon: {self.musteri_tel.get()}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, f"Servis Fiş No: {self.fis_no.get()}", ln=True)
    pdf.cell(200, 10, f"Giriş Tarihi: {self.giris_tarihi.get()}", ln=True)

    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Onarım Açıklaması:\n{self.onarim_aciklama.get('1.0', 'end').strip()}")

    pdf.ln(5)
    pdf.set_font("ArialUnicode", size=12, style='B')
    pdf.cell(60, 10, "Parça Adı", border=1)
    pdf.cell(40, 10, "Birim Fiyat", border=1)
    pdf.cell(20, 10, "Adet", border=1)
    pdf.cell(30, 10, "Ara Toplam", border=1)
    pdf.ln()

    pdf.set_font("ArialUnicode", size=12)
    toplam = 0
    for p, f, a, t in self.kalemler:
        try:
            fiyat = float(f.get().replace(",", "."))
            adet = float(a.get().replace(",", "."))
            ara_toplam = fiyat * adet
        except:
            fiyat = adet = ara_toplam = 0

        toplam += ara_toplam
        pdf.cell(60, 10, p.get(), border=1)
        pdf.cell(40, 10, f"{fiyat:.2f}", border=1)
        pdf.cell(20, 10, f"{adet:.0f}", border=1)
        pdf.cell(30, 10, f"{ara_toplam:.2f}", border=1)
        pdf.ln()

    pdf.ln(5)
    pdf.cell(200, 10, f"Toplam: {toplam:.2f} TL", ln=True)
    kdv_dahil = toplam * 1.20
    pdf.cell(200, 10, f"KDV Dahil: {kdv_dahil:.2f} TL", ln=True)

    pdf.ln(10)
    pdf.set_font("ArialUnicode", size=10, style='I')
    pdf.multi_cell(0, 7, "\n\n Müşteri İmzası: ______________________________")

    # JSON oluşturulacak veri
    veri = {
        "firma": self.firma_adi.get(),
        "telefon": self.telefon.get(),
        "eposta": self.eposta.get(),
        "adres": self.adres.get(),
        "musteri firma": self.musteri_firma.get(),
        "musteri": self.musteri_adi.get(),
        "musteri_mail": self.musteri_mail.get(),
        "musteri_tel": self.musteri_tel.get(),
        "fis_no": self.fis_no.get(),
        "giris_tarihi": self.giris_tarihi.get(),
        "onarim": self.onarim_aciklama.get("1.0", "end").strip(),
        "kalemler": [
            {
                "parca": p.get(),
                "fiyat": f.get(),
                "adet": a.get(),
                "ara_toplam": t.cget("text")
            }
            for p, f, a, t in self.kalemler
        ],
        "toplam": self.toplam_label.cget("text").replace("Toplam: ", ""),
        "kdv_dahil": self.kdv_label.cget("text").replace("KDV Dahil: ", "")
    }

    # JSON dosyasını oluşturulacak klasöre yaz
    json_klasoru = "goruntule/jsons"
    os.makedirs(json_klasoru, exist_ok=True)
    json_dosya = os.path.join(json_klasoru, "servis_kayitlari.json")

    if os.path.exists(json_dosya):
        with open(json_dosya, "r", encoding="utf-8") as f:
            mevcut_veriler = json.load(f)
    else:
        mevcut_veriler = []

    mevcut_veriler.append(veri)
    with open(json_dosya, "w", encoding="utf-8") as f:
        json.dump(mevcut_veriler, f, ensure_ascii=False, indent=4)

    print(f"Veri JSON'a eklendi: {json_dosya}")

    # PDF'i "fisler" klasörüne kaydet
    pdf_klasoru = "fisler"
    os.makedirs(pdf_klasoru, exist_ok=True)
    dosya_adi = os.path.join(pdf_klasoru, f"servis_fisi_{self.fis_no.get()}.pdf")
    pdf.output(dosya_adi)
    print(f"PDF oluşturuldu: {dosya_adi}")


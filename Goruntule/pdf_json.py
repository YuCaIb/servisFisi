from fpdf import FPDF
import os


def pdf_olustur_jsondan(veri, font_path="Goruntule/arial.ttf", font_path_bold="Goruntule/arialbd.ttf",
                        font_path_italic="Goruntule/ariali.ttf", output_dir="."):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Font tanımları
    pdf.add_font("ArialUnicode", "", font_path, uni=True)
    pdf.add_font("ArialUnicode", "B", font_path_bold, uni=True)
    pdf.add_font("ArialUnicode", "I", font_path_italic, uni=True)
    pdf.set_font("ArialUnicode", size=12)

    # Firma bilgileri
    pdf.set_xy(55, 10)
    pdf.cell(140, 8, f"Firma: {veri['firma']}", ln=True)
    pdf.set_x(55)
    pdf.cell(140, 8, f"Telefon: {veri['telefon']}", ln=True)
    pdf.set_x(55)
    pdf.cell(140, 8, f"E-posta: {veri['eposta']}", ln=True)

    # Alt çizgi
    pdf.set_line_width(0.5)
    pdf.line(10, 40, 200, 40)
    pdf.set_y(45)

    # Müşteri ve servis bilgileri
    pdf.cell(200, 10, f"Müşteri: {veri['musteri']}", ln=True)
    pdf.cell(200, 10, f"Müşteri Telefon: {veri['musteri_tel']}", ln=True)
    pdf.cell(200, 10, f"Servis Fiş No: {veri['fis_no']}", ln=True)
    pdf.cell(200, 10, f"Giriş Tarihi: {veri['giris_tarihi']}", ln=True)

    # Onarım açıklaması
    pdf.multi_cell(0, 10, f"Onarım Açıklaması:\n{veri['onarim']}")

    # Kalemler
    pdf.set_font("ArialUnicode", size=12, style="B")
    pdf.cell(60, 10, "Parça Adı", border=1)
    pdf.cell(40, 10, "Birim Fiyat", border=1)
    pdf.cell(20, 10, "Adet", border=1)
    pdf.cell(30, 10, "Ara Toplam", border=1)
    pdf.ln()
    pdf.set_font("ArialUnicode", size=12)

    for kalem in veri["kalemler"]:
        pdf.cell(60, 10, kalem["parca"], border=1)
        pdf.cell(40, 10, kalem["fiyat"], border=1)
        pdf.cell(20, 10, kalem["adet"], border=1)
        pdf.cell(30, 10, kalem["ara_toplam"], border=1)
        pdf.ln()

    pdf.ln(5)
    pdf.cell(200, 10, f"Toplam: {veri['toplam']} TL", ln=True)

    # Sayfa numarası
    pdf.set_y(-15)
    pdf.set_font("ArialUnicode", size=10, style="I")
    pdf.cell(0, 10, f"Sayfa {pdf.page_no()}", align="C")

    # Kaydet
    dosya_adi = os.path.join(output_dir, f"servis_fisi_{veri['fis_no']}_yeniden.pdf")
    pdf.output(dosya_adi)
    print(f"PDF yeniden oluşturuldu: {dosya_adi}")

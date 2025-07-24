import os
import json
from fpdf import FPDF
import pandas as pd

FONT_REG = "fonts/arial.ttf"
FONT_BOLD = "fonts/arialbd.ttf"
FONT_ITALIC = "fonts/ariali.ttf"


# ==================== JSON ====================
def json_kaydet(veri, json_path):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            mevcut = json.load(f)
    else:
        mevcut = []
    mevcut.append(veri)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(mevcut, f, ensure_ascii=False, indent=4)


def json_yukle(json_path):
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# ==================== PDF ====================
def pdf_servis_fisi_olustur(veri, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_font("ArialUnicode", "", FONT_REG, uni=True)
    pdf.add_font("ArialUnicode", "B", FONT_BOLD, uni=True)
    pdf.add_font("ArialUnicode", "I", FONT_ITALIC, uni=True)
    pdf.set_font("ArialUnicode", size=12)

    # Logo
    logo_y = 10
    logo_w = 33
    logo_h_estimate = 20
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=10, y=logo_y, w=logo_w)
    else:
        logo_h_estimate = 0

    # Firma bilgileri
    pdf.set_xy(55, logo_y)
    pdf.cell(140, 8, f"Firma: {veri['firma']}", ln=True)
    pdf.set_x(55)
    pdf.cell(140, 8, f"Telefon: {veri['telefon']}", ln=True)
    pdf.set_x(55)
    pdf.cell(140, 8, f"E-posta: {veri['eposta']}", ln=True)
    pdf.set_line_width(0.5)
    pdf.line(10, 45, 200, 45)  # Horizontal line moved down by 5 units (from 40 to 45)
    pdf.set_y(45)

    pdf.cell(200, 10, f"Müşteri Firma: {veri.get('musteri_firma', '')}", ln=True)
    pdf.cell(200, 10, f"Müşteri: {veri.get('musteri', '')}", ln=True)
    pdf.cell(200, 10, f"Mail: {veri.get('musteri_mail', '')}", ln=True)
    pdf.cell(200, 10, f"Telefon: {veri.get('musteri_tel', '')}", ln=True)
    pdf.cell(200, 10, f"Fiş No: {veri['fis_no']}", ln=True)
    pdf.cell(200, 10, f"Tarih: {veri['giris_tarihi']}", ln=True)

    pdf.multi_cell(0, 10, f"Onarım Açıklaması:\n{veri['onarim']}")
    pdf.set_font("ArialUnicode", size=12, style="B")
    pdf.cell(60, 10, "Parça Adı", border=1)
    pdf.cell(40, 10, "Birim Fiyat", border=1)
    pdf.cell(20, 10, "Adet", border=1)
    pdf.cell(30, 10, "Ara Toplam", border=1)
    pdf.ln()
    pdf.set_font("ArialUnicode", size=12)

    for k in veri["kalemler"]:
        pdf.cell(60, 10, k["parca"], border=1)
        pdf.cell(40, 10, k["fiyat"], border=1)
        pdf.cell(20, 10, k["adet"], border=1)
        pdf.cell(30, 10, k["ara_toplam"], border=1)
        pdf.ln()

    pdf.ln(5)
    pdf.cell(200, 10, f"Toplam: {veri['toplam']}", ln=True)

    pdf.set_y(-15)
    pdf.set_font("ArialUnicode", size=10, style="I")
    pdf.cell(0, 10, f"Sayfa {pdf.page_no()}", align="C")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)


# ==================== EXCEL ====================
def json_to_excel(json_path, excel_path):
    if not os.path.exists(json_path):
        print("JSON bulunamadı.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records_df = pd.DataFrame(data)
    items_data = []

    if "kalemler" in records_df.columns:
        for i, row in records_df.iterrows():
            fis_no = row.get("fis_no", "")
            for item in row["kalemler"]:
                new_item = item.copy()
                new_item["fis_no"] = fis_no
                items_data.append(new_item)
        records_df = records_df.drop(columns=["kalemler"])

    # Servis Kayitlari sayfasına toplam ekle
    if "toplam" in records_df.columns:
        toplam_sum = records_df["toplam"].apply(pd.to_numeric, errors="coerce").sum()
        kdv_sum = records_df["kdv_dahil"].apply(pd.to_numeric, errors="coerce").sum() if "kdv_dahil" in records_df.columns else 0
        toplam_row = pd.DataFrame([{col: "" for col in records_df.columns}])
        toplam_row.at[0, "toplam"] = toplam_sum
        if "kdv_dahil" in records_df.columns:
            toplam_row.at[0, "kdv_dahil"] = kdv_sum
        records_df = pd.concat([records_df, toplam_row], ignore_index=True)

    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        records_df.to_excel(writer, sheet_name="Servis Kayitlari", index=False)
        if items_data:
            items_df = pd.DataFrame(items_data)
            if "ara_toplam" in items_df.columns:
                ara_sum = items_df["ara_toplam"].apply(pd.to_numeric, errors="coerce").sum()
                toplam_row = pd.DataFrame([{col: "" for col in items_df.columns}])
                toplam_row.at[0, "ara_toplam"] = ara_sum
                items_df = pd.concat([items_df, toplam_row], ignore_index=True)
            items_df.to_excel(writer, sheet_name="Kalemler", index=False)



# ==================== Fis_No ====================
def en_son_fis_noyu_getir(json_dosya="data/jsons/servis_kayitlari.json"):
    if not os.path.exists(json_dosya):
        return 1  # İlk fiş

    try:
        with open(json_dosya, "r", encoding="utf-8") as f:
            veriler = json.load(f)
            fis_nolar = [int(v.get("fis_no", 0)) for v in veriler if str(v.get("fis_no", "")).isdigit()]
            return max(fis_nolar) + 1 if fis_nolar else 1
    except Exception as e:
        print("Fiş numarası alınamadı:", e)
        return 1


def get_next_fis_no(json_path="data/jsons/servis_kayitlari.json"):
    if not os.path.exists(json_path):
        return 1
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            veriler = json.load(f)
        fis_nolar = [int(v.get("fis_no", 0)) for v in veriler if str(v.get("fis_no", "")).isdigit()]
        return max(fis_nolar, default=0) + 1
    except:
        return 1

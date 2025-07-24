import pandas as pd
import json
import os

def json_file_to_excel(json_filepath, excel_filename="servis_kayitlari.xlsx"):
    """
    JSON dosyasındaki veriyi Excel dosyasına aktarır.
    Excel çıktısı ./goruntule/excel/ dizinine kaydedilir.
    """
    if not os.path.exists(json_filepath):
        print(f"Hata: Belirtilen JSON dosyası bulunamadı: {json_filepath}")
        return

    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Hata: JSON dosyası geçersiz formatta: {json_filepath}")
        return
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return

    # Ana kayıtları oku
    records_df = pd.DataFrame(data)

    # Kalemler varsa patlat
    if 'kalemler' in records_df.columns:
        exploded_items = []
        for index, row in records_df.iterrows():
            fis_no = row.get('fis_no', '')
            for item in row['kalemler']:
                item_copy = item.copy()
                item_copy['fis_no'] = fis_no
                exploded_items.append(item_copy)
        items_data = exploded_items
        records_df = records_df.drop(columns=['kalemler'])
    else:
        items_data = []

    # Excel çıktısı için klasörü hazırla
    output_dir = "goruntule/excel"
    os.makedirs(output_dir, exist_ok=True)
    full_excel_path = os.path.join(output_dir, excel_filename)

    # Excel yazımı
    with pd.ExcelWriter(full_excel_path, engine='openpyxl') as writer:
        records_df.to_excel(writer, sheet_name='Servis Kayitlari', index=False)
        if items_data:
            items_df = pd.DataFrame(items_data)
            items_df.to_excel(writer, sheet_name='Kalemler', index=False)

    print(f"Veriler başarıyla aktarıldı: {full_excel_path}")


# json_file_to_excel("goruntule/jsons/servis_kayitlari.json")

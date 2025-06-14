import pandas as pd
import json
import os # Dosya işlemleri için

def json_file_to_excel(json_filepath, excel_filename="servis_kayitlari.xlsx"):
    """
    JSON dosyasındaki veriyi Excel dosyasına aktarır.

    Args:
        json_filepath (str): JSON dosyasının yolu.
        excel_filename (str): Oluşturulacak Excel dosyasının adı.
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

    # Ana servis kayıtlarını içeren bir DataFrame oluştur
    records_df = pd.DataFrame(data)

    # 'kalemler' sütununu çıkar, çünkü bu ayrı bir sayfaya yazılacak
    if 'kalemler' in records_df.columns:
        # Her ana kaydın fis_no'sunu kalemlerle ilişkilendirmek için
        # Eğer JSON'unuzda her kalemin içinde ilgili fis_no yoksa,
        # bu kısmı manuel olarak birleştirmeniz gerekebilir.
        # Bu örnekte, ana kayıttan fis_no'yu her bir kaleme ekleyeceğiz.
        exploded_items = []
        for index, row in records_df.iterrows():
            fis_no = row['fis_no']
            for item in row['kalemler']:
                item_copy = item.copy()
                item_copy['fis_no'] = fis_no  # Her kaleme fis_no ekle
                exploded_items.append(item_copy)

        items_data = exploded_items
        records_df = records_df.drop(columns=['kalemler'])
    else:
        items_data = []

    # Excel yazıcısını oluştur
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        # Ana servis kayıtlarını ilk sayfaya yaz
        records_df.to_excel(writer, sheet_name='Servis Kayitlari', index=False)

        # Kalemler verisi varsa, ikinci bir sayfaya yaz
        if items_data:
            items_df = pd.DataFrame(items_data)
            items_df.to_excel(writer, sheet_name='Kalemler', index=False)

    print(f"Veriler '{excel_filename}' dosyasına başarıyla aktarıldı.")

# JSON dosyanızın adı (bu kodla aynı dizinde olduğunu varsayalım)
json_dosya_yolu = "servis_kayitlari.json"

# Fonksiyonu çağır
json_file_to_excel(json_dosya_yolu)
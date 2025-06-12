import os
import json


def en_son_fis_noyu_getir(json_dosya="servis_kayitlari.json"):
    if not os.path.exists(json_dosya):
        return 1  # İlk kayıt için 1 başlasın

    with open(json_dosya, "r", encoding="utf-8") as f:
        veriler = json.load(f)

    # Tüm fiş numaralarını al ve en büyüğünü bul
    fis_nolar = []
    for veri in veriler:
        try:
            fis_nolar.append(int(veri.get("fis_no", 0)))
        except:
            continue

    return max(fis_nolar) + 1 if fis_nolar else 1


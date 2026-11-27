"""Yönetici ve kurucu için Streamlit Secrets içeriği üretir.

Proje kökünde `python olustur_secrets.py` komutuyla çalıştırın.
Parolalar ekrana yazdırılmaz; çıktıdaki TOML bloğunu Streamlit Cloud > Settings > Secrets'e yapıştırın.
"""
from __future__ import annotations

import getpass
import re

from guvenlik import parola_hashle, parola_dogru_mu, _pbkdf2_kaydi_gecerli_mi


def hesap_al(etiket: str, varsayilan_kullanici: str) -> tuple[str, str]:
    while True:
        kullanici = input(f"{etiket} kullanıcı adı [{varsayilan_kullanici}]: ").strip() or varsayilan_kullanici
        if re.fullmatch(r"[A-Za-z0-9_.-]{3,64}", kullanici):
            break
        print("Kullanıcı adı 3-64 karakter olmalı; yalnızca İngilizce harf, rakam, nokta, tire ve alt çizgi kullanın.")

    while True:
        parola = getpass.getpass(f"{etiket} parolası (en az 12 karakter): ")
        tekrar = getpass.getpass("Parolayı tekrar girin: ")
        if len(parola) < 12:
            print("Parola en az 12 karakter olmalı.")
        elif parola != tekrar:
            print("Parolalar eşleşmedi.")
        else:
            ozet = parola_hashle(parola)
            # Üretilen değeri ekrana vermeden önce biçimini ve parolayı doğrula.
            if not _pbkdf2_kaydi_gecerli_mi(ozet) or not parola_dogru_mu(parola, ozet):
                print("Parola özeti doğrulanamadı. Lütfen yeniden deneyin.")
                continue
            return kullanici, ozet


def main() -> None:
    print("Güvenli Okul — iki ayrı rol için güvenli Secrets üretimi")
    print("Parolalar terminalde görünmez ve bu araç tarafından dosyaya kaydedilmez.\n")
    yonetici = hesap_al("YÖNETİCİ", "okul_yonetici")
    kurucu = hesap_al("KURUCU", "kurucu")
    if yonetici[0].casefold() == kurucu[0].casefold():
        raise SystemExit("Yönetici ve kurucu kullanıcı adları farklı olmalıdır. Aracı yeniden çalıştırın.")

    print("\nÖNEMLİ: Aşağıdaki iki password_hash satırının tamamını kopyalayın.")
    print("Örnek dosyadaki BURAYA_... metinlerini kullanmayın.\n")
    print("--- STREAMLIT SECRETS BAŞLANGIÇ ---")
    print("[hesaplar.yonetici]")
    print(f'username = "{yonetici[0]}"')
    print(f'password_hash = "{yonetici[1]}"')
    print("\n[hesaplar.kurucu]")
    print(f'username = "{kurucu[0]}"')
    print(f'password_hash = "{kurucu[1]}"')
    print("\n[uygulama]")
    print('demo_modu = "true"')
    print("--- STREAMLIT SECRETS BİTİŞ ---")
    print("\nYukarıdaki TOML bloğunu Streamlit Cloud > Manage app > Settings > Secrets alanına yapıştırın.")


if __name__ == "__main__":
    main()

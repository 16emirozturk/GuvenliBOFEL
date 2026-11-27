# Güvenli Okul v3.1.6 — hesap ayarı ve dil düzeltmeleri

## Düzeltilenler
- Yönetici/kurucu Secrets parola özeti doğrulama hatası için daha açık teşhis eklendi. Örnek placeholder değerinin gerçek PBKDF2 özeti olmadığı net biçimde belirtilir.
- `olustur_secrets.py` ürettiği PBKDF2 özetini çıktı vermeden önce kendi içinde doğrular.
- Windows bilgisayarda çift tıklayarak çalıştırılabilmesi için `OLUSTUR_SECRETS.bat` eklendi.
- Secrets üretiminde iki ayrı rol için en az 12 karakterli farklı parolalar istenir; parolalar dosyaya kaydedilmez.
- Yardım Merkezi'ndeki dört adım ve açıklamaları Almanca, Fransızca, İspanyolca, Arapça ve Azerbaycanca için gözden geçirilerek eklendi.
- Hesap yapılandırma hatalarının ilgili dillerde gösterimi eklendi.
- Arapça sağdan-sola düzeni ve Latin takip kodlarının soldan-sağa gösterimi korunmuştur.

## Korunanlar
- `stil.py` ve mevcut CSS/renkler/menü düzeni değiştirilmedi.
- Yönetici ve kurucu rol ayrımı ile sayfa yetki listesi korundu.
- 30 dakika oturum zaman aşımı, 5 hatalı girişte 5 dakika kilit ve sistem geneli başarısız giriş sınırı korundu.
- PDF font dosyaları ve PDF fallback kodu korundu.
- Otomatik veri silme eklenmedi.
- Gerçek veritabanı ve gerçek Secrets dosyası ZIP'e eklenmedi.

## Kurulum
1. ZIP'i çıkarın ve içindeki proje dosyalarını GitHub deposunun kök dizinine yükleyin.
2. Windows'ta `OLUSTUR_SECRETS.bat` dosyasını çift tıklayın (veya `py olustur_secrets.py` çalıştırın).
3. Programın ürettiği TOML bloğunun tamamını Streamlit Cloud → Manage app → Settings → Secrets alanına yapıştırın.
4. `secrets.toml.example` içindeki `BURAYA_...` örneklerini gerçek hesap bilgisi olarak kullanmayın.
5. Kaydedip Streamlit uygulamasını yeniden başlatın. Gerçek `secrets.toml` dosyasını GitHub'a yüklemeyin.

## Test sınırı
Bu sürümde yerel Python testleri çalıştırılmıştır. Streamlit Cloud üzerinde gerçek giriş ve tarayıcı testi bu ortamdan yapılamamıştır. Dil düzeltmeleri tüm uygulamanın eksiksiz dil denetimi olarak sunulmamaktadır; bu sürüm özellikle ekran görüntüsündeki Yardım Merkezi ve hesap ayarı hatalarını düzeltir.

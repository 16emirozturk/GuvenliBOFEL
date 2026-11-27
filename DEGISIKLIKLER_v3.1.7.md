# Güvenli Okul v3.1.7 — hesap ve PDF erişim kontrolü

## Bu sürümde doğrulananlar
- Yönetici ve Kurucu ayrı girişleri `[hesaplar.yonetici]` ve `[hesaplar.kurucu]` Secrets tablolarını kullanır. İki hesap da geçerli PBKDF2 özeti gerektirir.
- PDF proje raporu rol matriksinde hem Yönetici hem Kurucu için izinlidir. PDF yalnızca toplu istatistik içerir; bildirim açıklamaları ve takip kodları rapora eklenmez.
- Yönetici bildirim inceleme, Etki Merkezi ve önleyici takvim alanlarına erişir; Kurucu bu bireysel bildirim alanlarına erişemez.
- Oturum zaman aşımı ve hatalı giriş sınırları değiştirilmemiştir.
- PDF font fallback kodu ve mevcut arayüz korunmuştur.

## Secrets kurulumu
1. `py olustur_secrets.py` komutunu proje kökünde çalıştırın.
2. İki farklı, en az 12 karakterli parola belirleyin.
3. Programın ürettiği TOML bloğunun tamamını Streamlit Cloud → Manage app → Settings → Secrets alanına yapıştırın.
4. Örnek dosyadaki `BURAYA_...` yer tutucularını kullanmayın. Gerçek `secrets.toml` dosyasını GitHub'a yüklemeyin.
5. Kaydedip uygulamayı yeniden başlatın.

## Test sınırı
Yerel testler ve Python sözdizimi kontrolü çalıştırılmıştır. Canlı Streamlit Cloud oturumu bu ortamdan test edilemez. Bu nedenle bu paket için canlı dağıtımın hatasız olduğu iddia edilmez.

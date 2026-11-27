# Güvenli Okul v3.1.4 — Değişiklikler

## Çoklu yönetici desteği
- Tek `[admin]` giriş yapısı yerine `[admins.<hesap_etiketi>]` biçiminde birden fazla hesap tanımlanabilir.
- Varsayılan örnek hesaplar `okul_muduru` ve `rehberlik` kullanıcı adlarıdır; parola özetleri kullanıcı tarafından üretilmelidir. ZIP'te gerçek parola veya gerçek secrets dosyası yoktur.
- En fazla 10 hesap; benzersiz, büyük/küçük harfe duyarsız kullanıcı adları; yeni hesaplarda PBKDF2 özeti doğrulaması uygulanır.
- Eski `[admin]` hesabı geçiş kolaylığı için desteklenir.
- Giriş yapan hesap adı `session_state` ve yönetim denetim kaydında kullanılır.
- Ayarlardan kaldırılan bir yönetici, sonraki oturum kontrolünde dışarı çıkarılır.

## Korunan güvenlik davranışları
- 30 dakika hareketsizlikte oturum zaman aşımı aynen korunmuştur.
- Oturum başına 5 hatalı giriş sonrası 5 dakika kilit aynen korunmuştur.
- Son 15 dakikada veritabanı genelinde 20 hatalı giriş kontrolü aynen korunmuştur.
- Öğrenci ekranlarının yönetici inceleme/istatistik/denetim sayfalarına erişim kontrolleri değiştirilmemiştir.
- Otomatik veri silme/retention özelliği eklenmemiştir.

## Arayüz ve veri tabanı
- Mevcut Streamlit sayfa yerleşimi, CSS, renkler, menüler ve SQLite şeması değiştirilmemiştir.
- Veritabanı dosyası ve gerçek `.streamlit/secrets.toml` pakete dahil değildir.
- PDF font/fallback düzeltmeleri ve önceki dosya yapısı korunmuştur.

## Kurulum
1. ZIP'i çıkarın, içindekileri mevcut GitHub deposunun köküne yükleyin.
2. Yerelde `.streamlit/secrets.toml.example` dosyasını `.streamlit/secrets.toml` olarak kopyalayın.
3. Her yönetici parolası için ayrı PBKDF2 üretin: `py -c "import getpass; from guvenlik import parola_hashle; print(parola_hashle(getpass.getpass('Yonetici parolasi: ')))"`.
4. Üretilen hash değerlerini uygun `[admins.*]` bölümlerine yazın. Örnek hash yer tutucularını değiştirmeden bırakmayın.
5. Streamlit Cloud kullanılıyorsa aynı TOML içeriğini **Settings → Secrets** alanına yapıştırın; gerçek secrets dosyasını GitHub'a yüklemeyin.
6. `pytest -q` ile testleri çalıştırın ve Streamlit uygulamasını yeniden başlatın.

## Yetki kapsamı
Bu sürüm birden fazla ayrı kullanıcı hesabı sağlar; tüm hesaplar mevcut yönetici yetkilerine sahiptir. Müdür/rehberlik için ayrı erişim matrisi veya farklı ekran yetkisi bu pakete dahil değildir.

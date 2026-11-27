# Güvenli Okul v3.1.5 — Yönetici / Kurucu rol ayrımı

## Yeni özellikler
- Ayrı **Yönetici girişi** ve **Kurucu girişi** sayfaları eklendi.
- İki hesap `secrets.toml` içinde `[hesaplar.yonetici]` ve `[hesaplar.kurucu]` olarak tanımlanır.
- Her hesap kendi giriş ekranında doğrulanır; diğer rolün kimlik bilgileriyle geçiş yapılamaz.
- Her iki hesap için ayrı PBKDF2 özeti zorunludur. `olustur_secrets.py` aracı parolaları terminalde göstermeden Secrets TOML bloğu üretir.

## Yetki ayrımı
- **Yönetici:** bireysel bildirim inceleme, durum/birim güncelleme, inceleme notları, SLA bildirim merkezi, Etki Merkezi ve önleyici çalışma takvimi.
- **Kurucu:** toplu istatistikler, trendler, toplu PDF raporu, yönetim günlüğü, veritabanı yedekleme ve geri yükleme.
- Kurucu hesabı bireysel bildirim açıklamalarını, takip kodlarını ve CSV dışa aktarım alanını açamaz.
- Her iki rol de öğrenci/ziyaretçi hesaplarından tamamen ayrıdır.

## Korunan davranışlar
- 30 dakika hareketsizlikte oturum zaman aşımı.
- Oturum başına 5 hatalı denemede 5 dakika kilit.
- Veritabanı genelinde 15 dakikalık hatalı giriş kontrolü.
- Denetim günlüğüne gerçek kullanıcı adının yazılması.
- Oturumdaki rol yapılandırmadan kaldırılırsa sonraki kontrolde oturumun kapanması.
- PDF font yedekleri, mevcut sayfa tasarımı, logo, veritabanı şeması ve otomatik veri silmeme politikası korunur.

## Streamlit Cloud Secrets
1. Proje kökünde `python olustur_secrets.py` çalıştırın.
2. Yönetici ve kurucu için ayrı, en az 12 karakterlik parolalar girin.
3. Araç tarafından yazdırılan TOML bloğunun tamamını Manage app → Settings → Secrets alanına yapıştırın.
4. Uygulamayı yeniden başlatın. Gerçek `secrets.toml` içeriğini GitHub'a yüklemeyin.

## Test kapsamı
- İki rol için ayrı hesap yükleme ve parola doğrulaması.
- Yanlış giriş ekranında diğer rolün hesabının reddedilmesi.
- Aynı kullanıcı adının iki rolde kullanılmasının reddedilmesi.
- Eksik rol yapılandırmasının reddedilmesi.
- Yönetici ve kurucu sayfa izinlerinin kontrolü.

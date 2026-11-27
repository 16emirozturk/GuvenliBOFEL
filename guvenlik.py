"""Kimlik doğrulama yardımcıları ve kişisel veri maskeleme.

Streamlit'e bağımlı değildir; bağımsız test edilebilir.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets

_PBKDF2_ONEK = "pbkdf2_sha256"
_PBKDF2_ITERASYON = 600_000


# ---------------------------------------------------------------- parola
def _b(metin: str) -> bytes:
    return metin.encode("utf-8")


def sabit_zamanli_esit(a: str, b: str) -> bool:
    """hmac.compare_digest str ile yalnızca ASCII kabul eder (ş, ğ, ı TypeError verir);
    bu yüzden UTF-8 bayta çevrilir."""
    return hmac.compare_digest(_b(a), _b(b))


def parola_hashle(parola: str, iterasyon: int = _PBKDF2_ITERASYON) -> str:
    tuz = secrets.token_bytes(16)
    ozet = hashlib.pbkdf2_hmac("sha256", _b(parola), tuz, iterasyon)
    return f"{_PBKDF2_ONEK}${iterasyon}${tuz.hex()}${ozet.hex()}"


def parola_dogru_mu(parola: str, kayit: str) -> bool:
    """`kayit` PBKDF2 özeti ya da (yalnızca geliştirme için) düz metin olabilir."""
    if not kayit:
        return False
    if kayit.startswith(_PBKDF2_ONEK + "$"):
        try:
            _, it, tuz, ozet = kayit.split("$")
            hesap = hashlib.pbkdf2_hmac("sha256", _b(parola), bytes.fromhex(tuz), int(it))
            return hmac.compare_digest(hesap, bytes.fromhex(ozet))
        except (ValueError, TypeError):
            return False
    return sabit_zamanli_esit(parola, kayit)


def kimlik_dogrula(kullanici: str, parola: str, beklenen_kullanici: str, beklenen_parola: str) -> bool:
    """İki kontrol de her zaman çalışır (hangisinin hatalı olduğu zamanlamadan sızmaz)."""
    k = sabit_zamanli_esit(kullanici, beklenen_kullanici) if beklenen_kullanici else False
    p = parola_dogru_mu(parola, beklenen_parola)
    return k and p

def _pbkdf2_kaydi_gecerli_mi(kayit: str) -> bool:
    """Yeni çoklu yönetici hesapları için PBKDF2 kayıt biçimini doğrular."""
    try:
        # Streamlit Secrets'ten kopyalanırken satır başı/sonu boşlukları
        # gelebilir; yalnızca dış boşlukları temizle, özetin içini değiştirme.
        kayit = str(kayit).strip()
        onek, iterasyon, tuz_hex, ozet_hex = kayit.split("$")
        iterasyon_sayisi = int(iterasyon)
        tuz = bytes.fromhex(tuz_hex)
        ozet = bytes.fromhex(ozet_hex)
        return (
            onek == _PBKDF2_ONEK
            and 100_000 <= iterasyon_sayisi <= 1_000_000
            and len(tuz) >= 16
            and len(ozet) == 32
        )
    except (AttributeError, TypeError, ValueError):
        return False


def yonetici_hesaplarini_yukle(secret_ayarlari) -> tuple[list[dict[str, str]], str]:
    """Streamlit secrets içinden birden çok yöneticiyi güvenli biçimde yükler.

    Yeni biçim: [admins.mudur] / [admins.rehberlik]. Her hesap PBKDF2 özeti
    kullanmalıdır. Eski [admin] biçimi, geçişi kolaylaştırmak için desteklenir.
    Dönüş: (hesap listesi, hata mesajı).
    """
    try:
        coklu_ayar_var = "admins" in secret_ayarlari
    except Exception:
        coklu_ayar_var = False

    if coklu_ayar_var:
        try:
            coklu_ayar = secret_ayarlari["admins"]
            kayitlar = list(coklu_ayar.items())
        except Exception:
            return [], "[admins] bölümü geçerli bir TOML tablosu olmalıdır."

        if not kayitlar:
            return [], "[admins] altında en az bir yönetici hesabı tanımlanmalıdır."
        if len(kayitlar) > 10:
            return [], "En fazla 10 yönetici hesabı tanımlanabilir."

        hesaplar: list[dict[str, str]] = []
        gorulen_kullanicilar: set[str] = set()
        for hesap_etiketi, ayar in kayitlar:
            if not hasattr(ayar, "get"):
                return [], f"'{hesap_etiketi}' hesabı geçerli bir TOML alt tablosu değil."

            kullanici = str(ayar.get("username", "")).strip()
            parola_hash = str(ayar.get("password_hash", "")).strip()
            if not kullanici or not parola_hash:
                return [], f"'{hesap_etiketi}' hesabında username ve password_hash zorunludur."
            if len(kullanici) > 64:
                return [], "Yönetici kullanıcı adı 64 karakterden uzun olamaz."
            if not _pbkdf2_kaydi_gecerli_mi(parola_hash):
                return [], (
                    f"'{hesap_etiketi}' hesabının password_hash değeri geçersiz. "
                    "guvenlik.parola_hashle() ile yeni PBKDF2 özeti oluşturun."
                )

            anahtar = kullanici.casefold()
            if anahtar in gorulen_kullanicilar:
                return [], "Yönetici kullanıcı adları büyük/küçük harf farkı olmadan benzersiz olmalıdır."
            gorulen_kullanicilar.add(anahtar)
            hesaplar.append({"username": kullanici, "password_hash": parola_hash})

        return hesaplar, ""

    # Eski tek hesap biçimine geçici geriye dönük uyumluluk.
    try:
        eski_ayar = secret_ayarlari.get("admin", {})
    except Exception:
        eski_ayar = {}
    if hasattr(eski_ayar, "get"):
        eski_kullanici = str(eski_ayar.get("username", "")).strip()
        eski_parola = str(eski_ayar.get("password_hash") or eski_ayar.get("password") or "")
        if eski_kullanici and eski_parola:
            return [{"username": eski_kullanici, "password_hash": eski_parola}], ""

    return [], ""


def kimlik_dogrula_hesaplar(kullanici: str, parola: str, hesaplar) -> str | None:
    """Çoklu yönetici doğrulaması; doğruysa hesap kullanıcı adını, değilse None döndürür.

    Her hesap için parola kontrolü yapılır ve tüm hatalarda aynı genel sonuç kullanılır.
    Kullanıcı adları trim + Unicode casefold ile büyük/küçük harfe duyarsızdır.
    """
    girilen_kullanici = str(kullanici or "").strip().casefold()
    girilen_parola = str(parola or "")
    eslesen_yonetici = None

    try:
        hesap_listesi = list(hesaplar)
    except (TypeError, ValueError):
        return None

    for hesap in hesap_listesi:
        if not hasattr(hesap, "get"):
            continue
        beklenen_kullanici = str(hesap.get("username", "")).strip()
        kayitli_parola = str(hesap.get("password_hash") or hesap.get("password") or "")
        kullanici_dogru = (
            sabit_zamanli_esit(girilen_kullanici, beklenen_kullanici.casefold())
            if beklenen_kullanici else False
        )
        parola_dogru = parola_dogru_mu(girilen_parola, kayitli_parola)
        if kullanici_dogru and parola_dogru:
            eslesen_yonetici = beklenen_kullanici

    return eslesen_yonetici


# ------------------------------------------------------ iki ayrı yönetici rolü
ROL_ETIKETLERI = {"yonetici": "Yönetici", "kurucu": "Kurucu"}

# Veri minimizasyonu ilkesi: Kurucu teknik/araştırma alanlarını görür ancak
# bireysel bildirim açıklamalarına, takip kodlarına veya CSV dışa aktarımına erişemez.
SAYFA_YETKILERI = {
    "Bildirim inceleme": frozenset({"yonetici"}),
    "Etki Merkezi": frozenset({"yonetici"}),
    "Önleyici çalışma takvimi": frozenset({"yonetici"}),
    "Yönetici bildirim merkezi": frozenset({"yonetici"}),
    "İstatistikler": frozenset({"yonetici", "kurucu"}),
    "Trend ve ortam": frozenset({"yonetici", "kurucu"}),
    # Toplu ve kimliksiz PDF raporu iki yönetim rolüne de açıktır.
    "PDF proje raporu": frozenset({"yonetici", "kurucu"}),
    "Yönetim günlüğü": frozenset({"kurucu"}),
    "Yedekleme ve geri yükleme": frozenset({"kurucu"}),
}
KORUMALI_SAYFALAR = frozenset(SAYFA_YETKILERI)


def sayfaya_erisim_var_mi(rol: str, sayfa: str) -> bool:
    """Bir rolün ilgili yönetim sayfasına erişip erişemediğini döndürür."""
    return rol in SAYFA_YETKILERI.get(sayfa, frozenset())


def rol_hesaplarini_yukle(secret_ayarlari) -> tuple[dict[str, dict[str, str]], str]:
    """Streamlit Secrets içindeki [hesaplar.yonetici] ve [hesaplar.kurucu] bölümlerini yükler.

    Her rolde tek hesap vardır. Kullanıcı adları benzersiz, parola alanları PBKDF2
    özetli olmalıdır. Eski [admins] listesi roller belirtmediğinden otomatik yetki
    ataması yapılmaz; yapılandırma açıkça güncellenmelidir.
    """
    try:
        tum_hesaplar = secret_ayarlari.get("hesaplar", {})
    except Exception:
        tum_hesaplar = {}
    if not hasattr(tum_hesaplar, "get"):
        return {}, "[hesaplar] bölümü geçerli bir TOML tablosu olmalıdır."

    sonuc: dict[str, dict[str, str]] = {}
    kullanici_adlari: set[str] = set()
    for rol in ("yonetici", "kurucu"):
        try:
            ayar = tum_hesaplar.get(rol, {})
        except Exception:
            ayar = {}
        if not hasattr(ayar, "get"):
            return {}, f"[hesaplar.{rol}] geçerli bir TOML alt tablosu olmalıdır."

        kullanici = str(ayar.get("username", "")).strip()
        parola_hash = str(ayar.get("password_hash", "")).strip()
        if not kullanici or not parola_hash:
            return {}, (f"[hesaplar.{rol}] bölümünde username ve password_hash zorunludur. "
                        "İki hesap da tanımlanmalıdır.")
        if len(kullanici) < 3 or len(kullanici) > 64:
            return {}, f"{ROL_ETIKETLERI[rol]} kullanıcı adı 3-64 karakter olmalıdır."
        if not _pbkdf2_kaydi_gecerli_mi(parola_hash):
            return {}, (f"[hesaplar.{rol}] password_hash geçersiz veya örnek değer olarak bırakılmış. "
                        "Streamlit Secrets alanındaki değeri, proje ZIP'indeki olustur_secrets.py "
                        "aracının ürettiği TAM pbkdf2_sha256$... satırıyla değiştirin. "
                        "Tırnakları koruyun; başına/sonuna açıklama veya üç nokta eklemeyin.")
        anahtar = kullanici.casefold()
        if anahtar in kullanici_adlari:
            return {}, "Yönetici ve kurucu kullanıcı adları birbirinden farklı olmalıdır."
        kullanici_adlari.add(anahtar)
        sonuc[rol] = {"role": rol, "username": kullanici, "password_hash": parola_hash}

    return sonuc, ""


def kimlik_dogrula_rol(kullanici: str, parola: str, hesap) -> bool:
    """Yalnızca kendisine ait giriş ekranındaki tek hesabı doğrular."""
    beklenen_kullanici = str(hesap.get("username", "")) if hasattr(hesap, "get") else ""
    kayitli_parola = str(hesap.get("password_hash", "")) if hasattr(hesap, "get") else ""
    girilen_kullanici = str(kullanici or "").strip().casefold()
    kullanici_dogru = (
        sabit_zamanli_esit(girilen_kullanici, beklenen_kullanici.casefold())
        if beklenen_kullanici else False
    )
    parola_dogru = parola_dogru_mu(str(parola or ""), kayitli_parola)
    return kullanici_dogru and parola_dogru


# ------------------------------------------------------ kişisel veri maskeleme
def tc_kimlik_gecerli_mi(deger: str) -> bool:
    if not re.fullmatch(r"[1-9]\d{10}", deger):
        return False
    d = [int(c) for c in deger]
    if (sum(d[0:9:2]) * 7 - sum(d[1:8:2])) % 10 != d[9]:
        return False
    return sum(d[:10]) % 10 == d[10]


_IBAN = re.compile(r"(?<![A-Za-z0-9])TR\d{2}(?:\s?\d{4}){5}\s?\d{2}(?!\d)", re.I)
_EPOSTA = re.compile(r"[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+")
_TC = re.compile(r"(?<!\d)\d{11}(?!\d)")
_TELEFON = re.compile(
    r"(?<!\d)(?:\+?90[\s\-]*|0[\s\-]*)?\(?5\d{2}\)?[\s\-]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}(?!\d)"
)


def hassas_veri_maskele(metin: str) -> tuple[str, list[str]]:
    """Serbest metindeki T.C. kimlik no, telefon, e-posta ve IBAN'ı maskeler.

    Dönüş: (maskeli_metin, bulunan_türler). Ad-soyad, adres, okul numarası gibi
    yapısız bilgileri yakalayamaz; bu yüzden kullanıcı uyarısı ayrıca gereklidir.
    """
    bulunan: set[str] = set()

    def degistir(etiket, tur, kosul=None):
        def _f(m):
            if kosul and not kosul(m.group(0)):
                return m.group(0)
            bulunan.add(tur)
            return etiket
        return _f

    metin = _IBAN.sub(degistir("[IBAN]", "IBAN"), metin)
    metin = _EPOSTA.sub(degistir("[E-POSTA]", "e-posta"), metin)
    metin = _TC.sub(degistir("[T.C. KİMLİK NO]", "T.C. kimlik no", tc_kimlik_gecerli_mi), metin)
    metin = _TELEFON.sub(degistir("[TELEFON]", "telefon"), metin)
    return metin, sorted(bulunan)


# ------------------------------------------------------------- dışa aktarım
def csv_hucre_temizle(deger) -> str:
    """CSV/Excel formül enjeksiyonunu (=, +, -, @ ile başlayan hücreler) etkisizleştirir."""
    s = "" if deger is None else str(deger)
    return "'" + s if s[:1] in ("=", "+", "-", "@", "\t", "\r") else s

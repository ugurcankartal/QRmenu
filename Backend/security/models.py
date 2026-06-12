from django.conf import settings
from django.db import models


class LoginAttemptState(models.Model):
    """Brute-force korumasi: IP basina ard arda basarisiz giris sayaci."""

    ip_address = models.GenericIPAddressField(unique=True, verbose_name="IP adresi")
    failed_attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Basarisiz deneme",
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Kilit bitis zamani",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Guncellendi")

    class Meta:
        db_table = "api_loginattemptstate"
        verbose_name = "Giris deneme durumu"
        verbose_name_plural = "Giris deneme durumlari"

    def __str__(self):
        return f"{self.ip_address} ({self.failed_attempts})"


class FrontendLoginAudit(models.Model):
    class EventType(models.TextChoices):
        SUCCESS = "success", "Basarili giris"
        FAILED = "failed", "Basarisiz giris"
        BLOCKED = "blocked", "Kilitli (cok deneme)"
        FORBIDDEN_ROLE = "forbidden_role", "Yetkisiz rol"
        VALIDATION_ERROR = "validation_error", "Eksik alan"

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")
    event_type = models.CharField(
        max_length=32,
        choices=EventType.choices,
        verbose_name="Olay",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="frontend_login_audits",
        verbose_name="Kullanici",
    )
    username_attempted = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Denenen kullanici adi",
    )
    failure_reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Hata nedeni",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    forwarded_for = models.TextField(blank=True, verbose_name="X-Forwarded-For")
    country_code = models.CharField(max_length=8, blank=True, verbose_name="Ulke kodu")
    country_name = models.CharField(max_length=100, blank=True, verbose_name="Ulke")
    city = models.CharField(max_length=120, blank=True, verbose_name="Sehir")
    region = models.CharField(max_length=120, blank=True, verbose_name="Bolge")
    postal_code = models.CharField(max_length=32, blank=True, verbose_name="Posta kodu")
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Enlem",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Boylam",
    )
    location_label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Konum ozeti",
    )
    user_agent = models.TextField(blank=True, verbose_name="User-Agent")
    browser_name = models.CharField(max_length=80, blank=True, verbose_name="Tarayici")
    browser_version = models.CharField(max_length=40, blank=True, verbose_name="Tarayici surumu")
    os_name = models.CharField(max_length=80, blank=True, verbose_name="Isletim sistemi")
    os_version = models.CharField(max_length=40, blank=True, verbose_name="OS surumu")
    device_type = models.CharField(max_length=40, blank=True, verbose_name="Cihaz tipi")
    device_brand = models.CharField(max_length=80, blank=True, verbose_name="Cihaz markasi")
    device_model = models.CharField(max_length=120, blank=True, verbose_name="Cihaz modeli")
    accept_language = models.CharField(max_length=255, blank=True, verbose_name="Accept-Language")
    referer = models.TextField(blank=True, verbose_name="Referer")
    host = models.CharField(max_length=255, blank=True, verbose_name="Host")
    request_method = models.CharField(max_length=16, blank=True, verbose_name="HTTP metodu")
    request_path = models.CharField(max_length=512, blank=True, verbose_name="Istek yolu")
    is_secure = models.BooleanField(default=False, verbose_name="HTTPS")
    is_mobile = models.BooleanField(default=False, verbose_name="Mobil")
    is_bot = models.BooleanField(default=False, verbose_name="Bot")
    security_headers = models.JSONField(default=dict, blank=True, verbose_name="Guvenlik basliklari")

    class Meta:
        db_table = "api_frontendloginaudit"
        verbose_name = "On yuz giris kaydi"
        verbose_name_plural = "On yuz giris kayitlari"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"], name="api_fronten_created_773e59_idx"),
            models.Index(
                fields=["ip_address", "-created_at"],
                name="api_fronten_ip_addr_a72d4b_idx",
            ),
            models.Index(
                fields=["username_attempted", "-created_at"],
                name="api_fronten_usernam_22f40c_idx",
            ),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} — {self.username_attempted or '—'} ({self.ip_address})"


class SqlInjectionAttempt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    forwarded_for = models.TextField(blank=True, verbose_name="X-Forwarded-For")
    country_code = models.CharField(max_length=8, blank=True, verbose_name="Ulke kodu")
    country_name = models.CharField(max_length=100, blank=True, verbose_name="Ulke")
    city = models.CharField(max_length=120, blank=True, verbose_name="Sehir")
    region = models.CharField(max_length=120, blank=True, verbose_name="Bolge")
    location_label = models.CharField(max_length=255, blank=True, verbose_name="Konum ozeti")
    user_agent = models.TextField(blank=True, verbose_name="User-Agent")
    browser_name = models.CharField(max_length=80, blank=True, verbose_name="Tarayici")
    os_name = models.CharField(max_length=80, blank=True, verbose_name="Isletim sistemi")
    device_type = models.CharField(max_length=40, blank=True, verbose_name="Cihaz tipi")
    is_mobile = models.BooleanField(default=False, verbose_name="Mobil")
    is_bot = models.BooleanField(default=False, verbose_name="Bot")
    request_method = models.CharField(max_length=16, blank=True, verbose_name="HTTP metodu")
    request_path = models.CharField(max_length=512, blank=True, verbose_name="Istek yolu")
    query_string = models.TextField(blank=True, verbose_name="Query string")
    request_body = models.TextField(blank=True, verbose_name="Istek govdesi (kisaltilmis)")
    matched_pattern = models.CharField(max_length=255, verbose_name="Eslesen kalip")
    matched_value = models.TextField(blank=True, verbose_name="Eslesen deger (kisaltilmis)")
    source = models.CharField(max_length=64, blank=True, verbose_name="Kaynak alan")
    security_headers = models.JSONField(default=dict, blank=True, verbose_name="Guvenlik basliklari")

    class Meta:
        db_table = "api_sqlinjectionattempt"
        verbose_name = "SQL injection girisimi"
        verbose_name_plural = "SQL injection girisimleri"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"], name="api_sqlinje_created_8e7f86_idx"),
            models.Index(
                fields=["ip_address", "-created_at"],
                name="api_sqlinje_ip_addr_132ec6_idx",
            ),
        ]

    def __str__(self):
        return f"{self.ip_address} — {self.matched_pattern[:60]}"


class SitePageVisit(models.Model):
    class VisitSource(models.TextChoices):
        FRONTEND_ROUTE = "frontend_route", "On yuz sayfasi"
        SERVER_REQUEST = "server_request", "Sunucu istegi"

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")
    page_path = models.CharField(max_length=512, verbose_name="Sayfa yolu")
    query_string = models.CharField(max_length=512, blank=True, verbose_name="Query string")
    visit_source = models.CharField(
        max_length=32,
        choices=VisitSource.choices,
        default=VisitSource.FRONTEND_ROUTE,
        verbose_name="Kaynak",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="site_page_visits",
        verbose_name="Kullanici",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    forwarded_for = models.TextField(blank=True, verbose_name="X-Forwarded-For")
    country_code = models.CharField(max_length=8, blank=True, verbose_name="Ulke kodu")
    country_name = models.CharField(max_length=100, blank=True, verbose_name="Ulke")
    city = models.CharField(max_length=120, blank=True, verbose_name="Sehir")
    region = models.CharField(max_length=120, blank=True, verbose_name="Bolge")
    postal_code = models.CharField(max_length=32, blank=True, verbose_name="Posta kodu")
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Enlem",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Boylam",
    )
    location_label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Konum ozeti",
    )
    user_agent = models.TextField(blank=True, verbose_name="User-Agent")
    browser_name = models.CharField(max_length=80, blank=True, verbose_name="Tarayici")
    browser_version = models.CharField(max_length=40, blank=True, verbose_name="Tarayici surumu")
    os_name = models.CharField(max_length=80, blank=True, verbose_name="Isletim sistemi")
    os_version = models.CharField(max_length=40, blank=True, verbose_name="OS surumu")
    device_type = models.CharField(max_length=40, blank=True, verbose_name="Cihaz tipi")
    device_brand = models.CharField(max_length=80, blank=True, verbose_name="Cihaz markasi")
    device_model = models.CharField(max_length=120, blank=True, verbose_name="Cihaz modeli")
    accept_language = models.CharField(max_length=255, blank=True, verbose_name="Accept-Language")
    referer = models.TextField(blank=True, verbose_name="Referer")
    host = models.CharField(max_length=255, blank=True, verbose_name="Host")
    request_method = models.CharField(max_length=16, blank=True, verbose_name="HTTP metodu")
    is_secure = models.BooleanField(default=False, verbose_name="HTTPS")
    is_mobile = models.BooleanField(default=False, verbose_name="Mobil")
    is_bot = models.BooleanField(default=False, verbose_name="Bot")
    security_headers = models.JSONField(default=dict, blank=True, verbose_name="Guvenlik basliklari")

    class Meta:
        verbose_name = "Site ziyareti"
        verbose_name_plural = "Site ziyaretleri"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["page_path", "-created_at"]),
            models.Index(fields=["ip_address", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.page_path} — {self.ip_address or '—'}"

import uuid
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel


class SessionKeyPolicy(TimeStampedModel):
    """Yeni oturumlar için varsayılan yenileme süresi (tek kayıt)."""

    refresh_duration_minutes = models.PositiveIntegerField(
        default=120,
        verbose_name="Yenilenme süresi (dk)",
        help_text="Oturum her etkileşimde bu kadar dakika uzatılır (örn. 120 = 2 saat).",
    )
    max_concurrent_adisyon_sessions = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Eşzamanlı adisyon oturumu limiti",
        help_text=(
            "Yenilenme süresi içinde adisyona ürün ekleyebilen en fazla aktif oturum sayısı. "
            "Boş bırakılırsa sınırsız."
        ),
    )

    class Meta:
        verbose_name = "Oturum anahtarı ayarı"
        verbose_name_plural = "Oturum anahtarı ayarları"

    def __str__(self):
        return f"Yenilenme: {self.refresh_duration_minutes} dk"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={"refresh_duration_minutes": 120},
        )
        return obj


class SessionKey(TimeStampedModel):
    """Müşteri adisyon oturumu."""

    key = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        verbose_name="Anahtar",
    )
    refresh_duration_minutes = models.PositiveIntegerField(
        default=120,
        verbose_name="Yenilenme süresi (dk)",
        help_text="Bu oturum için geçerlilik süresi (dakika).",
    )
    last_activity_at = models.DateTimeField(verbose_name="Son etkinlik")
    expires_at = models.DateTimeField(verbose_name="Son geçerlilik")

    class Meta:
        verbose_name = "Oturum anahtarı"
        verbose_name_plural = "Oturum anahtarları"
        ordering = ["-last_activity_at"]
        indexes = [
            models.Index(fields=["key"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.key[:8]}… ({self.expires_at:%Y-%m-%d %H:%M})"

    @classmethod
    def generate_key(cls) -> str:
        return uuid.uuid4().hex

    def get_policy_refresh_duration_minutes(self) -> int:
        return SessionKeyPolicy.get_solo().refresh_duration_minutes

    @property
    def is_expired(self) -> bool:
        deadline = self.last_activity_at + timedelta(
            minutes=self.get_policy_refresh_duration_minutes(),
        )
        return timezone.now() >= deadline

    @property
    def policy_expires_at(self):
        return self.last_activity_at + timedelta(
            minutes=self.get_policy_refresh_duration_minutes(),
        )


class Adisyon(TimeStampedModel):
    """Oturum anahtarına bağlı sepet (adisyon)."""

    session_key = models.OneToOneField(
        SessionKey,
        on_delete=models.CASCADE,
        related_name="adisyon",
        verbose_name="Oturum anahtarı",
    )
    products = models.ManyToManyField(
        "api.Product",
        through="AdisyonItem",
        related_name="adisyons",
        blank=True,
        verbose_name="Ürünler",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Toplam tutar",
    )
    currency = models.ForeignKey(
        "currency.Currency",
        on_delete=models.PROTECT,
        related_name="adisyons",
        null=True,
        blank=True,
        verbose_name="Para birimi",
    )
    discounted_total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="İndirimli toplam tutar",
    )

    class Meta:
        verbose_name = "Adisyon"
        verbose_name_plural = "Adisyonlar"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Adisyon #{self.pk} ({self.session_key.key[:8]}…)"


class AdisyonItem(TimeStampedModel):
    """Adisyon ile ürün arasındaki ara tablo (adet bilgisi)."""

    adisyon = models.ForeignKey(
        Adisyon,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Adisyon",
    )
    product = models.ForeignKey(
        "api.Product",
        on_delete=models.CASCADE,
        related_name="adisyon_items",
        verbose_name="Ürün",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Adet")
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Sıra",
        help_text="Adisyondaki görüntüleme sırası.",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Birim fiyat",
        help_text="Ürün adisyona eklendiği andaki birim fiyat.",
    )
    currency = models.ForeignKey(
        "currency.Currency",
        on_delete=models.PROTECT,
        related_name="adisyon_items",
        null=True,
        blank=True,
        verbose_name="Para birimi",
        help_text="Ürün adisyona eklendiği andaki para birimi.",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Tutar",
        help_text="Birim fiyat × adet (güncel satır tutarı).",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Toplam tutar",
        help_text="Satır toplamı (birim fiyat × adet).",
    )
    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="İndirimli birim fiyat",
        help_text="Kampanya kuralı uygulandığında birim fiyat (ortalama).",
    )
    campaign_rule = models.ForeignKey(
        "api.CampaignRule",
        on_delete=models.SET_NULL,
        related_name="adisyon_items",
        null=True,
        blank=True,
        verbose_name="Uygulanan kampanya kuralı",
        help_text="Ürün eklendiğinde uygulanan kural anlık görüntüsü.",
    )

    class Meta:
        verbose_name = "Adisyon ürünü"
        verbose_name_plural = "Adisyon ürünleri"
        ordering = ["order", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["adisyon", "product"],
                name="unique_adisyon_product",
            ),
        ]
        indexes = [
            models.Index(fields=["adisyon"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.product_id} x{self.quantity}"

    def save(self, *args, **kwargs):
        from adisyon.services import apply_item_pricing, recalculate_adisyon

        if self._state.adding and self.order == 0:
            self.order = AdisyonItem.objects.filter(
                adisyon_id=self.adisyon_id,
            ).count()

        apply_item_pricing(self, is_new=self._state.adding)
        super().save(*args, **kwargs)
        recalculate_adisyon(self.adisyon)

    def delete(self, *args, **kwargs):
        from adisyon.services import recalculate_adisyon

        adisyon = self.adisyon
        super().delete(*args, **kwargs)
        recalculate_adisyon(adisyon)

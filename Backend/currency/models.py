from django.core.exceptions import ValidationError
from django.db import models

from core.models import TimeStampedModel


class Currency(TimeStampedModel):
    """Para birimleri ve çapraz kur tanımları."""

    code = models.CharField(
        max_length=3,
        unique=True,
        verbose_name="Kod",
        help_text="ISO 4217 para birimi kodu (örn: USD, EUR, TRY)",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Ad",
        help_text="Para biriminin tam adı (örn: US Dollar, Euro, Turkish Lira)",
    )
    symbol = models.CharField(
        max_length=10,
        verbose_name="Sembol",
        help_text="Para birimi sembolü (örn: $, €, ₺)",
    )
    exchange_rates = models.ManyToManyField(
        "self",
        through="CurrencyExchangeRate",
        symmetrical=False,
        through_fields=("from_currency", "to_currency"),
        related_name="reverse_exchange_rates",
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktif",
        help_text="Bu para birimi aktif mi?",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Sıra",
        help_text="Görüntüleme sırası",
    )

    class Meta:
        verbose_name = "Para Birimi"
        verbose_name_plural = "Para Birimleri"
        ordering = ["order", "code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name} ({self.symbol})"


class CurrencyExchangeRate(TimeStampedModel):
    """Kaynak → hedef para birimi çifti için alış/satış kurları."""

    from_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="from_currency_exchange_rates",
        verbose_name="Kaynak Para Birimi",
    )
    to_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="Hedef Para Birimi",
    )
    buy_rate = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        default=1.000000,
        verbose_name="Alış",
    )
    sell_rate = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        default=1.000000,
        verbose_name="Satış",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Para Birimi Çapraz Kuru"
        verbose_name_plural = "Para Birimi Çapraz Kurları"
        ordering = ["from_currency", "to_currency"]
        constraints = [
            models.UniqueConstraint(
                fields=["from_currency", "to_currency"],
                name="unique_currency_exchange_pair",
            ),
        ]
        indexes = [
            models.Index(fields=["from_currency"]),
            models.Index(fields=["to_currency"]),
        ]

    def __str__(self):
        return (
            f"{self.from_currency.code} -> {self.to_currency.code} "
            f"(Alış: {self.buy_rate}, Satış: {self.sell_rate})"
        )

    def clean(self):
        if (
            self.from_currency_id
            and self.to_currency_id
            and self.from_currency_id == self.to_currency_id
        ):
            raise ValidationError(
                {"to_currency": "Kaynak para birimi ile hedef para birimi aynı olamaz."}
            )


class ProductCurrency(TimeStampedModel):
    """Her ürün için tek para birimi (OneToOne)."""

    product = models.OneToOneField(
        "api.Product",
        on_delete=models.CASCADE,
        related_name="product_currency",
        verbose_name="Ürün",
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="product_currencies",
        verbose_name="Para Birimi",
    )

    class Meta:
        verbose_name = "Ürün Para Birimi"
        verbose_name_plural = "Ürün Para Birimleri"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["currency"]),
        ]

    def __str__(self):
        return f"{self.product} - {self.currency.code} ({self.currency.symbol})"

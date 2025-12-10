from django.conf import settings
from django.db import models
from nxtbn.core import CurrencyTypes, MoneyFieldTypes
from nxtbn.core.mixin import MonetaryMixin
from nxtbn.core.models import AbstractBaseModel, AbstractTranslationModel
from django_countries.fields import CountryField
from decimal import Decimal

class ShippingMethod(AbstractBaseModel):
    """
    Represents different shipping methods offered by a carrier, such as Standard or Express Shipping.

    Fields:
        - name: The name of the shipping method (e.g., "Express Shipping").
        - description: An optional text field to provide a detailed description of the method.
        - carrier: The name of the shipping carrier offering the method (e.g., "FedEx", "DHL").

    Examples:
        - FedEx - Standard Shipping
        - DHL - Express Shipping
    """
    name = models.CharField(
        max_length=200, 
        help_text="The name of the shipping method, e.g., 'Standard Shipping'."
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        help_text="Optional detailed description of the shipping method."
    )
    carrier = models.CharField(
        max_length=200, 
        help_text="Shipping carrier, e.g., 'FedEx', 'DHL'."
    )

    def __str__(self):
        """
        Returns a human-readable representation of the ShippingMethod instance.
        Example: "FedEx - Express Shipping"
        """
        return f"{self.carrier} - {self.name}"


class ShippingRate(MonetaryMixin, AbstractBaseModel):
    """
    Stores the shipping cost for a specific method, based on weight, country, and region.
    Each ShippingMethod can have multiple rates depending on these factors.

    Fields:
        - shipping_method: A foreign key linking the rate to a specific ShippingMethod.
        - country: Optional field specifying the country this rate applies to. Blank means global rates.
        - region: Optional field for specifying a region within a country (e.g., "California").
        - city: Optional field for more localized rates within a city (e.g., "San Francisco").
        - weight_min: Minimum weight (in kilograms) for the rate to be applicable.
        - weight_max: Maximum weight (in kilograms) for the rate to be applicable.
        - rate: The base shipping cost for packages that meet the weight and location criteria.
        - incremental_rate: Additional cost per kilogram beyond the base weight.
        - currency: The currency in which the rate is expressed (linked to the Currency model).

    Examples:
        - DHL Express Shipping for packages between 0kg and 5kg in the US costs $25.00.
        - FedEx Standard Shipping for packages between 5kg and 10kg globally costs $30.00.
    """
    money_validator_map = {
        "rate": {
            "currency_field": "currency",
            "type": MoneyFieldTypes.UNIT,
            "require_base_currency": True,
        },
        "incremental_rate": {
            "currency_field": "currency",
            "type": MoneyFieldTypes.UNIT,
            "require_base_currency": True,
        },
    }
    shipping_method = models.ForeignKey(
        ShippingMethod, 
        on_delete=models.CASCADE, 
        related_name="rates",
        help_text="The shipping method this rate applies to."
    )
    country = CountryField(
        blank=True, 
        null=True, 
        help_text="If blank, the rate applies globally."
    )
    region = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        help_text="Region within the country, e.g., 'California'. If blank, applies nationwide."
    )
    city = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        help_text="Specific city within the region, e.g., 'San Francisco'."
    )
    weight_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Minimum weight (in kg) for this rate."
    )
    weight_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Maximum weight (in kg) for this rate."
    )
    rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Base shipping cost for this rate."
    )
    incremental_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        help_text="Additional cost per kg beyond the base weight."
    )
    currency = models.CharField(
        max_length=3,
        default=CurrencyTypes.USD,
        choices=CurrencyTypes.choices,
        help_text="Currency in which the rate is expressed."
    )

    class Meta:
        verbose_name = "Shipping Rate"
        verbose_name_plural = "Shipping Rates"

    def save(self, *args, **kwargs):
        """
        Override the save method to ensure that weight_min is always less than weight_max.
        """
        if self.weight_min >= self.weight_max:
            raise ValueError("weight_min must be less than weight_max.")
        self.validate_amount()
        
        self.currency = settings.BASE_CURRENCY
        
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a human-readable representation of the ShippingRate instance.
        Example: "FedEx - Standard Shipping - US (California, San Francisco) (0kg to 5kg)"
        """
        location_parts = [self.city, self.region]
        if self.country:
            location_parts.append(self.country.name)
        location = ", ".join(filter(None, location_parts)) or "Global"
        return f"{self.shipping_method} - {location} ({self.weight_min}kg to {self.weight_max}kg)"


# ==================================================================
# Translation Models
# ==================================================================

class ShippingMethodTranslation(AbstractTranslationModel):
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE, related_name='translations')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    carrier = models.CharField(max_length=200)

    class Meta:
        unique_together = ('language_code', 'shipping_method')
        verbose_name = "Shipping Method Translation"
        verbose_name_plural = "Shipping Method Translations"

    def __str__(self):
        return f"{self.shipping_method} ({self.language_code})"

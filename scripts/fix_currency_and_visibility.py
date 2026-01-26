import os
import sys
import django
from django.utils import timezone
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nxtbn.settings")
django.setup()

from nxtbn.core.models import CurrencyExchange, CurrencyTypes, PublishableStatus
from nxtbn.product.models import Product, ProductVariant

def fix_visibility():
    print("Fixing product visibility...")
    products = Product.objects.all()
    count = 0
    for product in products:
        changed = False
        if not product.is_live:
            product.is_live = True
            changed = True
        if product.status != PublishableStatus.PUBLISHED:
            product.status = PublishableStatus.PUBLISHED
            changed = True
        if not product.published_date:
            product.published_date = timezone.now()
            changed = True
        
        if changed:
            product.save()
            count += 1
            print(f"Published product: {product.name}")
    
    print(f"Total products updated: {count}")

def setup_exchange_rates():
    print("Setting up exchange rates for GHS base...")
    
    # Base rates (APPROXIMATE - for robust testing)
    rates = {
        (CurrencyTypes.GHS, CurrencyTypes.USD): Decimal('0.065'),
        (CurrencyTypes.GHS, CurrencyTypes.EUR): Decimal('0.060'),
        (CurrencyTypes.GHS, CurrencyTypes.GBP): Decimal('0.050'),
        (CurrencyTypes.GHS, CurrencyTypes.NGN): Decimal('105.0'),
        (CurrencyTypes.GHS, CurrencyTypes.KES): Decimal('10.5'),
        (CurrencyTypes.GHS, CurrencyTypes.ZAR): Decimal('1.2'),
        (CurrencyTypes.GHS, CurrencyTypes.XOF): Decimal('40.0'),
        (CurrencyTypes.GHS, CurrencyTypes.XAF): Decimal('40.0'),
    }

    # Also add inverses and USD -> GHS just in case
    rates[(CurrencyTypes.USD, CurrencyTypes.GHS)] = Decimal('15.4') # 1 USD = 15.4 GHS

    for (base, target), rate in rates.items():
        obj, created = CurrencyExchange.objects.get_or_create(
            base_currency=base,
            target_currency=target,
            defaults={'exchange_rate': rate}
        )
        if not created:
            obj.exchange_rate = rate
            obj.save()
            print(f"Updated rate: {base} -> {target} = {rate}")
        else:
            print(f"Created rate: {base} -> {target} = {rate}")

if __name__ == "__main__":
    try:
        fix_visibility()
        setup_exchange_rates()
        print("Successfully applied fixes for currency and visibility.")
    except Exception as e:
        print(f"Error: {e}")

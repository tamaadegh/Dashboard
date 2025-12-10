from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List
from django.conf import settings
from nxtbn.core.models import CurrencyExchange
from django.core.cache import caches
from babel.numbers import format_currency


class CurrencyBackend(ABC):
    def __init__(self):
        self.base_currency = settings.BASE_CURRENCY
        self.cache_key_prefix = f"exchange_rate_{self.base_currency}_to"
        self.timeout = 604800 # Cache for 1 week
        self.cache_backend = 'generic'


    def fetch_data(self) -> List[Dict[str, float]]:
        """
        Fetch exchange rate data from a remote API or data source.
        Returns a list of dictionaries, each containing:
        - target_currency: str
        - exchange_rate: float
        """
        pass

    def refresh_rate(self):
        cache = caches[self.cache_backend]

        for fetch_data in self.fetch_data():
            CurrencyExchange.objects.update_or_create(
                base_currency=self.base_currency,
                target_currency=fetch_data['target_currency'],
                defaults={'exchange_rate': fetch_data['exchange_rate']}
            )
            key = f"{self.cache_key_prefix}_{fetch_data['target_currency']}"
            cache.set(key, fetch_data['exchange_rate'], timeout=self.timeout)


    def get_exchange_rate(self, target_currency: str) -> float:
        if target_currency == self.base_currency:
            return 1.0
        
        
        cache = caches[self.cache_backend]
        key = f"{self.cache_key_prefix}_{target_currency}"
        rate = cache.get(key)
        if rate:
            return rate
       
        
        # Fallback to database if not found in cache
        exchange_rate = CurrencyExchange.objects.filter(
            base_currency=self.base_currency,
            target_currency=target_currency
        ).values_list('exchange_rate', flat=True).first()

        if exchange_rate is None:
            raise ValueError(f"Exchange rate not found for {target_currency}")
        
        
        cache.set(key, exchange_rate, timeout=self.timeout)
       
        return exchange_rate



    def to_target_currency(self, target_currency: str, amount: float, locale: str = ''):
        """
        Convert the given amount from the base currency to the target currency,
        considering the currency precision.
        
        Args:
        - target_currency: str
        - amount: float
        
        Returns:
        - float: Amount in the target currency, formatted to the correct precision.
        """
        exchange_rate = self.get_exchange_rate(target_currency)
        converted_amount = Decimal(amount) * exchange_rate
        if locale:
            formatted_amount = format_currency(converted_amount, target_currency, locale=locale, format_type='standard')
        else:
            formatted_amount = converted_amount
    
        return formatted_amount
       
import os
from django.conf import settings
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from money.money import Currency, Money
from babel.numbers import get_currency_precision, format_currency
from money.exceptions import InvalidAmountError
from nxtbn.core.currency.backend import currency_Backend

def make_path(module_path):
    return os.path.join(*module_path.split('.')) + '/'
    


def build_currency_amount(amount: float, currency_code: str, locale: str = ''):
    """
    Formats and validates a currency amount based on the specified currency code.

    Args:
        amount (float): The amount to be formatted.
        currency_code (str): The currency code (e.g., 'USD', 'KWD', 'OMR', 'JPY').
        locale (str): Optional locale to format with the currency symbol.

    Returns:
        str: The formatted currency string.

    Raises:
        ValueError: If the amount is invalid for the specified currency.

    # Example usage:
    print(build_currency_amount(204.170, 'USD'))  # Output: "$ 204.17"
    print(build_currency_amount(204.170, 'KWD'))  # Output: "د.ك 204.170"
    print(build_currency_amount(204.000, 'JPY'))  # Output: "¥ 204" (JPY has 0 decimal places)
    """
    # Ensure the currency is valid
    try:
        currency = Currency(currency_code)
    except ValueError:
        raise ValueError(f"Invalid currency code: {currency_code}")

    # Determine the precision for the currency
    try:
        decimal_places = get_currency_precision(currency_code)
    except KeyError:
        raise ValueError(f"Currency precision not found for: {currency_code}")

    # Round the amount to the correct number of decimal places
    try:
        formatted_amount = Decimal(amount).quantize(Decimal(f'1.{"0" * decimal_places}'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid amount: {amount} for currency '{currency_code}'")

    # Create Money object (optional)
    try:
        money = Money(formatted_amount, currency)
    except InvalidAmountError:
        raise ValueError(f"Invalid amount '{formatted_amount}' for currency '{currency_code}'")

    # Format the currency for output
    if locale:
        formatted_currency = format_currency(money.amount, currency_code, locale=locale)
    else:
        formatted_currency = f"{formatted_amount:.{decimal_places}f}"

    return formatted_currency


def to_currency_subunit(amount: float, currency_code: str) -> int:
    """
    Converts a given amount to subunits (like cents for USD or fils for KWD) based on the currency.

    Args:
        amount (float): The amount to be converted to subunits.
        currency_code (str): The currency code (e.g., 'USD', 'KWD').

    Returns:
        int: The amount in subunits.

    # Example usage:
    print(to_currency_subunit(204.170, 'USD'))  # Output: 20417 (in cents)
    print(to_currency_subunit(204.170, 'KWD'))  # Output: 204170 (in fils)
    print(to_currency_subunit(204.000, 'JPY'))  # Output: 204 (no subunits for JPY)
    """
    # Ensure the currency is valid
    try:
        currency = Currency(currency_code)
    except ValueError:
        raise ValueError(f"Invalid currency code: {currency_code}")

    # Get the correct number of decimal places for the currency (subunit factor)
    try:
        decimal_places = get_currency_precision(currency_code)
    except KeyError:
        raise ValueError(f"Currency precision not found for: {currency_code}")

    # Multiply the amount by 10^decimal_places to convert it into subunits (e.g., 20.45 USD -> 2045 cents)
    try:
        subunit_amount = Decimal(amount) * (10 ** decimal_places)
        subunit_amount = subunit_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)  # Round to the nearest whole number
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid amount: {amount} for currency '{currency_code}'")

    return int(subunit_amount)


def to_currency_unit(subunit: int, currency_code: str, locale: str = ''):
    """
    Converts a given amount in subunits (e.g., cents for USD, fils for KWD) to a formatted currency string 
    based on the specified currency code and optional locale.

    Args:
        subunit (int): The amount in subunits to be converted (e.g., 2045 for 2045 cents).
        currency_code (str): The currency code (e.g., 'USD', 'KWD', 'JPY') for which the conversion is done.
        locale (str, optional): A locale string for formatting the currency output (default is an empty string).

    Returns:
        str: The formatted currency string representation of the amount in units.

    Raises:
        ValueError: If the currency code is invalid or the subunit amount is invalid for the specified currency.

    Example usage:
        print(to_currency_unit(2045, 'USD'))  # Output: "$ 20.45"
        print(to_currency_unit(204170, 'KWD', locale='en_KW'))  # Output: "د.ك 204.170"
        print(to_currency_unit(20456, 'JPY'))  # Output: "¥ 20456"  # JPY has no decimal places
    """
   
    # Ensure the currency is valid
    try:
        currency = Currency(currency_code)
    except ValueError:
        raise ValueError(f"Invalid currency code: {currency_code}")
    
    try:
        decimal_places = get_currency_precision(currency_code)
    except KeyError:
        raise ValueError(f"Currency precision not found for: {currency_code}")
    
    # Divide the subunit amount by 10^decimal_places to convert it into units (e.g., 2045 cents -> 20.45 USD)
    try:
        unit_amount = Decimal(subunit) / (10 ** decimal_places)
        unit_amount = unit_amount.quantize(Decimal(f'1.{"0" * decimal_places}'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid subunit amount: {subunit} for currency '{currency_code}'")
    
    # Format the currency for output
    if locale:
        formatted_currency = format_currency(unit_amount, currency_code, locale=locale)
    else:
        formatted_currency = f"{unit_amount}"

    return formatted_currency



def normalize_amount_currencywise(amount: float, currency_code: str) -> Decimal:
    """    
    Warning:
    This method rounds the amount to the nearest precision defined by the currency,
    which may lead to minor value reductions. It is primarily intended for generating
    test data, management commands, or sanitizing payloads in serializers.
    
    If used outside of test case/unit testing and test data generation, 
    it should be based on merchant requirements.
    
    Parameters:
    - amount (float): The monetary amount to be formatted.
    - currency_code (str): The ISO 4217 currency code (e.g., 'USD', 'JPY', 'KWD').

    Returns:
    - Decimal: The formatted amount with the appropriate precision.
    """
    precision = get_currency_precision(currency_code)
    amount_decimal = Decimal(str(amount))
    quantize_format = '1.' + '0' * precision
    formatted_amount = amount_decimal.quantize(Decimal(quantize_format), rounding=ROUND_HALF_UP)
    
    return formatted_amount


def get_in_user_currency(amount: float, user_currency: str, base_currency: str, locale: str = '') -> str:
    """
    Converts base currency amount to user currency amount through middleware delivered currency code
    """
    if not settings.IS_MULTI_CURRENCY:
        return build_currency_amount(amount, base_currency, locale)
    
    if user_currency == base_currency:
        return build_currency_amount(amount, base_currency, locale)

    cleaned_amount = build_currency_amount(amount, base_currency)
    backend = currency_Backend()
    return backend.to_target_currency(user_currency, cleaned_amount, locale)




def apply_exchange_rate(amount: str, exchange_rate: str, target_currency: str, locale: str = '') -> str:
    """
    Converts the given amount from the base currency to the target currency using the exchange rate.

    Args:
        amount (float): The amount to be converted.
        exchange_rate (float): The exchange rate from the base currency to the target currency.
        target_currency (str): The currency code of the target currency.
        locale (str, optional): The locale string for formatting the currency output (default is an empty string).

    Returns:
        str: The formatted currency string representation of the converted amount.
    """
    # Perform the conversion without formatting
    try:
        # Ensure amount is a Decimal for precision
        amount_decimal = Decimal(amount)
        converted_amount = amount_decimal * Decimal(exchange_rate)
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid amount '{amount}' or exchange rate '{exchange_rate}'")

    # Format the converted amount for output
    if locale:
        formatted_currency = format_currency(converted_amount, target_currency, locale=locale)
    else:
        # Return unformatted converted amount with the correct precision
        decimal_places = get_currency_precision(target_currency)
        formatted_currency = f"{converted_amount:.{decimal_places}f}"

    return formatted_currency
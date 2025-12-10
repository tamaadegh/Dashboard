import re

from typing import List
from rest_framework import serializers
from django.core.exceptions import ValidationError

def parse_user_agent(request):
    # Extract IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    # Extract user agent
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')

    # Determine device type
    if 'Mobile' in user_agent_string:
        device_type = 'Mobile'
    elif 'Tablet' in user_agent_string:
        device_type = 'Tablet'
    else:
        device_type = 'PC'

    # Determine browser and version
    browser, version = 'Unknown', ''
    browser_patterns = [
        (r'Chrome/(\d+\.\d+)', 'Chrome'),
        (r'Firefox/(\d+\.\d+)', 'Firefox'),
        (r'Safari/(\d+\.\d+)', 'Safari'),
        (r'OPR/(\d+\.\d+)', 'Opera'),
        (r'Edge/(\d+\.\d+)', 'Edge'),
        (r'MSIE (\d+\.\d+)', 'Internet Explorer'),
        (r'Trident/.*rv:(\d+\.\d+)', 'Internet Explorer'),
    ]

    for pattern, name in browser_patterns:
        match = re.search(pattern, user_agent_string)
        if match:
            browser = name
            version = match.group(1)
            break

    # Determine operating system
    if 'Windows' in user_agent_string:
        operating_system = 'Windows'
    elif 'Mac OS' in user_agent_string:
        operating_system = 'Mac OS'
    elif 'Linux' in user_agent_string:
        operating_system = 'Linux'
    elif 'Android' in user_agent_string:
        operating_system = 'Android'
    elif 'iPhone' in user_agent_string or 'iPad' in user_agent_string:
        operating_system = 'iOS'
    else:
        operating_system = 'Unknown'

    # Return collected metadata as a dictionary
    return {
        'ip_address': ip_address,
        'user_agent': user_agent_string,
        'device_type': device_type,
        'browser': browser,
        'browser_version': version,
        'operating_system': operating_system,
    }




def validate_variant_with_stocks(variants_payload: List[dict]):
    stock_errors = []
    for item in variants_payload:
        variant = item['variant']
        quantity = item['quantity']

        if variant.track_inventory and not variant.allow_backorder:
            if variant.track_inventory and not variant.allow_backorder and variant.get_valid_stock() < quantity:
                product_name = variant.product.name
                # Determine inventory name: prefer variant.name, fallback to sku
                inventory_name = variant.name if variant.name else variant.sku
                stock_errors.append(
                    f"Product '{product_name}' with inventory '{inventory_name}' does not have sufficient stock for the requested quantity."
                )
    if stock_errors:
        # Combine all stock error messages into one response
        raise serializers.ValidationError(stock_errors)

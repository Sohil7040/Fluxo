import requests
import json
from decimal import Decimal

def convert_currency(amount, from_currency, to_currency):
    """
    Convert currency using a free API (exchangerate-api.com)
    In production, you might want to use a more reliable service
    """
    if from_currency == to_currency:
        return Decimal(str(amount))
    
    try:
        # Using exchangerate-api.com (free tier)
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        rate = data['rates'].get(to_currency)
        
        if rate is None:
            raise ValueError(f"Currency {to_currency} not found")
        
        converted_amount = Decimal(str(amount)) * Decimal(str(rate))
        return converted_amount.quantize(Decimal('0.01'))
        
    except requests.RequestException as e:
        # Fallback: return original amount with a warning
        print(f"Currency conversion failed: {e}")
        return Decimal(str(amount))
    except Exception as e:
        print(f"Currency conversion error: {e}")
        return Decimal(str(amount))

def get_exchange_rate(from_currency, to_currency):
    """
    Get exchange rate between two currencies
    """
    if from_currency == to_currency:
        return 1.0
    
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data['rates'].get(to_currency, 1.0)
        
    except Exception as e:
        print(f"Failed to get exchange rate: {e}")
        return 1.0
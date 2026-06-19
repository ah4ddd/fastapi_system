import httpx
from ..config import settings
from typing import Dict


COINGECKO_API_KEY = settings.coingecko_api_key
BASE_URL = "https://api.coingecko.com/api/v3"


async def fetch_crypto_prices(coin_ids: list[str]) -> Dict | None:
    """
    Fetch current prices for multiple cryptocurrencies.

    Args:
        coin_ids: List of CoinGecko IDs (e.g., ['bitcoin', 'ethereum', 'solana'])

    Returns:
        Dict with price data or None if request fails.

    Example response:
    {
        "bitcoin": {"usd": 67234.5, "usd_24h_change": 2.3},
        "ethereum": {"usd": 3456.78, "usd_24h_change": -1.2}
    }
    """

    # Join coin IDs into comma-separated string
    # CoinGecko wants comma-separated string in URL parameter
    # ex - ?ids=bitcoin,ethereum,solana
    ids_param = ",".join(coin_ids)

    url = f"{BASE_URL}/simple/price"

    #  CoinGecko's auth header
    headers = {
        "x-cg-demo-api-key": COINGECKO_API_KEY,
        "Accept": "application/json" # tells server you want JSON response
    }

    params = {
        "ids": ids_param, # which coins to fetch
        "vs_currencies": "usd", # which fiat currency (usd, eur, inr)
        "include_24hr_change": "true" # add 24h percentage change
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=15.0)

            # Log remaining calls (CoinGecko doesn't expose this in free tier, but good practice)
            print(f"CoinGecko API status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 429:
                print("Rate limit exceeded")
                return None
            else:
                print(f"API Error: {response.status_code}")
                return None

        except httpx.TimeoutException:
            print("Request timeout")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None


def transform_price_data(raw_data: Dict | None) -> list[Dict]:
    """
    Transform CoinGecko response into clean format.

    Input:
    {
        "bitcoin": {"usd": 67234.5, "usd_24h_change": 2.3},
        "ethereum": {"usd": 3456.78, "usd_24h_change": -1.2}
    }

    Output:
    [
        {"symbol": "bitcoin", "price": 67234.5, "change_24h": 2.3},
        {"symbol": "ethereum", "price": 3456.78, "change_24h": -1.2}
    ]
    """
    if not raw_data:
        return []

    transformed = []

    # loop through dictionary key-value pairs
    for symbol, data in raw_data.items():
        transformed.append({
            "symbol": symbol,
            # get value, default to 0 if missing (defensive programming)
            "price_usd": data.get("usd", 0),
            "change_24h": data.get("usd_24h_change", 0)
        })

    return transformed

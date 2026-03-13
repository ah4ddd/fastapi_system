# This file is a service layer / utility module #
"""
Its only job is to:
    Call the OpenWeather API
    Parse the response
    Return the result as a Python dictionary
Nothing more. Nothing less.
"""

import httpx # async HTTP client
import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# asynchronous function, take a city name as string, return either dict/none
async def fetch_weather(city: str) -> dict | None:
    """
    Fetch weather data from OpenWeather API for a given city.

    Returns dict with weather data or None if request fails.
    """
    # Request parameters, these become URL query parameters
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"  # Celsius instead of Kelvin
    }
    # create HTTP client, make the Request
    async with httpx.AsyncClient() as client:
        try: # send GET request, wait for response (wait max 10 seconds)
            response = await client.get(BASE_URL, params=params, timeout=10.0)
            # Handling Response
            if response.status_code == 200:
                return response.json() # parse JSON response into Python dict
            else: # Anything else (404, 500, etc.) = return None
                print(f"API Error: {response.status_code}")
                return None
        # Error Handling No crash (app should survive external API failures)
        except httpx.TimeoutException:
            print("Request timeout")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

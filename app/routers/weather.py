from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db # type:ignore
from app.models import WeatherResponse # type:ignore
from app.db_models import WeatherDB # type:ignore
from app.services.openweather import fetch_weather # type:ignore
from datetime import datetime, timezone
from typing import Annotated

# prefix="/weather" = all routes start with /weather
# So @router.get("/{city}") becomes /weather/{city}
router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/{city}", response_model=WeatherResponse)
async def get_weather(city: str, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Fetch current weather for a city.

    - Call OpenWeather API
    - Store result in database
    - Return clean response
    """

    # Fetch from external API
    weather_data = await fetch_weather(city)

    if not weather_data:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch weather for {city}"
        )

    # Extract relevant data
    temp = weather_data["main"]["temp"]
    description = weather_data["weather"][0]["description"]
    humidity = weather_data["main"]["humidity"]
    # UTC — Coordinated Universal Time
    timestamp = datetime.now(timezone.utc)

    # Store in database
    db_weather = WeatherDB(
        city=city,
        temperature=temp,
        description=description,
        humidity=humidity,
        timestamp=timestamp
    )

    db.add(db_weather)
    await db.commit()

    # Return clean response
    return WeatherResponse(
        city=city,
        temperature=temp,
        description=description,
        humidity=humidity,
        timestamp=timestamp
    )

"""
FastAPI Router
      ↓
Weather Service (OpenWeather API call)
      ↓
Parsed JSON
      ↓
SQLAlchemy ORM model
      ↓
INSERT INTO weather_data
      ↓
PostgreSQL commit
      ↓
JSON response back to client
"""

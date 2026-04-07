from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db # type: ignore
from app.models import CryptoPricesResponse, CryptoPrice, CryptoHistory # type: ignore
from app.db_models import CryptoPriceDB # type: ignore
from app.services.coingecko import fetch_crypto_prices, transform_price_data # type: ignore
from app.auth import get_current_user # type: ignore
from datetime import datetime
from typing import List

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.get("/prices", response_model=CryptoPricesResponse)
async def get_crypto_prices(db: AsyncSession = Depends(get_db)):
    """
    Fetch current prices for Bitcoin, Ethereum, and Solana.

    - Fetches from CoinGecko API
    - Stores in database for historical tracking
    - Returns current prices with 24h change
    """

    # Coins to track
    coin_ids = ["bitcoin", "ethereum", "solana"]

    # Fetch from CoinGecko
    raw_data = await fetch_crypto_prices(coin_ids)

    if not raw_data:
        raise HTTPException(
            status_code=503,
            detail="Could not fetch crypto prices. API may be down or rate limited."
        )

    # Transform data
    prices = transform_price_data(raw_data)

    # Current timestamp
    timestamp = datetime.utcnow().isoformat()

    # Store in database
    # One commit for all 3 coins. Efficient.
    for price in prices:
        db_price = CryptoPriceDB(
            symbol=price["symbol"],
            price_usd=price["price_usd"],
            change_24h=price["change_24h"],
            timestamp=timestamp
        )
        db.add(db_price)

    await db.commit()

    # Build response
    # create objects, not modifie data
    # It runs once per coin → builds a list
    # API → currently static, not dynamic
    price_models = [CryptoPrice(**price) for price in prices]

    return CryptoPricesResponse(
        prices=price_models,
        timestamp=timestamp
    )

# This endpoint reads from database, not CoinGecko.
@router.get("/history/{symbol}", response_model=List[CryptoHistory])
async def get_price_history(symbol: str, db: AsyncSession = Depends(get_db)):
    """
    Get historical price data for a cryptocurrency from database.

    Returns last 100 price records for the given symbol.
    """

    # Query database
    query = (
        # get me data AND map each row into a CryptoPriceDB object
        select(CryptoPriceDB) # “SELECT * FROM crypto_prices
        .where(CryptoPriceDB.symbol == symbol) # WHERE symbol = 'bitcoin'
        .order_by(CryptoPriceDB.timestamp.desc()) # ORDER BY timestamp DESC
        .limit(100) # LIMIT 100 (only latest 100)
    )

    # wrapper object (send query to DB)
    # DB runs the query
    # Rows are fetched
    result = await db.execute(query)

    # DB → gives tuples (raw rows)
    # SQLAlchemy → converts → CryptoPriceDB objects
    # .scalars().all() → gives → list of objects
    # records is now a list of CryptoPriceDB objects.
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No price history found for {symbol}"
        )

    # Convert to response models (list comprehension)
    history = [
        CryptoHistory(
            symbol=record.symbol,
            price_usd=record.price_usd,
            change_24h=record.change_24h,
            timestamp=record.timestamp
        )
        for record in records
    ]

    return history

@router.get("/my-history", response_model=List[CryptoHistory])
# Before running this function, run get_current_user
# Depends() runs a function before route and injects its result.
async def get_my_crypto_history(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)):
    """
    Get fetched crypto prices.

    PROTECTED: Requires login.

    (For now, returns all data. Later, filter by user.)
    """

    query = (
        select(CryptoPriceDB)
        .order_by(CryptoPriceDB.timestamp.desc())
        .limit(50)
    )

    result = await db.execute(query)
    records = result.scalars().all()

    if not records:
        return []

    history = [
        CryptoHistory(
            symbol=record.symbol,
            price_usd=record.price_usd,
            change_24h=record.change_24h,
            timestamp=record.timestamp
        )
        for record in records
    ]

    return history

"""
HTTP Request → /history/BTC
        ↓
symbol = "BTC"
        ↓
Build Query (no execution yet)
        ↓
DB EXECUTES QUERY
    (loop over rows, filter, sort, limit)
        ↓
Raw rows returned (tuples)
        ↓
SQLAlchemy maps rows → CryptoPriceDB objects
    (loop happens internally)
        ↓
.scalars() unwraps tuples
        ↓
.all() converts to list
        ↓
records = [CryptoPriceDB, CryptoPriceDB, ...]
        ↓
YOUR LOOP runs
    for record in records:
        create CryptoHistory
        append to list
        ↓
history = [CryptoHistory, CryptoHistory, ...]
        ↓
return history → JSON
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

# What the CLIENT sends (input)
class ItemCreate(BaseModel):
    name: str = Field(min_length=3)
    price: float = Field(gt=0)
    description: str | None = Field(default=None, max_length=200)
    stock_quantity: int = Field(default=0, ge=0) # NEW (ge=0 means >= 0)

# What lives in DATABASE (internal)
class ItemInDB(ItemCreate):
    id: int
    cost_price: float
    supplier_secret: str

# What the CLIENT receives (output)
class ItemInPublic(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None

# Wrapper for POST response
class CreateItemResponse(BaseModel):
    item: ItemInPublic
    message: str


# --For Weather--
class WeatherResponse(BaseModel):
    city: str
    temperature: float
    description: str
    humidity: int
    timestamp: datetime


# --For GitHub API--
class GitHubRepo(BaseModel):
    """Single repository data"""
    name: str
    description: str | None = None
    stars: int
    language: str
    url: str
    updated_at: str

class GitHubReposResponse(BaseModel):
    """Response containing user's top repos"""
    username: str
    total_repos: int
    top_repos: List[GitHubRepo]
    fetched_at: str


# --For Crypto--
class CryptoPrice(BaseModel):
    """Single crypto price data"""
    symbol: str
    price_usd: float
    change_24h: float

class CryptoPricesResponse(BaseModel):
    """Response containing multiple crypto prices"""
    prices: List[CryptoPrice]
    timestamp: str

class CryptoHistory(BaseModel):
    """Historical price record"""
    symbol: str
    price_usd: float
    change_24h: float
    timestamp: str


# --For User--
class UserSignup(BaseModel):
    """User signup request"""
    email: str
    password: str

class UserLogin(BaseModel):
    """User login request"""
    email: str
    password: str

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    """User info (never include password)"""
    id: int
    email: str
    created_at: str

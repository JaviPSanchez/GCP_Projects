from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import datetime

class QuoteUSD(BaseModel):
    price: float
    volume_24h: float
    volume_change_24h: float
    percent_change_1h: float
    percent_change_24h: float
    percent_change_7d: float
    percent_change_30d: float
    percent_change_60d: float
    percent_change_90d: float
    market_cap: float
    market_cap_dominance: float
    fully_diluted_market_cap: Optional[float]
    tvl: Optional[float]
    
class Platform(BaseModel):
    id: Optional[int]
    name: Optional[str]
    symbol: Optional[str]
    slug: Optional[str]
    token_address: Optional[str]

class DataItem(BaseModel):
    id: int
    name: str
    symbol: str
    slug: str
    num_market_pairs: int
    date_added: Optional[datetime]
    tags: List[str]
    max_supply: Optional[float]
    circulating_supply: float
    total_supply: float
    infinite_supply: bool
    platform: Optional[Platform]
    cmc_rank: int
    self_reported_circulating_supply: Optional[float]
    self_reported_market_cap: Optional[float]
    tvl_ratio: Optional[float]
    last_updated: Optional[datetime]
    quote: Dict[str, QuoteUSD]

class Status(BaseModel):
    timestamp: datetime

class Record(BaseModel):
    status: Status
    data: List[DataItem]

    @field_validator('status')
    def check_status(cls, v):
        if not v.timestamp:
            raise ValueError('Timestamp must not be empty')
        return v

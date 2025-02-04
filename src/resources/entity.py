import datetime
from dataclasses import dataclass

@dataclass
class Player:
    id: int
    summoner_name: str
    display_name: str
    region: str
    server: str
    join_date: datetime
    is_processed: bool
    processed_date: datetime
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

@dataclass
class PlayerDataRes:
    puuid: str
    game_name: str
    tag_line: str

    @classmethod
    def from_res(cls, data: dict):
        return cls(
            puuid=data.get("puuid", ""),
            game_name=data.get("gameName", ""),
            tag_line=data.get("tagLine", "")
        )
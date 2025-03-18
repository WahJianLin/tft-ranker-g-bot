import datetime
from dataclasses import dataclass

from src.resources.constants import PlayerStatusEnum


@dataclass
class Player:
    id: int
    summoner_name: str
    display_name: str
    region: str
    riot_server: str
    join_date: datetime
    processed_date: datetime
    is_streamer: bool
    player_status: PlayerStatusEnum
    discord_id: int


@dataclass
class PlayerRiotData:
    id: int
    player_id: int
    summoner_id: str


@dataclass
class CompetitorV:
    summoner_name: str
    display_name: str
    riot_server: str
    player_status: PlayerStatusEnum
    summoner_id: str


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


@dataclass
class LeaderboardEntry:
    summoner_name: str
    tft_rank_title: str
    tft_rank_value: int
    display_name: str

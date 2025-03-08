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

    @classmethod
    def from_tuple(cls, data: tuple):
        return cls(
            id=data[0],
            summoner_name=data[1],
            display_name=data[2],
            region=data[3],
            riot_server=data[4],
            join_date=data[5],
            processed_date=data[6],
            is_streamer=data[7],
            player_status=data[8]
        )

@dataclass
class PlayerRiotData:
    id: int
    player_id: int
    summoner_id: str

    @classmethod
    def from_tuple(cls, data: tuple):
        return cls(
            id=data[0],
            player_id=data[1],
            summoner_id=data[2]
        )

@dataclass
class Competitor:
    id: int
    summoner_name: str
    summoner_id: str
    display_name: str
    riot_server: str
    is_competing: bool
    player_fkey: int

    @classmethod
    def from_tuple(cls, data: tuple):
        return cls(
            id=data[0],
            summoner_name=data[1],
            summoner_id=data[2],
            display_name=data[3],
            riot_server=data[4],
            is_competing=data[5],
            player_fkey=data[6]
        )


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

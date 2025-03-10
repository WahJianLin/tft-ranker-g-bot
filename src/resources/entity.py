import datetime
from dataclasses import dataclass

from src.resources.constants import PlayerStatusEnum


@dataclass
class Player:
    id: int | None
    summoner_name: str
    display_name: str
    region: str
    riot_server: str
    join_date: datetime
    processed_date: datetime
    is_streamer: bool
    player_status: PlayerStatusEnum

    @classmethod
    def constructor(
            cls,
            id_param: int | None,
            summoner_name_param: str,
            display_name_param: str,
            region_param: str,
            riot_server_param: str,
            join_date_param: str,
            processed_date_param: str,
            is_streamer_param: bool,
            player_status_param: PlayerStatusEnum
    ):
        return cls(
            id=id_param,
            summoner_name=summoner_name_param,
            display_name=display_name_param,
            region=region_param,
            riot_server=riot_server_param,
            join_date=join_date_param,
            processed_date=processed_date_param,
            is_streamer=is_streamer_param,
            player_status=player_status_param
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

    @classmethod
    def constructor(
            cls,
            id_param: int | None,
            player_id_param: int,
            summoner_id_param: str,

    ):
        return cls(
            id=id_param,
            player_id=player_id_param,
            summoner_id=summoner_id_param,
        )


@dataclass
class CompetitorV:
    summoner_name: str
    display_name: str
    riot_server: str
    player_status: PlayerStatusEnum
    summoner_id: str

    @classmethod
    def constructor(cls, summoner_name_param: str, display_name_param: str, riot_server_param: str,
                    player_status_param: PlayerStatusEnum, summoner_id_param: str):
        return cls(
            summoner_name=summoner_name_param,
            display_name=display_name_param,
            riot_server=riot_server_param,
            player_status=player_status_param,
            summoner_id=summoner_id_param
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
    @classmethod
    def constructor(cls, puuid_param: str, game_name_param: str, tag_line_param: str,
                    ):
        return cls(
            puuid=puuid_param,
            game_name=game_name_param,
            tag_line=tag_line_param,
        )


@dataclass
class LeaderboardEntry:
    summoner_name: str
    tft_rank_title: str
    tft_rank_value: int
    display_name: str

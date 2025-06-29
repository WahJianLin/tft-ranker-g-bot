import logging
import os
from typing import Final

import requests
from dotenv import load_dotenv
from requests import Response

from src.actions.database import get_competitors_by_status
from src.resources.constants import QUEUE_TYPE, RANKED_QUEUE_TYPE, TIER, RANK, \
    LEAGUE_POINTS, RiotTiersEnum, RiotRanksEnum, TierToTitleEnum
from src.resources.entity import PlayerDataRes, LeaderboardEntry, CompetitorV
from src.resources.logging_constants import RIOT_FAIL, RIOT_ERROR_CODE, RIOT_SUCCESS, RIOT_CALL, \
    RIOT_CALL_GET_RANK_DATA, RIOT_CALL_GET_SUMMONER_ID, RIOT_CALL_GET_PLAYER_DATA_CALL

load_dotenv()

RIOT_API_KEY: Final[str] = os.getenv('RIOT_API_KEY')

GET_ACCOUNT_DATA_URL: str = 'https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}'

GET_RANK_DATA_URL: str = 'https://{}.api.riotgames.com/tft/league/v1/entries/by-summoner/{}?api_key={}'

GET_RANK_DATA_BY_PUUID_URL: str = 'https://{}.api.riotgames.com/tft/league/v1/by-puuid/{}?api_key={}'

GET_SUMMONER_DATA_URL: str = 'https://{}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{}?api_key={}'


def riot_get_player_data_call(summoner_name: str, region: str) -> PlayerDataRes or None:
    split_name: list[str] = summoner_name.split('#')
    game_name: str = split_name[0]
    tag_line: str = split_name[1]
    url: str = GET_ACCOUNT_DATA_URL.format(region, game_name, tag_line, RIOT_API_KEY)
    try:
        logging.info(RIOT_CALL.format(RIOT_CALL_GET_PLAYER_DATA_CALL))
        response: Response = requests.get(url)

        if response.status_code == 200:
            body: dict = response.json()
            logging.info(RIOT_SUCCESS)
            return PlayerDataRes.from_res(body)
        else:
            logging.error(RIOT_FAIL)
            logging.info(RIOT_ERROR_CODE.format(response.status_code))
            return None
    except requests.exceptions.RequestException as e:
        logging.info(RIOT_FAIL)
        logging.exception(e)
        return None


# deprecated
def riot_get_summoner_id_call(puuid: str, server: str) -> str | None:
    url = GET_SUMMONER_DATA_URL.format(server, puuid, RIOT_API_KEY)
    try:
        logging.info(RIOT_CALL.format(RIOT_CALL_GET_SUMMONER_ID))
        response: Response = requests.get(url)

        if response.status_code == 200:
            body: dict = response.json()
            logging.info(RIOT_SUCCESS)
            return body['id']
        else:
            logging.error(RIOT_FAIL)
            logging.info(RIOT_ERROR_CODE.format(response.status_code))
            return None
    except requests.exceptions.RequestException as e:
        logging.info(RIOT_FAIL)
        logging.exception(e)
        return None


def riot_get_rank_data(competitor: CompetitorV) -> LeaderboardEntry | None:
    url = GET_RANK_DATA_BY_PUUID_URL.format(competitor.riot_server, competitor.puuid, RIOT_API_KEY)
    try:
        logging.info(RIOT_CALL.format(RIOT_CALL_GET_RANK_DATA))
        response: Response = requests.get(url)
        if response.status_code == 200:
            body: dict = response.json()
            body_len: int = len(body)
            if body_len > 0:
                rank_data: dict = {}
                # checks to see if players have played normal tft ranked
                while not rank_data and body_len > 0:
                    if body[body_len - 1][QUEUE_TYPE] == RANKED_QUEUE_TYPE:
                        rank_data = body[body_len - 1]
                    body_len -= 1
                if len(rank_data) == 0:
                    return None
                tier: str = rank_data[TIER]  # gets metal rank like iron or bronze
                rank: str = rank_data[RANK]  # gets rank subdivision
                points: int = rank_data[LEAGUE_POINTS]  # gets lp value

                tft_rank_title: str = f'{TierToTitleEnum[tier].value} {rank} {points} LP'
                tft_rank_value: int = RiotTiersEnum[tier].value + RiotRanksEnum[rank].value + points

                logging.info(RIOT_SUCCESS)
                return LeaderboardEntry(competitor.summoner_name, tft_rank_title, tft_rank_value,
                                        competitor.display_name)
            logging.info(RIOT_SUCCESS)
            return None
        else:
            logging.error(RIOT_FAIL)
            logging.info(RIOT_ERROR_CODE.format(response.status_code))
            print('Error get_rank_data:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        logging.info(RIOT_FAIL)
        logging.exception(e)
        return None


def riot_get_ranks() -> list[LeaderboardEntry]:
    leaderboard_entries: list[LeaderboardEntry] = []
    valid_competitors: list[CompetitorV] = get_competitors_by_status()

    for competitor in valid_competitors:
        leaderboard_entry: LeaderboardEntry = riot_get_rank_data(competitor)
        if leaderboard_entry:
            leaderboard_entries.append(leaderboard_entry)

    return leaderboard_entries


# method should not be used often. returns riot table id and puuid.
# input missing_list -> riot table id, summoner_name, region
def riot_get_missing_puuid(missing_list: list[tuple[int, str, str]]) -> list[tuple[int, str]]:
    puuid_list: list[tuple[int, str]] = []
    for entry in missing_list:
        player_data: PlayerDataRes = riot_get_player_data_call(entry[1], entry[2])
        puuid_list.append((entry[0], player_data.puuid))
    return puuid_list

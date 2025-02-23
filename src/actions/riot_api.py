import logging
import os
from typing import Final

import requests
from dotenv import load_dotenv
from requests import Response

from src.actions.database import get_valid_competitor
from src.resources.constants import QUEUE_TYPE, RANKED_QUEUE_TYPE, TIER, RANK, \
    LEAGUE_POINTS, RiotTiersEnum, RiotRanksEnum
from src.resources.entity import PlayerDataRes, LeaderboardEntry, Competitor
from src.resources.logging_constants import RIOT_FAIL, RIOT_ERROR_CODE, RIOT_SUCCESS, RIOT_CALL, \
    RIOT_CALL_GET_RANK_DATA, RIOT_CALL_GET_SUMMONER_ID, RIOT_CALL_GET_PLAYER_DATA_CALL

load_dotenv()

RIOT_API_KEY: Final[str] = os.getenv('RIOT_API_KEY')

GET_ACCOUNT_DATA_URL: str = 'https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}'

GET_RANK_DATA_URL: str = 'https://{}.api.riotgames.com/tft/league/v1/entries/by-summoner/{}?api_key={}'

GET_SUMMONER_DATA_URL: str = 'https://{}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{}?api_key={}'


def get_player_data_call(summoner_name: str, region: str) -> PlayerDataRes or None:
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


def get_summoner_id_call(puuid: str, server: str) -> str | None:
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


def get_rank_data(competitor: Competitor) -> LeaderboardEntry | None:
    url = GET_RANK_DATA_URL.format(competitor.riot_server, competitor.summoner_id, RIOT_API_KEY)
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
                tier: str = rank_data[TIER]  # gets metal rank like iron or bronze
                rank: str = rank_data[RANK]  # gets rank subdivision
                points: int = rank_data[LEAGUE_POINTS]  # gets lp value

                tft_rank_title: str = f'{tier} {rank} {points} LP'
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


def get_ranks() -> list[LeaderboardEntry]:
    leaderboard_entries: list[LeaderboardEntry] = []
    valid_competitors: list[tuple[Competitor, ...]] = get_valid_competitor()

    for entry in valid_competitors:
        competitor: Competitor = Competitor.from_tuple(entry)
        leaderboard_entry: LeaderboardEntry = get_rank_data(competitor)
        if leaderboard_entry:
            leaderboard_entries.append(leaderboard_entry)

    return leaderboard_entries

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

load_dotenv()

RIOT_API_KEY: Final[str] = os.getenv('RIOT_API_KEY')

GET_ACCOUNT_DATA_URL = 'https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}'

GET_RANK_DATA_URL = 'https://{}.api.riotgames.com/tft/league/v1/entries/by-summoner/{}?api_key={}'

GET_SUMMONER_DATA_URL = 'https://{}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{}?api_key={}'


def get_player_data_call(summoner_name: str, region: str) -> PlayerDataRes or None:
    split_name: list[str] = summoner_name.split('#')
    game_name: str = split_name[0]
    tag_line: str = split_name[1]
    url: str = GET_ACCOUNT_DATA_URL.format(region, game_name, tag_line, RIOT_API_KEY)
    print("calling get_player_data_call on", summoner_name, region)
    try:
        response: Response = requests.get(url)

        if response.status_code == 200:
            body: dict = response.json()
            return PlayerDataRes.from_res(body)
        else:
            print('Error api get_player_data_call:', response.status_code, 'Player', game_name, response.content, url)
            return None
    except requests.exceptions.RequestException as e:

        print('Error exception in get_player_data_call:', e)
        return None


def get_summoner_id_call(puuid: str, server: str) -> str | None:
    url = GET_SUMMONER_DATA_URL.format(server, puuid, RIOT_API_KEY)
    try:
        response: Response = requests.get(url)

        if response.status_code == 200:
            body: dict = response.json()
            return body['id']
        else:
            print('Error not correct code in get_summoner_id_call:', response.status_code, url)
            return None
    except requests.exceptions.RequestException as e:

        # Handle any network-related errors or exceptions
        print('Error exception in get_summoner_id_call:', e)
        return None

def get_rank_data(competitor: Competitor) -> LeaderboardEntry | None:
    url = GET_RANK_DATA_URL.format(competitor.riot_server, competitor.summoner_id, RIOT_API_KEY)
    try:
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

                return LeaderboardEntry(competitor.summoner_name, tft_rank_title, tft_rank_value,
                                        competitor.display_name)

            return None
        else:
            # logging.error()
            print('Error get_rank_data:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:

        # Handle any network-related errors or exceptions
        print('Error get_rank_data:', e)
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

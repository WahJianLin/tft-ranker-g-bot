import json
import os
from typing import Final

import requests
from dotenv import load_dotenv

from src.resources.constants import ServerLocationEnum, REGION_MAP, QUEUE_TYPE, RANKED_QUEUE_TYPE, TIER, RANK, \
    LEAGUE_POINTS, RiotTiersEnum, RiotRanksEnum, SUMMONER_NAME, TFT_RANK_VALUE, TFT_RANK_TITLE, DISPLAY_NAME, \
    SUMMONER_NAME_JSON_VAL, SUMMONER_ID_JSON_VAL, SERVER_JSON_VAL, DISPLAY_NAME_JSON_VAL, SERVER_NAME_MAP
from src.resources.entity import PlayerDataRes

load_dotenv()

RIOT_API_KEY: Final[str] = os.getenv('RIOT_API_KEY')

GET_ACCOUNT_DATA_URL = 'https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}'

GET_RANK_DATA_URL = 'https://{}.api.riotgames.com/tft/league/v1/entries/by-summoner/{}?api_key={}'

GET_SUMMONER_DATA_URL = 'https://{}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{}?api_key={}'

total_api_calls: int = 0


def get_player_data_call(summoner_name: str, region: str) -> PlayerDataRes or None:
    split_name = summoner_name.split('#')
    game_name = split_name[0]
    tag_line = split_name[1]
    url = GET_ACCOUNT_DATA_URL.format(region, game_name, tag_line, RIOT_API_KEY)
    print("calling get_player_data_call on", summoner_name, region)
    try:
        response = requests.get(url)

        if response.status_code == 200:
            body = response.json()
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
        response = requests.get(url)

        if response.status_code == 200:
            body = response.json()
            return body['id']
        else:
            print('Error not correct code in get_summoner_id_call:', response.status_code, url)
            return None
    except requests.exceptions.RequestException as e:

        # Handle any network-related errors or exceptions
        print('Error exception in get_summoner_id_call:', e)
        return None


def get_rank_data(summoner_name: str, summoner_id: int, server: str, display_name: str, leaderboard: list) -> None:
    url = GET_RANK_DATA_URL.format(server, summoner_id, RIOT_API_KEY)
    global total_api_calls
    total_api_calls += 1
    print('user', summoner_name)
    try:
        response = requests.get(url)
        print(len(leaderboard))

        print(response.status_code)
        print(response.text)

        if response.status_code == 200:
            body = response.json()
            body_len = len(body)
            if body_len > 0:
                rank_data = None
                # checks to see if players have played normal tft ranked
                while rank_data is None and body_len > 0:
                    if body[body_len - 1][QUEUE_TYPE] == RANKED_QUEUE_TYPE:
                        rank_data = body[body_len - 1]
                    body_len -= 1
                tier: str = rank_data[TIER]  # gets metal rank like iron or bronze
                rank: str = rank_data[RANK]  # gets rank subdivision
                points: int = rank_data[LEAGUE_POINTS]  # gets lp value

                tft_rank_title = f'{tier} {rank} {points} LP'
                tft_rank_value = RiotTiersEnum[tier].value + RiotRanksEnum[rank].value + points
                entry = {SUMMONER_NAME: summoner_name, TFT_RANK_TITLE: tft_rank_title,
                         TFT_RANK_VALUE: tft_rank_value, DISPLAY_NAME: display_name}

                leaderboard.append(entry)
            return None
        else:
            print('Error get_rank_data:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:

        # Handle any network-related errors or exceptions
        print('Error get_rank_data:', e)
        return None


def get_ranks(leaderboard: list) -> None:
    print(RIOT_API_KEY)
    with open('resources\\processedPlayers.json', 'r') as file:
        data = json.load(file)
    for p in data:
        get_rank_data(p[SUMMONER_NAME_JSON_VAL], p[SUMMONER_ID_JSON_VAL], p[SERVER_JSON_VAL], p[DISPLAY_NAME_JSON_VAL],
                      leaderboard)

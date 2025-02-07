import json
import os
import requests
from discord import app_commands

from dotenv import load_dotenv
from enum import Enum
from typing import Final
from datetime import datetime, date

from src.resources.entity import Player, PlayerDataRes

load_dotenv()

class RIOT_TIERS(Enum):
    IRON = 100000000
    BRONZE = 200000000
    SILVER = 300000000
    GOLD = 400000000
    PLATINUM = 500000000
    EMERALD = 600000000
    DIAMOND = 700000000
    MASTER = 800000000
    GRAND_MASTER = 900000000
    CHALLENGER = 1000000000


class RIOT_RANKS(Enum):
    IV = 100000
    III = 200000
    II = 300000
    I = 400000


class SERVER_LOCATION(Enum):
    BR = 'br'
    EUNE = 'eune'
    EUW = 'euw'
    JP = 'jp'
    KR = 'kr'
    LAN = 'lan'
    LAS = 'las'
    ME = 'me'
    NA = 'na'
    OCE = 'oce'
    RU = 'ru'
    SEA = 'sea'
    TR = 'tr'
    TW = 'tw'
    VN = 'vn'

region_map = {
    SERVER_LOCATION.BR: 'americas',
    SERVER_LOCATION.EUNE: 'europe',
    SERVER_LOCATION.EUW: 'europe',
    SERVER_LOCATION.JP: 'asia',
    SERVER_LOCATION.KR: 'asia',
    SERVER_LOCATION.LAN: 'americas',
    SERVER_LOCATION.LAS: 'americas',
    SERVER_LOCATION.ME: 'europe',
    SERVER_LOCATION.NA: 'americas',
    SERVER_LOCATION.OCE: 'asia',
    SERVER_LOCATION.RU: 'europe',
    SERVER_LOCATION.SEA: 'asia',
    SERVER_LOCATION.TR: 'europe',
    SERVER_LOCATION.TW: 'asia',
    SERVER_LOCATION.VN: 'asia',
}

server_name_map = {
    SERVER_LOCATION.BR: 'br1',
    SERVER_LOCATION.EUNE: 'eun1',
    SERVER_LOCATION.EUW: 'euw1',
    SERVER_LOCATION.JP: 'jp1',
    SERVER_LOCATION.KR: 'kr',
    SERVER_LOCATION.LAN: 'la1',
    SERVER_LOCATION.LAS: 'la2',
    SERVER_LOCATION.ME: 'me1',
    SERVER_LOCATION.NA: 'na1',
    SERVER_LOCATION.OCE: 'oc1',
    SERVER_LOCATION.RU: 'ru',
    SERVER_LOCATION.SEA: 'sg2',
    SERVER_LOCATION.TR: 'tr1',
    SERVER_LOCATION.TW: 'tw2',
    SERVER_LOCATION.VN: 'vn2',
}

RIOT_API_KEY: Final[str] = os.getenv('RIOT_API_KEY')

RANKED_QUEUE_TYPE = 'RANKED_TFT'

# CONSTANTS names
SUMMONER_ID_JSON_VAL = 'summonerId'
SUMMONER_NAME_JSON_VAL = 'summonerName'
SERVER_JSON_VAL = 'server'
DISPLAY_NAME_JSON_VAL = 'displayName'
TIER = 'tier'
RANK = 'rank'
LEAGUE_POINTS = 'leaguePoints'
TFT_RANK_VALUE = 'tft_rank_value'
TFT_RANK_TITLE ='tft_rank_title'
QUEUE_TYPE = 'queueType'
SUMMONER_NAME = 'summoner_name'
DISPLAY_NAME = 'display_name'

LEADER_BOARD_TITLE = 'Leaderboard rank: '

GET_ACCOUNT_DATA_URL = 'https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}'

GET_RANK_DATA_URL = 'https://{}.api.riotgames.com/tft/league/v1/entries/by-summoner/{}?api_key={}'

total_api_calls = 0


leaderboard = []

def get_player_data_call(summoner_name: str, location: SERVER_LOCATION) -> PlayerDataRes or None:
    split_name = summoner_name.split('#')
    game_name = split_name[0]
    tag_line = split_name[1]
    url = GET_ACCOUNT_DATA_URL.format(region_map[location], game_name, tag_line, RIOT_API_KEY)
    print("calling get_player_data_call on", summoner_name, location)
    try:
        response = requests.get(url)

        if response.status_code == 200:
            body = response.json()
            print(type(body), body)
            return PlayerDataRes.from_res(body)
        else:
            print('Error api get_player_data_call:', response.status_code, 'Player', game_name, response.content, url)
            return None
    except requests.exceptions.RequestException as e:

        print('Error exception in get_player_data_call:', e)
        return None

def get_ranks() -> None:
    print(RIOT_API_KEY)
    with open('resources\\processedPlayers.json', 'r') as file:
        data = json.load(file)
    for p in data:
        get_rank_data(p[SUMMONER_NAME_JSON_VAL], p[SUMMONER_ID_JSON_VAL], p[SERVER_JSON_VAL], p[DISPLAY_NAME_JSON_VAL])

def get_rank_data(summoner_name: str, summoner_id: int, server: str, display_name: str) -> None:
    # Define the API endpoint URL
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
                # rank_data=body[body_len-1]
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
                tft_rank_value = RIOT_TIERS[tier].value + RIOT_RANKS[rank].value + points
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


def sort_leaderboard() -> None:
    leaderboard.sort(key=lambda x: x[TFT_RANK_VALUE], reverse=True)


def generate_leaderboard_display() -> str:
    now = datetime.now()
    dt_string = now.strftime('%B %d, %Y %I:%M:%S %p')
    leaderboard_str = LEADER_BOARD_TITLE + dt_string + '\n'
    leaderboard_str += '-' * 30 + '\n'
    rank_pos = 0
    last_rank_val = -1
    print("-"*30)
    print(len(leaderboard))
    print(leaderboard)
    final_leaderboard = []

    for val in leaderboard:

        # Check if the value is not already in 'res'
        if val not in final_leaderboard:
            # If not present, append it to 'res'
            final_leaderboard.append(val)

    print(final_leaderboard)
    for entry in final_leaderboard:
        if last_rank_val != entry[TFT_RANK_VALUE]:
            rank_pos += 1
        entry_detail = f'{rank_pos}) {entry[DISPLAY_NAME]}    {entry[TFT_RANK_TITLE]}\n'
        leaderboard_str += entry_detail
    leaderboard_str += '-' * 30
    print(leaderboard_str)
    return leaderboard_str


def get_leaderboard_result() -> str:
    get_ranks()
    sort_leaderboard()
    return generate_leaderboard_display()


def register_tft_race(summoner_name: str, location: SERVER_LOCATION) -> None:

    display_name: str = summoner_name.split("#")[0]
    player: Player = Player(None, summoner_name, display_name, region_map[location], server_name_map[location], date.today(), False, None)
    print(player)

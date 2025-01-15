import json
import os
import requests

from dotenv import load_dotenv
from enum import Enum
from typing import Final

load_dotenv()

class TIER(Enum):
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
class RANK(Enum):
    IV = 100000
    III = 200000
    II = 300000
    I = 400000

leaderboard = []
RANKED_QUEUE_TYPE = 'RANKED_TFT'
RIOT_API_KEY: Final[str] = os.getenv('RIOT_API_KEY')

def get_ranks() -> None:

    print(RIOT_API_KEY)
    with open('actions\processedPlayers.json', 'r') as file:
        data = json.load(file)
    for p in data:
        get_rank_data(p['summonerName'],p['summonerId'])

def get_rank_data(summoner_name: str, summoner_id: int)->None:
    # Define the API endpoint URL
    url = f'https://na1.api.riotgames.com/tft/league/v1/entries/by-summoner/{summoner_id}?api_key={RIOT_API_KEY}'

    try:
        response = requests.get(url)

        if response.status_code == 200:
            body = response.json()
            body_len = len(body)
            if body_len > 0:
                # rank_data=body[body_len-1]
                rank_data = None
                # checks to see if players have played normal tft ranked
                while rank_data is None and body_len > 0:
                    if body[body_len-1]['queueType']==RANKED_QUEUE_TYPE:
                        rank_data = body[body_len-1]
                    body_len-=1
                tier: str = rank_data['tier'] #gets metal rank like iron or bronze
                rank: str = rank_data['rank'] #gets rank subdivision
                points: int = rank_data['leaguePoints'] #gets lp value

                tft_rank_title = f'{tier} {rank} {points} LP'
                tft_rank_value = TIER[tier].value + RANK[rank].value + points
                entry = {"summoner_name":summoner_name, "tft_rank_title" : tft_rank_title, "tft_rank_value": tft_rank_value}

                leaderboard.append(entry)
            return None
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:

        # Handle any network-related errors or exceptions
        print('Error:', e)
        return None


def sort_leaderboard()->None:
    leaderboard.sort(key=lambda x: x['tft_rank_value'], reverse=True)

def generate_leaderboard_display()->str:
    leaderboard_str = "\n-"*30
    rank_pos = 0
    last_rank_val = -1
    for entry in leaderboard:
        if last_rank_val != entry['tft_rank_value']:
            rank_pos+=1
        entry_detail = f'{rank_pos}) {entry['summoner_name']}    {entry['tft_rank_title']}\n'
        leaderboard_str+=entry_detail
    leaderboard_str+="-"*30
    print(leaderboard_str)
    return leaderboard_str

def get_leaderboard_result()->str:
    get_ranks()
    sort_leaderboard()
    return generate_leaderboard_display()
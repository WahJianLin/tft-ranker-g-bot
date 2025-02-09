from enum import Enum


class RiotTiersEnum(Enum):
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


class RiotRanksEnum(Enum):
    IV = 100000
    III = 200000
    II = 300000
    I = 400000


class ServerLocationEnum(Enum):
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


REGION_MAP = {
    ServerLocationEnum.BR: 'americas',
    ServerLocationEnum.EUNE: 'europe',
    ServerLocationEnum.EUW: 'europe',
    ServerLocationEnum.JP: 'asia',
    ServerLocationEnum.KR: 'asia',
    ServerLocationEnum.LAN: 'americas',
    ServerLocationEnum.LAS: 'americas',
    ServerLocationEnum.ME: 'europe',
    ServerLocationEnum.NA: 'americas',
    ServerLocationEnum.OCE: 'asia',
    ServerLocationEnum.RU: 'europe',
    ServerLocationEnum.SEA: 'asia',
    ServerLocationEnum.TR: 'europe',
    ServerLocationEnum.TW: 'asia',
    ServerLocationEnum.VN: 'asia',
}

SERVER_NAME_MAP = {
    ServerLocationEnum.BR: 'br1',
    ServerLocationEnum.EUNE: 'eun1',
    ServerLocationEnum.EUW: 'euw1',
    ServerLocationEnum.JP: 'jp1',
    ServerLocationEnum.KR: 'kr',
    ServerLocationEnum.LAN: 'la1',
    ServerLocationEnum.LAS: 'la2',
    ServerLocationEnum.ME: 'me1',
    ServerLocationEnum.NA: 'na1',
    ServerLocationEnum.OCE: 'oc1',
    ServerLocationEnum.RU: 'ru',
    ServerLocationEnum.SEA: 'sg2',
    ServerLocationEnum.TR: 'tr1',
    ServerLocationEnum.TW: 'tw2',
    ServerLocationEnum.VN: 'vn2',
}

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
TFT_RANK_TITLE = 'tft_rank_title'
QUEUE_TYPE = 'queueType'
SUMMONER_NAME = 'summoner_name'
DISPLAY_NAME = 'display_name'

LEADER_BOARD_TITLE = 'Leaderboard rank: '
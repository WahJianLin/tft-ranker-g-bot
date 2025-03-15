import logging
from datetime import date, datetime

from src.actions.database import insert_player, get_players, insert_player_riot_data, \
    get_player_riot_data_by_ids, update_player_processed, get_player_riot_data_by_id
from src.actions.riot_api import get_ranks, get_summoner_id_call, get_player_data_call
from src.actions.util import format_str_spacing_util
from src.resources.constants import REGION_MAP, SERVER_NAME_MAP, LEADER_BOARD_TITLE, ServerLocationEnum, \
    UNPROCESSED_PLAYERS_TITLE, PlayerStatusEnum
from src.resources.entity import Player, PlayerDataRes, LeaderboardEntry, PlayerRiotData


# Registering into waitlist
def register_player(
        summoner_name: str,
        location: ServerLocationEnum,
        display_name: str | None,
        discord_id: int,
        is_streamer: bool = False
) -> None:
    display_name_to_save: str = display_name if display_name is not None else summoner_name.split("#")[0]
    join_date: date = date.today()
    processed_date: date | None = None

    player: Player = Player(None, summoner_name, display_name_to_save, REGION_MAP[location], SERVER_NAME_MAP[location],
                            join_date, processed_date, is_streamer, PlayerStatusEnum.UNPROCESSED.value, discord_id)
    insert_player(player)


# get list of unprocessed players
def get_unprocessed_players() -> str:
    player_list: list[Player] = get_players()
    unprocessed_players_str: str = UNPROCESSED_PLAYERS_TITLE + '\n'
    unprocessed_players_str += '-' * 120 + '\n'
    space_in_between: int = 50
    for player in player_list:
        player_name_str = f"Player: {player.summoner_name}"
        player_name_str = format_str_spacing_util(player_name_str, space_in_between)
        display_name_str: str = f"Display Name: {player.display_name}"
        display_name_str = format_str_spacing_util(display_name_str, space_in_between)
        register_date_str = f"Register Date: {player.join_date}\n"

        player_detail_str: str = player_name_str + display_name_str + register_date_str
        unprocessed_players_str += player_detail_str
    unprocessed_players_str += '-' * 120 + '\n'

    return unprocessed_players_str


# processing waitlist
def process_waitlist() -> None:
    player_list: list[Player] = get_players()
    summoner_data_tpl: list[tuple[int, str]] = []
    player_ids: list[int] = []

    # gets list of unregistered players and player ids
    for player in player_list:

        player_data_res: PlayerDataRes = get_player_data_call(player.summoner_name, player.region)
        summoner_id: str | None = get_summoner_id_call(player_data_res.puuid, player.riot_server)

        if get_player_riot_data_by_id(player.id) is None:
            player_ids.append(player.id)
            summoner_data_tpl.append(
                (player.id, summoner_id))
        else:
            logging.info("Failed: Competitor already registered")

    # processes the players into competitors and updates relevant tables
    if summoner_data_tpl:
        insert_player_riot_data(summoner_data_tpl)

        player_riot_data_list: list[PlayerRiotData] = get_player_riot_data_by_ids(player_ids)

        processed_ids: list[int] = []

        for player_riot_data in player_riot_data_list:
            processed_ids.append(player_riot_data.player_id)

        if processed_ids:
            update_player_processed(processed_ids)
    else:
        logging.info("Failed: No Competitor to add")


# generating leaderboard
def sort_leaderboard(leaderboard_entries: list[LeaderboardEntry]) -> None:
    leaderboard_entries.sort(key=lambda entry: entry.tft_rank_value, reverse=True)


def gen_ranked_leaderboard_text(leaderboard_entries: list[LeaderboardEntry]) -> str:
    now: datetime = datetime.now()
    dt_string: str = now.strftime('%B %d, %Y %I:%M:%S %p')
    leaderboard_str: str = LEADER_BOARD_TITLE + dt_string + '\n'
    leaderboard_str += '-' * 80 + '\n'
    rank_pos: int = 0
    last_rank_val: int = -1
    final_leaderboard: list[LeaderboardEntry] = []

    # clears out any potential duplicates
    for val in leaderboard_entries:
        if val not in final_leaderboard:
            final_leaderboard.append(val)

    # populates leader board
    for entry in final_leaderboard:
        if last_rank_val != entry.tft_rank_value:
            last_rank_val = entry.tft_rank_value
            rank_pos += 1
        player_name_rank: str = f'{rank_pos}) {entry.display_name}'
        player_name_rank = format_str_spacing_util(player_name_rank, 25)
        entry_detail: str = f'{player_name_rank}{entry.tft_rank_title}\n'
        leaderboard_str += entry_detail
    leaderboard_str += '-' * 80
    return leaderboard_str


def get_leaderboard_result() -> str:
    leaderboard_entries: list[LeaderboardEntry] = get_ranks()
    sort_leaderboard(leaderboard_entries)
    return gen_ranked_leaderboard_text(leaderboard_entries)

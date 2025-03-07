import logging
from datetime import date, datetime

from src.actions.database import insert_player, get_players, insert_competitors, \
    get_competitor_by_summoner_name, get_competitors_by_summoner_names, update_player_processed
from src.actions.riot_api import get_ranks, get_summoner_id_call, get_player_data_call
from src.resources.constants import REGION_MAP, SERVER_NAME_MAP, LEADER_BOARD_TITLE, ServerLocationEnum, \
    UNPROCESSED_PLAYERS_TITLE
from src.resources.entity import Player, PlayerDataRes, Competitor, LeaderboardEntry


# Registering into waitlist
def register_player(summoner_name: str, location: ServerLocationEnum, display_name: str | None,
                    is_streamer: bool = False) -> None:
    display_name_to_save: str = display_name if display_name is not None else summoner_name.split("#")[0]
    join_date: date = date.today()
    is_processed: bool = False
    processed_date: date | None = None

    player: Player = Player(None, summoner_name, display_name_to_save, REGION_MAP[location], SERVER_NAME_MAP[location],
                            join_date, is_processed, processed_date, is_streamer)
    insert_player(player)


# get list of unprocessed players

def get_unprocessed_players() -> str:
    players_tpl: list[tuple[Player, ...]] = get_players()
    unprocessed_players_str: str = UNPROCESSED_PLAYERS_TITLE + '\n'
    unprocessed_players_str += '-' * 30 + '\n'
    space_in_between: str = 10 * " "
    for player_tpl in players_tpl:
        player: Player = Player.from_tuple(player_tpl)
        player_detail_str = f"Player: {player.summoner_name}," + space_in_between
        player_detail_str += f"Display Name: {player.display_name}," + space_in_between
        player_detail_str += f"Register Date: {player.join_date}\n"
        unprocessed_players_str += player_detail_str
    unprocessed_players_str += '-' * 30 + '\n'

    return unprocessed_players_str


# processing waitlist
def process_waitlist() -> None:
    players_tpl: list[tuple[Player, ...]] = get_players()
    summoner_data_tpl: list[tuple[str, str, str, str, bool, int]] = []
    player_ids: list[int] = []

    # gets list of unregistered players and player ids
    for player_tpl in players_tpl:
        player: Player = Player.from_tuple(player_tpl)

        player_data_res: PlayerDataRes = get_player_data_call(player.summoner_name, player.region)
        summoner_id: str | None = get_summoner_id_call(player_data_res.puuid, player.riot_server)

        if get_competitor_by_summoner_name(player.summoner_name) is None:
            player_ids.append(player.id)
            summoner_data_tpl.append(
                (player.summoner_name, summoner_id, player.display_name, player.riot_server, True, player.id))
        else:
            logging.info("Failed: Competitor already registered")

    # processes the players into competitors and updates relevant tables
    if summoner_data_tpl:
        insert_competitors(summoner_data_tpl)

        processed_competitor_tpl: list[tuple[Competitor, ...]] = get_competitors_by_summoner_names(player_ids)

        processed_ids: list[int] = []

        for competitor_tpl in processed_competitor_tpl:
            competitor: Competitor = Competitor.from_tuple(competitor_tpl)
            processed_ids.append(competitor.player_fkey)

        if processed_ids:
            update_player_processed(processed_ids)
    else:
        logging.info("Failed: No Competitor to add)")


# generating leaderboard
def sort_leaderboard(leaderboard_entries: list[LeaderboardEntry]) -> None:
    leaderboard_entries.sort(key=lambda entry: entry.tft_rank_value, reverse=True)


def gen_ranked_leaderboard_text(leaderboard_entries: list[LeaderboardEntry]) -> str:
    now: datetime = datetime.now()
    dt_string: str = now.strftime('%B %d, %Y %I:%M:%S %p')
    leaderboard_str: str = LEADER_BOARD_TITLE + dt_string + '\n'
    leaderboard_str += '-' * 30 + '\n'
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
            rank_pos += 1
        entry_detail: str = f'{rank_pos}) {entry.display_name}    {entry.tft_rank_title}\n'
        leaderboard_str += entry_detail
    leaderboard_str += '-' * 30
    return leaderboard_str


def get_leaderboard_result() -> str:
    leaderboard_entries: list[LeaderboardEntry] = get_ranks()
    sort_leaderboard(leaderboard_entries)
    return gen_ranked_leaderboard_text(leaderboard_entries)

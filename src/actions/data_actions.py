from datetime import date, datetime

from src.actions.database import insert_player, get_players, insert_competitors, \
    get_competitor_by_summoner_name, get_competitors_by_summoner_names, update_player_processed
from src.actions.riot_api import get_ranks, get_summoner_id_call, get_player_data_call
from src.resources.constants import ServerLocationEnum, REGION_MAP, SERVER_NAME_MAP, TFT_RANK_VALUE, LEADER_BOARD_TITLE, \
    DISPLAY_NAME, TFT_RANK_TITLE
from src.resources.entity import Player, PlayerDataRes, Competitor, LeaderboardEntry


# Registering into waitlist
def register_player(summoner_name: str, location: ServerLocationEnum) -> None:
    display_name: str = summoner_name.split("#")[0]
    player: Player = Player(None, summoner_name, display_name, REGION_MAP[location], SERVER_NAME_MAP[location],
                            date.today(), False, None)
    insert_player(player)


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
            print("Failed: Competitor already registered")

    #processes the players into competitors and updates relevant tables
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
        print('Failed: No Competitor to add')


# generating leaderboard
def sort_leaderboard(leaderboard_entries: list[LeaderboardEntry]) -> None:
    leaderboard_entries.sort(key=lambda entry: entry.tft_rank_value, reverse=True)


def generate_leaderboard_display(leaderboard_entries: list[LeaderboardEntry]) -> str:
    now = datetime.now()
    dt_string = now.strftime('%B %d, %Y %I:%M:%S %p')
    leaderboard_str = LEADER_BOARD_TITLE + dt_string + '\n'
    leaderboard_str += '-' * 30 + '\n'
    rank_pos = 0
    last_rank_val = -1
    final_leaderboard: list[LeaderboardEntry] = []

    for val in leaderboard_entries:

        # Check if the value is not already in 'res'
        if val not in final_leaderboard:
            # If not present, append it to 'res'
            final_leaderboard.append(val)

    print(final_leaderboard)
    for entry in final_leaderboard:
        if last_rank_val != entry.tft_rank_value:
            rank_pos += 1
        entry_detail = f'{rank_pos}) {entry.display_name}    {entry.tft_rank_title}\n'
        leaderboard_str += entry_detail
    leaderboard_str += '-' * 30
    print(leaderboard_str)
    return leaderboard_str


def get_leaderboard_result() -> str:
    leaderboard_entries: list[LeaderboardEntry] = get_ranks()
    sort_leaderboard(leaderboard_entries)
    return generate_leaderboard_display(leaderboard_entries)

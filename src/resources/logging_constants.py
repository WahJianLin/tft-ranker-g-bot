# SLASH LOGGING

ERROR_EXISTING_SUMMONER: str = "Failure: {} is already registered."
PERMISSION_IS_NOT_MOD: str = "User is not a Mod."

SLASH_COMMANDS: str = 'Slash Command {} executed'
COMMAND_SUCCESS: str = 'Command Success'
COMMAND_FAIL: str = 'Command Failure'

COMMAND_SUCCESS_SUMMONER_REGISTERED: str = "Registration Success. Please wait until mod reviews registration."
COMMAND_SUCCESS_PROCESS: str = "Players have been processed into competitors."

COMMAND_ERROR_UNEXPECTED: str = "Failure: Unexpected Error."
COMMAND_ERROR_SUMMONER_NAME: str = "Failure: Invalid Summoner Name {}. Summoner_name should match name#tag format."
COMMAND_ERROR_SUMMONER_NOT_FOUND: str = "Failure: Summoner Name and selected server combination not found in riot database."
COMMAND_ERROR_DISPLAY_NAME_LENGTH: str = "Failure: Display Name needs to be between 2 and 17 characters long."

DATABASE_CALL: str = 'Database Action {} executed'
DATABASE_SUCCESS: str = 'Database Action {} Success'
DATABASE_FAIL: str = 'Database Action {} Failure'

DB_CALL_GET_PLAYERS: str = 'get_players'
DB_CALL_GET_PLAYER_BY_NAME: str = 'get_player_by_summoner_name'
DB_CALL_GET_ALL_VALID_COMPETITOR: str = 'get_valid_competitor'
DB_CALL_GET_VALID_COMPETITOR_BY_NAME: str = 'get_competitor_by_summoner_name'
DB_CALL_GET_RIOT_DATA_BY_ID: str = 'get_player_riot_data_by_id'
DB_CALL_GET_VALID_COMPETITORS_BY_NAMES: str = 'get_competitors_by_summoner_names'

DB_CALL_UPDATE_PLAYERS_PROCESSED: str = 'update_player_processed'
DB_CALL_UPDATE_PLAYER_STATUS: str = 'update_player_status'


DB_CALL_INSERT_PLAYER: str = 'insert_player'
DB_CALL_INSERT_COMPETITOR: str = 'insert_competitor'
DB_CALL_INSERT_COMPETITORS: str = 'insert_competitors'

RIOT_CALL: str = 'RIOT Call {} executed'
RIOT_SUCCESS: str = 'RIOT Call Success'
RIOT_FAIL: str = 'RIOT Call Failure'
RIOT_ERROR_CODE: str = 'RIOT Error Code: {}'

RIOT_CALL_GET_RANK_DATA: str = 'get_rank_data'
RIOT_CALL_GET_SUMMONER_ID: str = 'get_summoner_id_call'
RIOT_CALL_GET_PLAYER_DATA_CALL: str = 'get_player_data_call'

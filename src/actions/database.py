import logging
import os
from datetime import datetime, date

import psycopg2
from dotenv import load_dotenv
from psycopg2._psycopg import connection, cursor

from src.resources.constants import PlayerStatusEnum
from src.resources.entity import Player, CompetitorV, PlayerRiotData
from src.resources.logging_constants import DATABASE_CALL, DB_CALL_GET_ALL_VALID_COMPETITOR, DATABASE_SUCCESS, \
    DATABASE_FAIL, DB_CALL_GET_VALID_COMPETITOR_BY_NAME, DB_CALL_GET_VALID_COMPETITORS_BY_NAMES, \
    DB_CALL_UPDATE_PLAYERS_PROCESSED, DB_CALL_INSERT_COMPETITOR, ERROR_EXISTING_SUMMONER, DB_CALL_INSERT_PLAYER, \
    DB_CALL_GET_PLAYER_BY_NAME, DB_CALL_GET_PLAYERS, DB_CALL_UPDATE_PLAYER_STATUS, DB_CALL_GET_RIOT_DATA_BY_ID, \
    DB_CALL_UPDATE_MISSING_PUUID, DB_CALL_GET_MISSING_PUUID

load_dotenv()

SCHEMA: str = os.getenv('DATABASE_SCHEMA')

PLAYER_TABLE: str = 'players'
RIOT_DATA_TABLE: str = 'riot_data'
COMPETITOR_VIEW: str = 'competitor_v'


def db_base_connect() -> connection:
    return psycopg2.connect(
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASS'),
        host=os.getenv('DATABASE_HOST'),
        port=int(os.getenv('DATABASE_PORT'))
    )


def get_players_by_status(status: PlayerStatusEnum = PlayerStatusEnum.UNPROCESSED) -> list[Player]:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_PLAYERS))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        player_list: list[Player] = []

        query: str = f"SELECT * FROM {SCHEMA}.{PLAYER_TABLE} where player_status = %s"
        db_cursor.execute(query, [status.value])
        records: list[tuple[any, ...]] = db_cursor.fetchall()

        for player_tpl in records:
            player: Player = Player(player_tpl[0], player_tpl[1], player_tpl[2], player_tpl[3],
                                    player_tpl[4], player_tpl[5], player_tpl[6], player_tpl[7],
                                    player_tpl[8], player_tpl[9])
            player_list.append(player)

        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS.format(DB_CALL_GET_PLAYERS))
        return player_list
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_GET_PLAYERS))
        logging.exception(e)
        raise Exception(format(e)) from None


def get_player_by_summoner_name(summoner_name: str) -> Player | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_PLAYER_BY_NAME))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        query: str = f"SELECT * FROM {SCHEMA}.{PLAYER_TABLE} WHERE summoner_name = %s"
        db_cursor.execute(query, [summoner_name])
        record: tuple[any, ...] = db_cursor.fetchone()

        db_cursor.close()
        conn.close()

        if record is None:
            logging.info(DATABASE_SUCCESS.format(DB_CALL_GET_PLAYER_BY_NAME))
            return None

        player: Player = Player(record[0], record[1], record[2], record[3], record[4], record[5], record[6],
                                record[7], record[8], record[9])

        logging.info(DATABASE_SUCCESS.format(DB_CALL_GET_PLAYER_BY_NAME))
        return player
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_GET_PLAYER_BY_NAME))
        logging.exception(e)
        raise Exception(format(e)) from None


def insert_player(player: Player) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_INSERT_PLAYER))
        if get_player_by_summoner_name(player.summoner_name) is None:
            conn: connection = db_base_connect()
            db_cursor: cursor = conn.cursor()
            query: str = f"INSERT INTO {SCHEMA}.{PLAYER_TABLE}(summoner_name, display_name, region, riot_server, join_date, processed_date, is_streamer, player_status, discord_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values: tuple[str, str, str, str, datetime, datetime, bool, PlayerStatusEnum, int] = (
                player.summoner_name,
                player.display_name,
                player.region,
                player.riot_server,
                player.join_date,
                player.processed_date,
                player.is_streamer,
                player.player_status,
                player.discord_id
            )
            db_cursor.execute(query, values)
            conn.commit()
            db_cursor.close()
            conn.close()

            logging.info(DATABASE_SUCCESS.format(DB_CALL_INSERT_PLAYER))
        else:
            logging.info(ERROR_EXISTING_SUMMONER.format(player.summoner_name))
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_INSERT_PLAYER))
        logging.exception(e)
        raise Exception(format(e)) from None


def get_competitors_by_status() -> list[CompetitorV] | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_ALL_VALID_COMPETITOR))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        competitor_list: list[CompetitorV] = []

        query: str = f"SELECT * FROM {SCHEMA}.{COMPETITOR_VIEW} where player_status = %s"

        db_cursor.execute(query, [PlayerStatusEnum.COMPETING.value])
        records: list[tuple[any, ...]] = db_cursor.fetchall()
        for comp_tpl in records:
            competitor: CompetitorV = CompetitorV(comp_tpl[0], comp_tpl[1], comp_tpl[2],
                                                  PlayerStatusEnum(comp_tpl[3]), comp_tpl[4], comp_tpl[5])
            competitor_list.append(competitor)
        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS.format(DB_CALL_GET_ALL_VALID_COMPETITOR))
        return competitor_list
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_GET_ALL_VALID_COMPETITOR))
        logging.exception(e)
        raise Exception(format(e)) from None


# deprecated
def get_competitor_by_summoner_name(player_id: int) -> Player | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_VALID_COMPETITOR_BY_NAME))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        query: str = f"SELECT * FROM {SCHEMA}.{RIOT_DATA_TABLE} WHERE player_id = %s"
        db_cursor.execute(query, [player_id])
        record: tuple[any, ...] = db_cursor.fetchone()

        player: Player = Player(record[0], record[1], record[2], record[3], record[4], record[5], record[6],
                                record[7], record[8], record[9])

        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS.format(DB_CALL_GET_VALID_COMPETITOR_BY_NAME))
        return player
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_GET_VALID_COMPETITOR_BY_NAME))
        logging.exception(e)
        raise Exception(format(e)) from None


def get_player_riot_data_by_id(player_id: int) -> PlayerRiotData | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_RIOT_DATA_BY_ID))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        query: str = f"SELECT * FROM {SCHEMA}.{RIOT_DATA_TABLE} WHERE player_id = %s"
        db_cursor.execute(query, [player_id])
        record: tuple[any, ...] = db_cursor.fetchone()

        db_cursor.close()
        conn.close()

        if record is None:
            logging.info(DATABASE_SUCCESS.format(DB_CALL_GET_RIOT_DATA_BY_ID))
            return None

        player_riot_data: PlayerRiotData = PlayerRiotData(record[0], record[1], None, record[2])
        logging.info(DATABASE_SUCCESS.format(DB_CALL_GET_RIOT_DATA_BY_ID))
        return player_riot_data
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_GET_RIOT_DATA_BY_ID))
        logging.exception(e)
        raise Exception(format(e)) from None


def get_player_riot_data_by_ids(player_ids: list[int]) -> list[PlayerRiotData] | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_VALID_COMPETITORS_BY_NAMES))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        player_riot_data_list: list[PlayerRiotData] = []

        format_strings = ','.join(['%s'] * len(player_ids))
        query: str = f"SELECT id, player_id, puuid FROM {SCHEMA}.{RIOT_DATA_TABLE} WHERE player_id IN (%s)" % format_strings
        db_cursor.execute(query, tuple(player_ids))
        records: list[tuple[any, ...]] = db_cursor.fetchall()

        for player_data_tpl in records:
            player_data: PlayerRiotData = PlayerRiotData(player_data_tpl[0], player_data_tpl[1],
                                                         None, player_data_tpl[2])
            player_riot_data_list.append(player_data)

        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS.format(DB_CALL_GET_VALID_COMPETITORS_BY_NAMES))
        return player_riot_data_list
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_GET_VALID_COMPETITORS_BY_NAMES))
        logging.exception(e)
        raise Exception(format(e)) from None


def get_missing_puuid() -> list[tuple[int, str, str]]:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_MISSING_PUUID))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        query: str = f"SELECT rd.id, pl.summoner_name, pl.region FROM {SCHEMA}.{PLAYER_TABLE} AS pl JOIN {SCHEMA}.{RIOT_DATA_TABLE} AS rd on pl.id = rd.player_id WHERE rd.puuid IS NULL"
        db_cursor.execute(query)
        records: list[tuple[any, ...]] = db_cursor.fetchall()

        missing_list: list[tuple[int, str, str]] = [(record[0], record[1], record[2]) for record in records]
        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS.format(DB_CALL_GET_MISSING_PUUID))
        return missing_list
    except Exception as e:
        logging.exception(e)
        raise Exception(format(e)) from None


def update_player_processed(player_ids: list[int]) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_UPDATE_PLAYERS_PROCESSED))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        today: date = date.today()

        query: str = f"UPDATE {SCHEMA}.{PLAYER_TABLE} SET player_status = %s, processed_date = %s WHERE id = %s"
        data: list[tuple[PlayerStatusEnum, date, int]] = [(PlayerStatusEnum.COMPETING.value, today, player_id) for
                                                          player_id in player_ids]

        db_cursor.executemany(query, data)

        conn.commit()
        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS.format(DB_CALL_UPDATE_PLAYERS_PROCESSED))
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_UPDATE_PLAYERS_PROCESSED))
        logging.exception(e)
        raise Exception(format(e)) from None


# untested
def insert_competitor(player: Player, summoner_id: str) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_INSERT_COMPETITOR))
        if get_competitor_by_summoner_name(player.id) is None:
            conn: connection = db_base_connect()
            db_cursor: cursor = conn.cursor()
            query: str = f"INSERT INTO {SCHEMA}.{RIOT_DATA_TABLE}(player_id, summoner_id)	VALUES (%s, %s)"
            values: tuple[int, str] = (
                player.id, summoner_id
            )
            db_cursor.execute(query, values)
            conn.commit()
            db_cursor.close()
            conn.close()

            logging.info(DATABASE_SUCCESS.format(DB_CALL_INSERT_COMPETITOR))
        else:
            logging.info(ERROR_EXISTING_SUMMONER.format(player.summoner_name))
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_INSERT_COMPETITOR))
        logging.exception(e)
        raise Exception(format(e)) from None


def insert_player_riot_data(competitors_list: list[tuple[int, str]]) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_INSERT_COMPETITOR))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()
        query: str = f"INSERT INTO {SCHEMA}.{RIOT_DATA_TABLE}(player_id, puuid)	VALUES "
        args_str = ','.join(
            db_cursor.mogrify("(%s, %s)", competitor).decode('utf-8') for competitor in
            competitors_list)

        db_cursor.execute(query + args_str)

        conn.commit()
        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS.format(DB_CALL_INSERT_COMPETITOR))
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_INSERT_COMPETITOR))
        logging.exception(e)
        raise Exception(format(e)) from None


def update_missing_puuid(puuid_list: list[tuple[int, str]]) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_UPDATE_MISSING_PUUID))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        args_str = ','.join(
            db_cursor.mogrify("(%s, %s)", tpl).decode('utf-8') for tpl in
            puuid_list)

        query = f"UPDATE {SCHEMA}.{RIOT_DATA_TABLE} AS rd SET puuid = v.puuid FROM (VALUES {args_str}) AS v(id, puuid) WHERE rd.id = v.id;"

        db_cursor.execute(query)

        conn.commit()
        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS.format(DB_CALL_UPDATE_MISSING_PUUID))
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_UPDATE_MISSING_PUUID))
        logging.exception(e)
        raise Exception(format(e)) from None


def db_update_player_status(player_id: int, status: PlayerStatusEnum) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_UPDATE_PLAYER_STATUS))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        query: str = f"UPDATE {SCHEMA}.{PLAYER_TABLE} SET player_status = %s WHERE id = %s"
        values: tuple[str, int] = (status.value, player_id)

        db_cursor.execute(query, values)

        conn.commit()
        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS.format(DB_CALL_UPDATE_PLAYER_STATUS))
    except Exception as e:
        logging.info(DATABASE_FAIL.format(DB_CALL_UPDATE_PLAYER_STATUS))
        logging.exception(e)
        raise Exception(format(e)) from None

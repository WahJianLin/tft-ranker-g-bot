import logging
import os
from datetime import datetime, date

import psycopg2
from dotenv import load_dotenv
from psycopg2._psycopg import connection, cursor

from src.resources.constants import PlayerStatusEnum
from src.resources.entity import Player, Competitor, PlayerRiotData
from src.resources.logging_constants import DATABASE_CALL, DB_CALL_GET_ALL_VALID_COMPETITOR, DATABASE_SUCCESS, \
    DATABASE_FAIL, DB_CALL_GET_VALID_COMPETITOR_BY_NAME, DB_CALL_GET_VALID_COMPETITORS_BY_NAMES, \
    DB_CALL_UPDATE_PLAYERS_PROCESSED, DB_CALL_INSERT_COMPETITOR, ERROR_EXISTING_SUMMONER, DB_CALL_INSERT_PLAYER, \
    DB_CALL_GET_PLAYER_BY_NAME, DB_CALL_GET_PLAYERS

load_dotenv()

PLAYER_TABLE: str = 'players_dev'
RIOT_DATA_TABLE: str = 'riot_data_dev'

def db_base_connect() -> connection:
    return psycopg2.connect(
        database=os.getenv('DATA_BASE_NAME'),
        user=os.getenv('DATA_BASE_USER'),
        password=os.getenv('DATA_BASE_PASS'),
        host=os.getenv('DATA_BASE_HOST'),
        port=int(os.getenv('DATABASE_PORT'))
    )


def get_players(is_processed: bool = False) -> list[tuple[Player, ...]]:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_PLAYERS))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        query: str = f"SELECT * FROM {PLAYER_TABLE}"
        db_cursor.execute(query, [str(is_processed)])
        records: list[tuple[Player, ...]] = db_cursor.fetchall()

        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS)
        return records
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)


def get_player_by_summoner_name(summoner_name: str) -> tuple[Player, ...] | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_PLAYER_BY_NAME))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        query: str = f"SELECT * FROM {PLAYER_TABLE} WHERE summoner_name = %s"
        db_cursor.execute(query, [summoner_name])
        record: tuple[Player, ...] = db_cursor.fetchone()

        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS)
        return record
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)


def insert_player(player: Player) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_INSERT_PLAYER))
        if get_player_by_summoner_name(player.summoner_name) is None:
            conn: connection = db_base_connect()
            db_cursor: cursor = conn.cursor()
            values: tuple[str, str, str, str, datetime, datetime, bool, PlayerStatusEnum] = (
                player.summoner_name,
                player.display_name,
                player.region,
                player.riot_server,
                player.join_date,
                player.processed_date,
                player.is_streamer,
                player.player_status
            )
            db_cursor.execute(
                f"INSERT INTO public.{PLAYER_TABLE}(summoner_name, display_name, region, riot_server, join_date, "
                "processed_date, is_streamer, player_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                values
            )
            conn.commit()
            db_cursor.close()
            conn.close()

            logging.info(DATABASE_SUCCESS)
        else:
            logging.info(ERROR_EXISTING_SUMMONER.format(player.summoner_name))
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)


def get_valid_competitor() -> list[tuple[Competitor, ...]] | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_ALL_VALID_COMPETITOR))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        query: str = f"SELECT * FROM {RIOT_DATA_TABLE} WHERE is_competing = true"
        db_cursor.execute(query)
        record: list[tuple[Competitor, ...]] = db_cursor.fetchall()

        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS)
        return record
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)


def get_competitor_by_summoner_name(summoner_name: str) -> tuple[Player, ...] | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_VALID_COMPETITOR_BY_NAME))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        query: str = f"SELECT * FROM {RIOT_DATA_TABLE} WHERE summoner_name = %s"
        db_cursor.execute(query, [summoner_name])
        record: tuple[Player, ...] = db_cursor.fetchone()

        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS)
        return record
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)

def get_player_riot_data(player_id: int) -> tuple[Player, ...] | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_VALID_COMPETITOR_BY_NAME))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        query: str = f"SELECT * FROM {RIOT_DATA_TABLE} WHERE player_id = %s"
        db_cursor.execute(query, [player_id])
        record: tuple[Player, ...] = db_cursor.fetchone()

        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS)
        return record
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)


def get_competitors_by_summoner_names(player_ids: list[int]) -> list[tuple[PlayerRiotData, ...]] | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_VALID_COMPETITORS_BY_NAMES))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        format_strings = ','.join(['%s'] * len(player_ids))
        query: str = f"SELECT * FROM {RIOT_DATA_TABLE} WHERE player_id IN (%s)" % format_strings
        db_cursor.execute(query, tuple(player_ids))
        record: list[tuple[PlayerRiotData, ...]] = db_cursor.fetchall()

        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS)
        return record
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)


def update_player_processed(player_ids: list[int]) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_UPDATE_PLAYERS_PROCESSED))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        today: date = date.today()

        # query: str = f"UPDATE players SET player_status = true, processed_date = %s WHERE id = %s"

        query: str = f"UPDATE {PLAYER_TABLE} SET player_status = %s, processed_date = %s WHERE id = %s"
        data: list[tuple[PlayerStatusEnum, date, int]] = [(PlayerStatusEnum.COMPETING.value, today, player_id) for player_id in player_ids]

        db_cursor.executemany(query, data)

        conn.commit()
        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS)
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)


def insert_competitor(player: Player, summoner_id: str) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_INSERT_COMPETITOR))
        if get_competitor_by_summoner_name(player.summoner_name) is None:
            conn: connection = db_base_connect()
            db_cursor: cursor = conn.cursor()
            query: str = "INSERT INTO public.competitors(summoner_name, summoner_id, display_name, riot_server, is_competing)	VALUES (%s, %s, %s, %s, %s)"
            values: tuple[str, str, str, str, bool] = (
                player.summoner_name, summoner_id, player.display_name, player.riot_server, True
            )
            db_cursor.execute(query, values)
            conn.commit()
            db_cursor.close()
            conn.close()

            logging.info(DATABASE_SUCCESS)
        else:
            logging.info(ERROR_EXISTING_SUMMONER.format(player.summoner_name))
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)


def insert_competitors(competitors_list: list[tuple[int, str]]) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_INSERT_COMPETITOR))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()
        query: str = f"INSERT INTO public.{RIOT_DATA_TABLE}(player_id, summoner_id)	VALUES "
        args_str = ','.join(
            db_cursor.mogrify("(%s, %s)", competitor).decode('utf-8') for competitor in
            competitors_list)

        db_cursor.execute(query + args_str)

        conn.commit()
        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS)
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)

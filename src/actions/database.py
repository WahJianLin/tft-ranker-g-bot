import logging
import os
from datetime import datetime, date

import psycopg2
from dotenv import load_dotenv
from psycopg2._psycopg import connection, cursor

from src.resources.entity import Player, Competitor
from src.resources.logging_constants import DATABASE_CALL, DB_CALL_GET_ALL_VALID_COMPETITOR, DATABASE_SUCCESS, \
    DATABASE_FAIL, DB_CALL_GET_VALID_COMPETITOR_BY_NAME, DB_CALL_GET_VALID_COMPETITORS_BY_NAMES, \
    DB_CALL_UPDATE_PLAYERS_PROCESSED, DB_CALL_INSERT_COMPETITOR, ERROR_EXISTING_SUMMONER, DB_CALL_INSERT_PLAYER, \
    DB_CALL_GET_PLAYER_BY_NAME, DB_CALL_GET_PLAYERS

load_dotenv()


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

        query: str = "SELECT * FROM players WHERE is_processed = %s"
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

        query: str = "SELECT * FROM players WHERE summoner_name = %s"
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
            values: tuple[str, str, str, str, datetime, bool, datetime, bool] = (
                player.summoner_name,
                player.display_name,
                player.region,
                player.riot_server,
                player.join_date,
                player.is_processed,
                player.processed_date,
                player.is_streamer
            )
            db_cursor.execute(
                "INSERT INTO public.players(summoner_name, display_name, region, riot_server, join_date, "
                "is_processed, processed_date, is_streamer) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
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

        query: str = "SELECT * FROM competitors WHERE is_competing = true"
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

        query: str = "SELECT * FROM competitors WHERE summoner_name = %s"
        db_cursor.execute(query, [summoner_name])
        record: tuple[Player, ...] = db_cursor.fetchone()

        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS)
        return record
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)


def get_competitors_by_summoner_names(player_ids: list[int]) -> list[tuple[Competitor, ...]] | None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_GET_VALID_COMPETITORS_BY_NAMES))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()

        format_strings = ','.join(['%s'] * len(player_ids))
        query: str = "SELECT * FROM competitors WHERE player_fkey IN (%s)" % format_strings
        db_cursor.execute(query, tuple(player_ids))
        record: list[tuple[Competitor, ...]] = db_cursor.fetchall()

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

        query: str = "UPDATE players SET is_processed = true, processed_date = %s WHERE id = %s"
        data: list[tuple[date, int]] = [(today, player_id) for player_id in player_ids]

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


def insert_competitors(competitors_list: list[tuple[str, str, str, str, bool, int]]) -> None:
    try:
        logging.info(DATABASE_CALL.format(DB_CALL_INSERT_COMPETITOR))
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()
        query: str = "INSERT INTO public.competitors(summoner_name, summoner_id, display_name, riot_server, is_competing, player_fkey)	VALUES "
        args_str = ','.join(
            db_cursor.mogrify("(%s, %s, %s, %s, %s, %s)", competitor).decode('utf-8') for competitor in
            competitors_list)

        db_cursor.execute(query + args_str)

        conn.commit()
        db_cursor.close()
        conn.close()

        logging.info(DATABASE_SUCCESS)
    except Exception as e:
        logging.info(DATABASE_FAIL)
        logging.exception(e)

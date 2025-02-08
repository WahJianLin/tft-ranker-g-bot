import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from psycopg2._psycopg import connection, cursor

from src.resources.entity import Player

load_dotenv()


def db_base_connect() -> connection:
    return psycopg2.connect(
        database=os.getenv('DATA_BASE_NAME'),
        user=os.getenv('DATA_BASE_USER'),
        password=os.getenv('DATA_BASE_PASS'),
        host=os.getenv('DATA_BASE_HOST'),
        port=int(os.getenv('DATABASE_PORT'))
    )


def get_unprocessed_players() -> list[tuple[Player, ...]]:
    conn: connection = db_base_connect()
    db_cursor: cursor = conn.cursor()

    query: str = "SELECT * FROM players"
    db_cursor.execute(query)
    records: list[tuple[Player, ...]] = db_cursor.fetchall()

    db_cursor.close()
    conn.close()
    return records


def get_unprocessed_player_by_summoner_name(summoner_name: str) -> tuple[Player, ...] | None:
    conn: connection = db_base_connect()
    db_cursor: cursor = conn.cursor()

    query: str = "SELECT * FROM players WHERE summoner_name = %s"
    db_cursor.execute(query, [summoner_name])
    record: tuple[Player, ...] = db_cursor.fetchone()

    db_cursor.close()
    conn.close()
    return record


def insert_unprocessed_players(player: Player) -> None:
    if get_unprocessed_player_by_summoner_name(player.summoner_name) is None:
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()
        values: tuple[str, str, str, str, datetime, bool, datetime] = (
            player.summoner_name, player.display_name, player.region, player.server, player.join_date,
            player.is_processed,
            player.processed_date
        )
        db_cursor.execute(
            "INSERT INTO public.players(summoner_name, display_name, region, server, join_date, "
            "is_processed, processed_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            values
        )
        conn.commit()
        print("Success: Player Registered")
        db_cursor.close()
        conn.close()
    else:
        print("Failed: Player already registered")

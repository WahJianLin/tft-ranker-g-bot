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


def get_players(is_processed: bool = False) -> list[tuple[Player, ...]]:
    conn: connection = db_base_connect()
    db_cursor: cursor = conn.cursor()

    query: str = "SELECT * FROM players WHERE is_processed = %s"
    db_cursor.execute(query, [str(is_processed)])
    records: list[tuple[Player, ...]] = db_cursor.fetchall()

    db_cursor.close()
    conn.close()
    return records


def get_player_by_summoner_name(summoner_name: str) -> tuple[Player, ...] | None:
    conn: connection = db_base_connect()
    db_cursor: cursor = conn.cursor()

    query: str = "SELECT * FROM players WHERE summoner_name = %s"
    db_cursor.execute(query, [summoner_name])
    record: tuple[Player, ...] = db_cursor.fetchone()

    db_cursor.close()
    conn.close()
    return record


def insert_player(player: Player) -> None:
    if get_player_by_summoner_name(player.summoner_name) is None:
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()
        values: tuple[str, str, str, str, datetime, bool, datetime] = (
            player.summoner_name, player.display_name, player.region, player.riot_server, player.join_date,
            player.is_processed,
            player.processed_date
        )
        db_cursor.execute(
            "INSERT INTO public.players(summoner_name, display_name, region, riot_server, join_date, "
            "is_processed, processed_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            values
        )
        conn.commit()
        print("Success: Player Registered")
        db_cursor.close()
        conn.close()
    else:
        print("Failed: Player already registered")

def get_competitor_by_summoner_name(summoner_name: str) -> tuple[Player, ...] | None:
    conn: connection = db_base_connect()
    db_cursor: cursor = conn.cursor()

    query: str = "SELECT * FROM competitors WHERE summoner_name = %s"
    db_cursor.execute(query, [summoner_name])
    record: tuple[Player, ...] = db_cursor.fetchone()

    db_cursor.close()
    conn.close()
    return record

def insert_competitor(player: Player, summoner_id: str) -> None:
    if get_competitor_by_summoner_name(player.summoner_name) is None:
        conn: connection = db_base_connect()
        db_cursor: cursor = conn.cursor()
        values: tuple[str, str, str, str, bool] = (
            player.summoner_name, summoner_id, player.display_name, player.riot_server, True
        )
        db_cursor.execute(
            "INSERT INTO public.competitors(summoner_name, summoner_id, display_name, riot_server, is_competing)	VALUES (%s, %s, %s, %s, %s)",
            values
        )
        conn.commit()
        print("Success: Competitor is processed and registered")
        db_cursor.close()
        conn.close()
    else:
        print("Failed: Competitor already registered")

def insert_competitors(competitors_list:list[tuple[str, str, str, str, bool]]) -> None:
    conn: connection = db_base_connect()
    db_cursor: cursor = conn.cursor()
    query: str =  "INSERT INTO public.competitors(summoner_name, summoner_id, display_name, riot_server, is_competing)	VALUES "
    args_str = ','.join(db_cursor.mogrify("(%s, %s, %s, %s, %s)", competitor).decode('utf-8') for competitor in competitors_list)
    print(query + args_str)
    db_cursor.execute(query + args_str)

    conn.commit()
    print("Success: Competitor is processed and registered")
    db_cursor.close()
    conn.close()
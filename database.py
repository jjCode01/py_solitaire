import psycopg2

from config import config


def games_played() -> list:
    conn = None
    games = []
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT win_flag from game", [])
        games = cur.fetchall()
        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return games


def games_won():
    ...


def insert_game(date, type, win_flag, duration_seconds, move_count):
    sql = """INSERT INTO game(date, type, win_flag, duration_seconds, move_count)
             VALUES(%s,%s,%s,%s,%s)"""

    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(
            sql,
            (
                date,
                type,
                win_flag,
                duration_seconds,
                move_count,
            ),
        )
        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

import psycopg2

from config import config


def main():
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)

        cur = conn.cursor()
        cur.execute("SELECT version()")

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


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
        print("Error in writing to database...")
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()

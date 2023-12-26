import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv('DB_PATH')
allowed_table_names = ['mantlejumpmap', 'firstmap', 'gymmap', 'doorbouncemap']


def insert_into_db(player_name, time_score, table_name):
    if table_name not in allowed_table_names:
        return []
    
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            player_name TEXT,
            time_score REAL
        )
    '''
    
    try:
        cur.execute(query)
        cur.execute(f"INSERT INTO {table_name} (player_name, time_score) VALUES (?, ?)", (player_name, time_score))
        con.commit()
        con.close()
    except:
        print("Error executing insert_into_db query...")


def read_leaderboard(table_name):
    if table_name not in allowed_table_names:
        return []
    
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    query = f'''
        SELECT player_name, MIN(time_score) as min_time_score
        FROM {table_name}
        GROUP BY player_name
        ORDER BY min_time_score
        LIMIT 10
    '''

    try:
        cur.execute(query)
        results = cur.fetchall()
        con.close()
    except:
        print("Error executing read_leaderboard query...")
        return []

    return results


def read_personal_best(player_name, table_name):
    if table_name not in allowed_table_names:
        return []
    
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    query = f'''
        SELECT player_name, time_score
        FROM {table_name}
        WHERE player_name = ?
        ORDER BY time_score
        LIMIT 10
    '''

    try:
        cur.execute(query, (player_name,))
        results = cur.fetchall()
        con.close()
    except:
        print("Error executing read_personal_best query...")
        return []

    return results


def timer_converter(timer):
    minutes, seconds = divmod(timer, 60)
    return f"{int(minutes):02d}", f"{int(seconds):02d}"


def table_constructor(leaderboard):
    table = "```ansi\n"
    table += "[2;45m[2;37m{:<5} {:<20}  {:<10}[0m[2;45m[0m[2;45m[2;37m[0m[2;45m[0m\n".format("Rank", "Username", "Best Time")
    for idx, (player_name, time_score) in enumerate(leaderboard, start=1):
        time_score = timer_converter(time_score)
        time_score = f"{time_score[0]}:{time_score[1]}"
        if idx % 2 == 0:
            table += "[2;45m[2;37m[2;47m[2;30m{:<5} {:<26} {}[0m[2;37m[2;47m[0m[2;37m[2;45m[0m[2;45m[0m[2;45m[2;37m[0m[2;45m[0m\n".format(idx, player_name[:20], time_score)
        else:
            table += "[2;40m{:<5} {:<26} {}\n[0m".format(idx, player_name[:20], time_score)
    table += "```"

    return table
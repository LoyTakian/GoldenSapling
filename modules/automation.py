from r5rIntegration import read_and_process_txt_file, update_top10_file
from dbIntegration import read_leaderboard, allowed_table_names
from collections import defaultdict
from dotenv import load_dotenv
from datetime import datetime
import os
import time
import requests
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import subprocess
from pathlib import Path

load_dotenv()
R5R_SERVER_EXE = os.getenv("R5R_SERVER_EXE")
R5R_SERVERS_URL = os.getenv("R5R_SERVERS_URL")
RECORDS_FOLDER_PATH = os.getenv("RECORDS_FOLDER_PATH")
DISCORD_BOT_PATH = os.getenv("DISCORD_BOT_PATH")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file_path = os.path.join(f"{DISCORD_BOT_PATH}logs", "info.log")
handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=365)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



def r5r_request():
    global player_count
    global hub

    try:
        response = requests.post(R5R_SERVERS_URL, timeout=60)
        servers = response.json().get("servers")
    except Exception as e:  # noqa: E722
        print(f"r5r_request exception: {e}")
        player_count = "K"
        hub = []
        return False
    
    hub = next(
        (
            server
            for server in servers
            if server.get("name") == "[NA] MOVEMENT HUB"
        ),
        [],
    )
    player_count = hub.get("playerCount", "Z") if hub else "X"
    
    return True

def edit_files():
    global to_be_added

    files = [f for f in os.listdir(RECORDS_FOLDER_PATH) if f.endswith(".txt")]
    sorted_files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))

    to_be_added = defaultdict(list)

    for file in sorted_files:
        file_path = os.path.join(RECORDS_FOLDER_PATH, file)

        try:
            run = read_and_process_txt_file(f"{file_path}")
            to_be_added[run[2]].append((run[0], run[1]))
            os.remove(file_path)

        except:  # noqa: E722
            continue

    return True

def edit_info():
    global to_be_added

    try:
        with open(f"{DISCORD_BOT_PATH}info.json", "r") as file:
            info = json.load(file)

            for map, players in info.get("new_runs").items():
                for player in players:
                    to_be_added["".join(map.lower().split())].append(
                        (player["player_name"], player["time_score"])
                    )

    except:  # noqa: E722
        print("Error reading info.json file")

    try:
        with open(f"{DISCORD_BOT_PATH}info.json", "w") as file:
            data = {
                "players": player_count,
                "new_runs": {
                    "First Map": [
                        {"player_name": player[0], "time_score": player[1]}
                        for player in to_be_added.get("firstmap", [])
                    ],
                    "Gym Map": [
                        {"player_name": player[0], "time_score": player[1]}
                        for player in to_be_added.get("gymmap", [])
                    ],
                    "Mantle Jump Map": [
                        {"player_name": player[0], "time_score": player[1]}
                        for player in to_be_added.get("mantlejumpmap", [])
                    ],
                    "It Hurts Map": [
                        {"player_name": player[0], "time_score": player[1]}
                        for player in to_be_added.get("ithurtsmap", [])
                    ],
                    "Strafe It Map": [
                        {"player_name": player[0], "time_score": player[1]}
                        for player in to_be_added.get("strafeitmap", [])
                    ],
                },
            }

            json_string = json.dumps(data, indent=4)
            file.write(json_string)

    except:  # noqa: E722
        print("Error writing info.json file")

    return True

def update_top10():
    global entries

    entries = {}
    for table in allowed_table_names:
        try:
            leaderboard = read_leaderboard(table)
            entries[table] = leaderboard
            update_top10_file(entries)

        except:  # noqa: E722
            continue
    
    return True


os.chdir(R5R_SERVER_EXE)
while True:
    count = 0
    player_count = "Y"
    hub = []
    files = []
    entries = {}
    to_be_added = defaultdict(list)
    logger.info("---------------------------------------------------------------")
    logger.info(f"Loop Start! player_count: {player_count} | hub: {hub} | files: {files} | to_be_added: {to_be_added}")

    r5r_request()

    edit_files()

    edit_info()

    update_top10()

    while player_count == "K":
        if count <= 2:    
            logger.info(f"Request Failed {count} times! Player Count: {player_count} | to be added: {to_be_added}")
            time.sleep(30)
            r5r_request()
            count += 1
        else:
            break
    
    logger.info(f"Player Count: {player_count} | to be added: {to_be_added}")
    
    if not hub:
        try:
            # Kill the process
            subprocess.run(["taskkill", "/f", "/im", "r5apex_ds.exe"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to restart HUB: {e}")

        try:
            # Restart HUB
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Restarting HUB - {current_time}")
            hub_exe_path = Path(f"{R5R_SERVER_EXE}r5apex_ds.exe")

            # Start HUB
            subprocess.Popen(str(hub_exe_path.resolve()))
        except FileNotFoundError as e:
            print(f"File not found: {e}")

    time.sleep(60)

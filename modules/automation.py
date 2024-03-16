from r5rIntegration import read_and_process_txt_file, update_top10_file
from dbIntegration import read_leaderboard, allowed_table_names
from collections import defaultdict
from dotenv import load_dotenv
from datetime import datetime
import os
import time
import requests
import json
# import logging

load_dotenv()
R5R_SERVER_EXE = os.getenv("R5R_SERVER_EXE")
R5R_SERVERS_URL = os.getenv("R5R_SERVERS_URL")
RECORDS_FOLDER_PATH = os.getenv("RECORDS_FOLDER_PATH")

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# handler = logging.FileHandler('bot.log')
# handler.setLevel(logging.INFO)

# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)

# logger.addHandler(handler)

while True:
    # logger.info("Start of True.")
    try:
        response = requests.post(R5R_SERVERS_URL)
        servers = response.json().get("servers")
        # logger.info("Post succesfully.")

    except:  # noqa: E722
        print("Failed to send POST request.")
        servers = []
        # logger.info("Post failed.")

    hub = next(
        (
            server
            for server in servers
            if server["name"] == "[NA] MOVEMENT HUB - Test Release"
        ),
        [],
    )
    player_count = hub.get("playerCount", 0) if hub else "X"

    # logger.info(f"Server found: {hub}")

    try:
        # logger.info("Acessing files")
        files = [f for f in os.listdir(RECORDS_FOLDER_PATH) if f.endswith(".txt")]
        sorted_files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))

        to_be_added = defaultdict(list)

        for file in sorted_files:
            file_path = os.path.join(RECORDS_FOLDER_PATH, file)

            try:
                run = read_and_process_txt_file(f"{file_path}")
                # logger.info("Running read_and_process_txt_file")
                to_be_added[run[2]].append((run[0], run[1]))

            except Exception as e:
                print(f"Failed running read_and_process_txt_file. Error: {e}")
                # logger.info(f"Failed running read_and_process_txt_file. Error: {e}")
                continue
            
            # logger.info(f"To be Added: {to_be_added}")

            try:
                os.remove(file_path)

            except Exception as e:
                print(f"Error deleting a file. Error: {e}")

        try:                
            # logger.info("Starting to Rewrite info.json")
            with open ("info.json", "r") as file:
                info = json.load(file)
                
                for map, players in info.get("new_runs").items():
                    for player in players:
                        to_be_added["".join(map.lower().split())].append((player["player_name"], player["time_score"]))
            # logger.info(f"new data: {to_be_added}")

            with open("info.json", "w") as file:
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
                    },
                }

                json_string = json.dumps(data, indent=4)
                # logger.info(f"info.json content: {data}")
                file.write(json_string)

        except Exception as e:
            print(f"Error updating JSON file. Error: {e}")

    except Exception as e:
        # logger.info(f"Accessing files failed. {e}")
        print(f"Unexpected error in the main loop (1). Error: {e}")

    entries = {}

    try:
        for table in allowed_table_names:
            try:
                leaderboard = read_leaderboard(table)
                entries[table] = leaderboard

            except Exception as e:
                print(f"Failed to read leaderboard for table {table}. Error: {e}")
                continue

        try:
            update_top10_file(entries)

        except Exception as e:
            print(f"Failed to update top 10 file. Error: {e}")

        if not hub:
            os.system("taskkill /f /im r5apex_ds.exe")
            try:
                current_time = datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"Restarting HUB - {formatted_time}")
                os.chdir(os.path.dirname(R5R_SERVER_EXE))
                os.startfile(R5R_SERVER_EXE)

            except FileNotFoundError:
                print("File not found! Check the file path.")

            except Exception as e:
                print(f"Failed to restart HUB. Error: {e}")

    except Exception as e:
        print(f"Unexpected error in the main loop (2). Error: {e}")

    time.sleep(60)
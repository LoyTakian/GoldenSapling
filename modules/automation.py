import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from r5rIntegration import read_and_process_txt_file
from dbIntegration import read_leaderboard, allowed_table_names
from r5rIntegration import update_top10_file
from collections import defaultdict
import json

load_dotenv()
R5R_SERVER_EXE = os.getenv("R5R_SERVER_EXE")
R5R_SERVERS_URL = os.getenv("R5R_SERVERS_URL")
RECORDS_FOLDER_PATH = os.getenv("RECORDS_FOLDER_PATH")


def is_hub_running(server_list, server_name):
    for server in server_list:
        if server.get("name") == server_name:
            return True

    return False


while True:
    try:
        files = [f for f in os.listdir(RECORDS_FOLDER_PATH) if f.endswith(".txt")]
        sorted_files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))

        to_be_added = defaultdict(list)

        for file in sorted_files:
            file_path = os.path.join(RECORDS_FOLDER_PATH, file)
            
            try:
                run = read_and_process_txt_file(f"{file_path}")

            except Exception as e:
                print(f"Failed running read_and_process_txt_file. Error: {e}")
                continue
            
            to_be_added[run[2]].append((run[0], run[1]))


            try:
                os.remove(file_path)

            except Exception as e:
                print(f"Error deleting a file. Error: {e}")
        
        try:
            with open("info.json", "r+") as file:
                data = json.load(file)
                player_amount = data.get("players")

                new_data = {
                    "players": player_amount,
                    "new_runs": {
                        "First Map": [{"player_name": player[0],"time_score": player[1]} for player in to_be_added.get("firstmap", [])],
                        "Gym Map": [{"player_name": player[0],"time_score": player[1]} for player in to_be_added.get("gymmap", [])],
                        "Mantle Jump Map": [{"player_name": player[0],"time_score": player[1]} for player in to_be_added.get("mantlejumpmap", [])]
                        }
                }

                file.seek(0)
                json_string = json.dumps(new_data, indent=4)
                file.write(json_string)
                file.truncate()
        except Exception as e:
            print(f"Error updating JSON file. Error: {e}")
    
    except Exception as e:
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

        try:
            response = requests.post(R5R_SERVERS_URL)

        except Exception as e:
            print(f"Failed to send POST request. Error: {e}")

        if response.status_code == 200:
            try:
                json_response = response.json()

            except Exception as e:
                print(f"Failed to parse JSON response. Error: {e}")
                continue

        if json_response and not is_hub_running(
            json_response.get("servers", []), "[NA] MOVEMENT HUB - Test Release"
        ):
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

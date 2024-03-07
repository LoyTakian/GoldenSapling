import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from r5rIntegration import read_and_process_txt_file
from dbIntegration import read_leaderboard, allowed_table_names
from r5rIntegration import update_top10_file

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
    files = [f for f in os.listdir(RECORDS_FOLDER_PATH) if f.endswith(".txt")]
    sorted_files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))

    for file in sorted_files:
        file_path = os.path.join(RECORDS_FOLDER_PATH, file)
        read_and_process_txt_file(f"{file_path}")

        os.remove(file_path)

    entries = {}

    for table in allowed_table_names:
        leaderboard = read_leaderboard(table)
        entries[table] = leaderboard

    update_top10_file(entries)

    response = requests.post(R5R_SERVERS_URL)

    if response.status_code == 200:
        try:
            json_response = response.json()
        except:
            print(f"Response error! ***{response}***")

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

    time.sleep(60)

import os
import time
from dotenv import load_dotenv
from r5rIntegration import read_and_process_txt_file
from dbIntegration import read_leaderboard, allowed_table_names
from r5rIntegration import update_top3_file

load_dotenv()
RECORDS_FOLDER_PATH = os.getenv('RECORDS_FOLDER_PATH')


while True:
    files = [f for f in os.listdir(RECORDS_FOLDER_PATH) if f.endswith('.txt')]

    for file in files:
        file_path = os.path.join(RECORDS_FOLDER_PATH, file)
        read_and_process_txt_file(f"{file_path}")

        os.remove(file_path)

    entries = {}

    for table in allowed_table_names:
        leaderboard = read_leaderboard(table)[:3]
        entries[table] = leaderboard

    update_top3_file(entries)

    time.sleep(60)

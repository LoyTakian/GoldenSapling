import os
from dotenv import load_dotenv
from modules.dbIntegration import insert_into_db, allowed_table_names, timer_converter

load_dotenv()
TOP3_FOLDER_PATH = os.getenv("TOP3_FOLDER_PATH")


def read_and_process_txt_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
        record = content.split("!@#$%THISISTHEIRDATA!@#$%:")
        if len(record) == 3:
            player_name = record[0]
            time_score = record[1]
            table_name = record[2]

            if table_name in allowed_table_names:
                insert_into_db(player_name, time_score, table_name)

                return (player_name, time_score, table_name)

            else:
                print("Error executing read_and_process_txt_file...")


def update_top10_file(entries):
    top_10 = []

    FM1Name, FM1Time = _get_entry_data(entries, "firstmap", 0)
    FM2Name, FM2Time = _get_entry_data(entries, "firstmap", 1)
    FM3Name, FM3Time = _get_entry_data(entries, "firstmap", 2)

    MJM1Name, MJM1Time = _get_entry_data(entries, "mantlejumpmap", 0)
    MJM2Name, MJM2Time = _get_entry_data(entries, "mantlejumpmap", 1)
    MJM3Name, MJM3Time = _get_entry_data(entries, "mantlejumpmap", 2)

    GM1Name, GM1Time = _get_entry_data(entries, "gymmap", 0)
    GM2Name, GM2Time = _get_entry_data(entries, "gymmap", 1)
    GM3Name, GM3Time = _get_entry_data(entries, "gymmap", 2)

    for map in allowed_table_names:
        for player, _ in entries.get(map, []):
            top_10.append(player)

    top_10 = list(set(top_10))

    with open(f"{TOP3_FOLDER_PATH}/_mh_leaderboards.nut", "w") as file:
        file.write("untyped\n\n")

        file.write("globalize_all_functions\n\n")

        file.write(
            f'global const array <string> top3_players = ["{GM1Name}","{GM2Name}","{GM3Name}","{MJM1Name}","{MJM2Name}","{MJM3Name}","{FM1Name}","{FM2Name}","{FM3Name}"]\n'
        )
        file.write("global const array <string> top10_players = [")
        file.write(", ".join(f'"{player}"' for player in top_10))
        file.write("]\n\n")

        file.write("void function MH_Spawn_Leadeboards(entity player) {\n")
        file.write(
            f'	CreatePanelText(player, "{GM1Name} - {timer_converter(GM1Time)[0]}:{timer_converter(GM1Time)[1]}", "#1", < 878.8, 0.0105, 40643.5 >, < 0, 0.0007, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player, "{GM2Name} - {timer_converter(GM2Time)[0]}:{timer_converter(GM2Time)[1]}", "#2", < 878.8, 0.0105, 40593.5 >, < 0, 0.0007, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player, "{GM3Name} - {timer_converter(GM3Time)[0]}:{timer_converter(GM3Time)[1]}", "#3", < 878.8, 0.0105, 40543.5 >, < 0, 0.0007, 0 >, false, 1 )\n\n'
        )

        file.write(
            f'	CreatePanelText(player, "{MJM1Name} - {timer_converter(MJM1Time)[0]}:{timer_converter(MJM1Time)[1]}", "#1", < -878.8, -0.0052, 40643.5 >, < 0, -179.9997, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player, "{MJM2Name} - {timer_converter(MJM2Time)[0]}:{timer_converter(MJM2Time)[1]}", "#2", < -878.8, -0.0052, 40593.5 >, < 0, -179.9997, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player, "{MJM3Name} - {timer_converter(MJM3Time)[0]}:{timer_converter(MJM3Time)[1]}", "#3", < -878.8, -0.0052, 40543.5 >, < 0, -179.9997, 0 >, false, 1 )\n\n'
        )

        file.write(
            f'	CreatePanelText(player, "{FM1Name} - {timer_converter(FM1Time)[0]}:{timer_converter(FM1Time)[1]}", "#1", < 0.0026, -878.8, 40643.5 >, < 0, -89.9998, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player, "{FM2Name} - {timer_converter(FM2Time)[0]}:{timer_converter(FM2Time)[1]}", "#2", < 0.0026, -878.8, 40593.5 >, < 0, -89.9998, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player, "{FM3Name} - {timer_converter(FM3Time)[0]}:{timer_converter(FM3Time)[1]}", "#3", < 0.0026, -878.8, 40543.5 >, < 0, -89.9998, 0 >, false, 1 )\n\n'
        )

        file.write("}\n")


def _get_entry_data(entries, map_name, position):
    try:
        name, time = entries[map_name][position]
        time = int(time)
    except (KeyError, IndexError):
        name, time = "EMPTY", 0
    return name, time

import os
from dotenv import load_dotenv
from dbIntegration import insert_into_db, allowed_table_names, timer_converter


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

    IH1Name, IH1Time = _get_entry_data(entries, "ithurtsmap", 0)
    IH2Name, IH2Time = _get_entry_data(entries, "ithurtsmap", 1)
    IH3Name, IH3Time = _get_entry_data(entries, "ithurtsmap", 2)

    SI1Name, SI1Time = _get_entry_data(entries, "strafeitmap", 0)
    SI2Name, SI2Time = _get_entry_data(entries, "strafeitmap", 1)
    SI3Name, SI3Time = _get_entry_data(entries, "strafeitmap", 2)

    for map in allowed_table_names:
        for player, _ in entries.get(map, []):
            top_10.append(player)

    top_10 = list(set(top_10))

    with open(f"{TOP3_FOLDER_PATH}_mh_leaderboards.nut", "w") as file:
        file.write("untyped\n\n")

        file.write("globalize_all_functions\n\n")

        file.write(
            f'global const array <string> top3_players = ["{GM1Name}","{GM2Name}","{GM3Name}","{MJM1Name}","{MJM2Name}","{MJM3Name}","{FM1Name}","{FM2Name}","{FM3Name}", "{IH1Name}", "{IH2Name}", "{IH3Name}", "{SI1Name}", "{SI2Name}", "{SI3Name}"]\n'
        )
        file.write("global const array <string> top10_players = [")
        file.write(", ".join(f'"{player}"' for player in top_10))
        file.write("]\n\n")

        file.write("void function MH_Spawn_Leaderboards(entity player) {\n")
        file.write(
            f'	CreatePanelText(player,"{GM1Name} - {timer_converter(GM1Time)[0]}:{timer_converter(GM1Time)[1]}", "#1", < 879, 0, 40643.5 >, < 0, 0, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player,"{GM2Name} - {timer_converter(GM2Time)[0]}:{timer_converter(GM2Time)[1]}", "#2", < 879, 0, 40593.5 >, < 0, 0, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player,"{GM3Name} - {timer_converter(GM3Time)[0]}:{timer_converter(GM3Time)[1]}", "#3", < 879, 0, 40543.5 >, < 0, 0, 0 >, false, 1 )\n\n'
        )
        file.write(
            f'	CreatePanelText(player,"{SI1Name} - {timer_converter(SI1Time)[0]}:{timer_converter(SI1Time)[1]}", "#1", < -879, 0, 40643.5 >, < 0, -180, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player,"{SI2Name} - {timer_converter(SI2Time)[0]}:{timer_converter(SI2Time)[1]}", "#2", < -879, 0, 40593.5 >, < 0, -180, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player,"{SI3Name} - {timer_converter(SI3Time)[0]}:{timer_converter(SI3Time)[1]}", "#3", < -879, 0, 40543.5 >, < 0, -180, 0 >, false, 1 )\n\n'
        )
        file.write(
            f'	CreatePanelText(player,"{FM1Name} - {timer_converter(FM1Time)[0]}:{timer_converter(FM1Time)[1]}", "#1", < 0, -879, 40643.5 >, < 0, -90, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player,"{FM2Name} - {timer_converter(FM2Time)[0]}:{timer_converter(FM2Time)[1]}", "#2", < 0, -879, 40593.5 >, < 0, -90, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player,"{FM3Name} - {timer_converter(FM3Time)[0]}:{timer_converter(FM3Time)[1]}", "#3", < 0, -879, 40543.5 >, < 0, -90, 0 >, false, 1 )\n\n'
        )
        file.write(
            f'	CreatePanelText(player,"{IH1Name} - {timer_converter(IH1Time)[0]}:{timer_converter(IH1Time)[1]}", "#1", < 0, 879, 40643.5 >, < 0, 90, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player,"{IH2Name} - {timer_converter(IH2Time)[0]}:{timer_converter(IH2Time)[1]}", "#2", < 0, 879, 40593.5 >, < 0, 90, 0 >, false, 1 )\n'
        )
        file.write(
            f'	CreatePanelText(player,"{IH3Name} - {timer_converter(IH3Time)[0]}:{timer_converter(IH3Time)[1]}", "#3", < 0, 879, 40543.5 >, < 0, 90, 0 >, false, 1 )\n\n'
        )

        file.write("}\n")


def _get_entry_data(entries, map_name, position):
    try:
        name, time = entries[map_name][position]
        time = int(time)
    except (KeyError, IndexError):
        name, time = "EMPTY", 0
    return name, time

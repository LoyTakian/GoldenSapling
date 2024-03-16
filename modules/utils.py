from discord import SelectOption, Interaction, utils
from discord.ui import Select, View
import json


class RoleSelectView(View):
    def __init__(self, roleClass):
        super().__init__()
        self.add_item(roleClass())


class RoleSelectPlatform(Select):
    def __init__(self):
        options = [
            SelectOption(label="PC", emoji="💻", description="If you are based"),
            SelectOption(label="Xbox", emoji="❎", description="If you stinky poopoo"),
            SelectOption(
                label="Playstation", emoji="🎮", description="if you poopoo stink"
            ),
            SelectOption(
                label="Switch",
                emoji="💀",
                description="What are you doing with your life?",
            ),
        ]

        super().__init__(
            placeholder="Get your platform role",
            min_values=1,
            max_values=4,
            options=options,
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        for role_name in ["PC", "Xbox", "Playstation", "Switch"]:
            role = utils.get(interaction.guild.roles, name=role_name)

            if role is None:
                continue

            if role_name in self.values:
                if role not in interaction.user.roles:
                    await interaction.user.add_roles(role)
            else:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)

        await interaction.followup.send("Roles added!", ephemeral=True)
        return


class RoleSelectContent(Select):
    def __init__(self):
        options = [
            SelectOption(
                label="Stream Ping",
                emoji="🟣",
                description="Gets notified whenever Treeree starts a stream",
            ),
            SelectOption(
                label="Video Ping",
                emoji="🔴",
                description="Gets notified whenever Treeree posts a video (never)",
            ),
        ]

        super().__init__(
            placeholder="Get your content notification role",
            min_values=1,
            max_values=2,
            options=options,
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        for role_name in ["Stream Ping", "Video Ping"]:
            role = utils.get(interaction.guild.roles, name=role_name)

            if role is None:
                continue

            if role_name in self.values:
                if role not in interaction.user.roles:
                    await interaction.user.add_roles(role)
            else:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)

        await interaction.followup.send("Roles added!", ephemeral=True)
        return


class RoleSelectExtra(Select):
    def __init__(self):
        options = [
            SelectOption(
                label="Jay Ping",
                emoji="🤓",
                description="Gets notified whenever JayTheYggrasil starts a stream",
            ),
            SelectOption(
                label="Beta Tester",
                emoji="👁️",
                description="Get notified whenever we do something in R5 Reloaded",
            ),
        ]

        super().__init__(
            placeholder="Get your extra role",
            min_values=1,
            max_values=2,
            options=options,
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        for role_name in ["Jay Ping", "Beta Tester"]:
            role = utils.get(interaction.guild.roles, name=role_name)

            if role is None:
                continue

            if role_name in self.values:
                if role not in interaction.user.roles:
                    await interaction.user.add_roles(role)
            else:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)

        await interaction.followup.send("Roles added!", ephemeral=True)
        return


def is_spammer(message, moderator_roles):
    author_roles = {role.id for role in message.author.roles}

    if moderator_roles.intersection(author_roles):
        return False

    return True


def time_to_seconds(time_str):
    try:
        minutes, seconds = map(int, time_str.split(":"))
        total_seconds = minutes * 60 + seconds
        return total_seconds
    except ValueError:
        print("Invalid time format. Please use 'min:sec' format.")


def seconds_to_time(time_str):
    minutes, seconds = divmod(int(time_str), 60)
    return f"{int(minutes):02d}", f"{int(seconds):02d}"


def log_runs_table(players):
    table = "```ansi\n"
    table += (
        "[2;45m[2;37m {:<23} {:<9}[0m[2;45m[0m[2;45m[2;37m[0m[2;45m[0m\n".format(
            "Username", "New Time"
        )
    )
    for idx, player in enumerate(players, start=1):
        time_score = seconds_to_time(player.get("time_score"))
        time_score = f"{time_score[0]}:{time_score[1]}"
        if idx % 2 == 0:
            table += "[2;45m[2;37m[2;47m[2;30m {:<26} {} [0m[2;37m[2;47m[0m[2;37m[2;45m[0m[2;45m[0m[2;45m[2;37m[0m[2;45m[0m\n".format(
                player.get("player_name")[:20], time_score
            )
        else:
            table += "[2;40m {:<26} {} \n[0m".format(
                player.get("player_name")[:20], time_score
            )
    table += "```"

    return table


def reset_info_file(players):
    data = {
        "players": players,
        "new_runs": {"First Map": [], "Gym Map": [], "Mantle Jump Map": []},
    }

    json_string = json.dumps(data, indent=4)

    with open("info.json", "w") as f:
        f.write(json_string)


def table_constructor(leaderboard):
    table = "```ansi\n"
    table += (
        "[2;45m[2;37m{:<5} {:<20}  {:<10}[0m[2;45m[0m[2;45m[2;37m[0m[2;45m[0m\n".format(
            "Rank", "Username", "Best Time"
        )
    )
    for idx, (player_name, time_score) in enumerate(leaderboard, start=1):
        time_score = seconds_to_time(time_score)
        time_score = f"{time_score[0]}:{time_score[1]}"
        if idx % 2 == 0:
            table += "[2;45m[2;37m[2;47m[2;30m{:<5} {:<26} {}[0m[2;37m[2;47m[0m[2;37m[2;45m[0m[2;45m[0m[2;45m[2;37m[0m[2;45m[0m\n".format(
                idx, player_name[:20], time_score
            )
        else:
            table += "[2;40m{:<5} {:<26} {}\n[0m".format(
                idx, player_name[:20], time_score
            )
    table += "```"

    return table


help_message = """**:heartpulse: ABOUT :heartpulse:**
Hey, I'm a bot made by @loy_ and my purpose is to be of service in Treeree's discord server.
For now I  can:
* Help with banning spammers that uses `@everyone` and `@here`
* Help with providing better embeds for twitter links
* Provide up-to-date information about our **Movement HUB** R5 reloaded server

**:star: LIST OF COMMANDS :star:**
```ansi
[1;2m[1;2m[1;2m[1;31m[1;37m[1;37m[1;40m/leaderboard[0m[1;37m[0m[1;37m[0m[1;31m[0m[0m[0m[0m:
This command is utilized within movement map posts to display the top 10 fastest players on that specific map.
```
```ansi
[2;37m[2;40m[0m[2;37m[0m[1;2m[1;2m[1;40m[1;37m[1;40m[1;37m[0m[1;37m[1;40m[0m[1;37m[1;40m[0m[1;40m[0m[0m[0m[2;42m[2;37m[2;40m[2;37m[1;37m[1;40m[1;37m/personal_best [1;31m[1;40mNICKNAME[0m[1;31m[1;40m[0m[1;37m[1;40m:[0m[1;37m[1;40m[0m[1;37m[1;40m[0m[2;37m[2;40m[0m[2;37m[2;40m[0m[2;37m[2;42m
[0m[2;42m[0mThis command is utilized within movement map posts to display the top 10 fastest runs of a specified player on that specific map.
(the NICKNAME is case-sensitive.)
```
**:warning: The bot can take up to 1 minute to update with new info, be patient! :warning:**"""

leaderboard_message = """# LEADERBOARDS
:white_check_mark: Check your times by sending ``/personal_best`` on the map posts. :white_check_mark:
⚠️ The bot can take up to 1 minute to update with new info, be patient! ⚠️"""

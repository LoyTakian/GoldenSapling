import os
import re
import discord
import datetime
from discord.ext import tasks
from dotenv import load_dotenv
from modules.dbIntegration import (
    read_leaderboard,
    read_personal_best,
    table_constructor,
)


load_dotenv()
TOKEN = os.getenv("TOKEN")
LEADERBOARD_MESSAGE_ID = int(os.getenv("LEADERBOARD_MESSAGE_ID"))
LEADERBOARD_CHANNEL_ID = int(os.getenv("LEADERBOARD_CHANNEL_ID"))
LEADERBOARD_FIRSTMAP_ID = int(os.getenv("LEADERBOARD_FIRSTMAP_ID"))
LEADERBOARD_GYMMAP_ID = int(os.getenv("LEADERBOARD_GYMMAP_ID"))
LEADERBOARD_MANTLEJUMPMAP_ID = int(os.getenv("LEADERBOARD_MANTLEJUMPMAP_ID"))
TWITTER_PATTERN = r"https://twitter\.com/(\S+)"
X_PATTERN = r"https://x\.com/(\S+)"
MODERATOR_ROLES_ID = {839992880314974209, 839992880314974208, 839992880302653458}

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f"Bot {self.user} is ready.")
        self.update_leaderboard.start()

    async def on_message(self, message):
        if message.author == client.user:
            return

        if "@everyone" in message.content or "@here" in message.content:
            author_roles = {role.id for role in message.author.roles}
            if MODERATOR_ROLES_ID.intersection(author_roles):
                return
            else:
                try:
                    await message.guild.ban(
                        message.author,
                        reason="Sent @ everyone, Probably a hacked account.",
                        delete_message_days=7,
                    )

                    now = datetime.datetime.now()
                    print(
                        f"{message.author} was banned for using @everyone on {now.strftime('%Y-%m-%d %H:%M:%S')}."
                    )
                except discord.Forbidden:
                    print("I do not have permission to ban.")
                except discord.HTTPException:
                    print("Banning failed.")

        # Regular expression pattern to match Twitter links
        twitter_pattern = TWITTER_PATTERN
        x_pattern = X_PATTERN

        # Check if the message contains a Twitter link
        match = re.search(twitter_pattern, message.content)
        match2 = re.search(x_pattern, message.content)

        if match or match2:
            # Extract the Twitter username
            url_content = match2.group(1) if match2 else match.group(1)

            # Modify the URL by adding "vx" before "twitter"
            modified_url = f"{message.author.mention}, here's a better version of the link: https://vxtwitter.com/{url_content}"

            # Send the modified URL
            await message.channel.send(modified_url)

    @tasks.loop(seconds=60)
    async def update_leaderboard(self):
        channel = self.get_channel(LEADERBOARD_CHANNEL_ID)
        mjm = read_leaderboard("mantlejumpmap")
        fm = read_leaderboard("firstmap")
        gm = read_leaderboard("gymmap")

        mjm = (
            table_constructor(mjm)
            or "```ansi\n[2;41m[2;30m[0m[2;41m[0m[2;41m[2;30m[2;37m[1;37m[4;37mNO SUBMISSIONS[0m[1;37m[1;41m[0m[2;37m[2;41m[0m[2;30m[2;41m[0m[2;41m[0m```"
        )
        fm = (
            table_constructor(fm)
            or "```ansi\n[2;41m[2;30m[0m[2;41m[0m[2;41m[2;30m[2;37m[1;37m[4;37mNO SUBMISSIONS[0m[1;37m[1;41m[0m[2;37m[2;41m[0m[2;30m[2;41m[0m[2;41m[0m```"
        )
        gm = (
            table_constructor(gm)
            or "```ansi\n[2;41m[2;30m[0m[2;41m[0m[2;41m[2;30m[2;37m[1;37m[4;37mNO SUBMISSIONS[0m[1;37m[1;41m[0m[2;37m[2;41m[0m[2;30m[2;41m[0m[2;41m[0m```"
        )

        try:
            leaderboard_message = await channel.fetch_message(LEADERBOARD_MESSAGE_ID)
            answer = f"""# LEADERBOARDS
:white_check_mark:  Check your times by sending ``/personal_best`` on the map posts.
:warning: The bot can take up to 1 minute to update with new info, be patient!"""

            if answer != leaderboard_message.content:
                await leaderboard_message.edit(content=answer)

        except discord.NotFound:
            print("Leaderboard message not found or unable to access")

        try:
            leaderboard_firstmap_message = await channel.fetch_message(
                LEADERBOARD_FIRSTMAP_ID
            )
            answer = f"""### First Map
{fm}
post: https://discord.com/channels/839992880293478400/1100536422450073690"""

            if len(answer) >= 1800:
                print(f"fm length: {len(answer)}")

            if answer != leaderboard_firstmap_message.content:
                await leaderboard_firstmap_message.edit(content=answer)

        except discord.NotFound:
            print("Leaderboard message not found or unable to access")

        try:
            leaderboard_gymmap_message = await channel.fetch_message(
                LEADERBOARD_GYMMAP_ID
            )
            answer = f"""### Gym Map
{gm}
post: https://discord.com/channels/839992880293478400/1180733536676880396"""

            if len(answer) >= 1800:
                print(f"gm length: {len(answer)}")

            if answer != leaderboard_gymmap_message.content:
                await leaderboard_gymmap_message.edit(content=answer)

        except discord.NotFound:
            print("Leaderboard message not found or unable to access")

        try:
            leaderboard_mantlejumpmap_message = await channel.fetch_message(
                LEADERBOARD_MANTLEJUMPMAP_ID
            )
            answer = f"""### Mantle Jump Map
{mjm}
post: https://discord.com/channels/839992880293478400/1123705203015827597"""

            if len(answer) >= 1800:
                print(f"mjm length: {len(answer)}")

            if answer != leaderboard_mantlejumpmap_message.content:
                await leaderboard_mantlejumpmap_message.edit(content=answer)

        except discord.NotFound:
            print("Leaderboard message not found or unable to access")


client = aclient()
tree = discord.app_commands.CommandTree(client)


@tree.command(
    name="leaderboard",
    description="Returns the top 10 scoreboard for a specific movement map.",
)
async def self(interaction: discord.Interaction):
    channel_name = interaction.channel.name
    leaderboard = []
    map_name = "INVALID"

    match channel_name:
        case "Mantle Jump Map":
            map_name = "Mantle Jump Map"
            leaderboard = read_leaderboard("mantlejumpmap")
        case "Doorbounce Map":
            map_name = "Doorbounce Map"
            leaderboard = read_leaderboard("doorbouncemap")
        case "First Map":
            map_name = "First Map"
            leaderboard = read_leaderboard("firstmap")
        case "Gym Map":
            map_name = "Gym Map"
            leaderboard = read_leaderboard("gymmap")
        case _:
            await interaction.response.send_message(
                f"**{channel_name}** doesn't have a leaderboard."
            )
            return

    answer = f"**{map_name.upper()} LEADERBOARD**\n"

    # If there's no one in the leaderboard
    if len(leaderboard) <= 0:
        answer += "```ansi\n"
        answer += "[2;41m[2;30m[0m[2;41m[0m[2;41m[2;30m[2;37m[1;37m[4;37mNO SUBMISSIONS[0m[1;37m[1;41m[0m[2;37m[2;41m[0m[2;30m[2;41m[0m[2;41m[0m"
        answer += "```"
        await interaction.response.send_message(answer)
        return

    # If there's at least 1 player in the leaderboard
    else:
        answer += table_constructor(leaderboard)
        await interaction.response.send_message(answer)


@tree.command(name="hello", description="Greets the user.")
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hello! I'm a bot made by loy_ and my purpose is to serve Treeree's server! For more info send /help"
    )


@tree.command(name="help", description="Returns info about this bot.")
async def self(interaction: discord.Integration):
    answer = f"**⭐ LIST OF COMMANDS ⭐**\n"
    answer += "```ansi\n"
    answer += """[1;2m[1;2m[1;2m[1;31m[1;37m[1;37m[1;40m/leaderboard[0m[1;37m[0m[1;37m[0m[1;31m[0m[0m[0m[0m:
Using this command in the movement maps posts will return you a top 10 fastest runs of that specific map, if it has one.


[2;37m[2;40m[0m[2;37m[0m[1;2m[1;2m[1;40m[1;37m[1;40m[1;37m[0m[1;37m[1;40m[0m[1;37m[1;40m[0m[1;40m[0m[0m[0m[2;42m[2;37m[2;40m[2;37m[1;37m[1;40m[1;37m/personal_best [1;31m[1;40m<nickname>[0m[1;31m[1;40m[0m[1;37m[1;40m:[0m[1;37m[1;40m[0m[1;37m[1;40m[0m[2;37m[2;40m[0m[2;37m[2;40m[0m[2;37m[2;42m
[0m[2;42m[0mUsing this command in the movement maps posts will return you the top 10 fastest runs of that specific player in that specific map, if it has one."""
    answer += "```\n"
    answer += "⚠️ The bot can take up to 1 minute to update with new info, be patient!"
    await interaction.response.send_message(answer)


@tree.command(
    name="personal_best",
    description="Returns 10 quickest times of a specific player for a specific movement map.",
)
async def self(interaction: discord.Integration, player_name: str):
    channel_name = interaction.channel.name
    leaderboard = []
    map_name = "INVALID"

    if len(player_name) <= 0 or player_name == "":
        await interaction.response.send_message(f"**Player nickname cannot be empty.**")
        return

    match channel_name:
        case "Mantle Jump Map":
            map_name = "Mantle Jump Map"
            leaderboard = read_personal_best(player_name, "mantlejumpmap")
        case "Doorbounce Map":
            map_name = "Doorbounce Map"
            leaderboard = read_personal_best(player_name, "doorbouncemap")
        case "First Map":
            map_name = "First Map"
            leaderboard = read_personal_best(player_name, "firstmap")
        case "Gym Map":
            map_name = "Gym Map"
            leaderboard = read_personal_best(player_name, "gymmap")
        case _:
            await interaction.response.send_message(
                f"**{channel_name}** doesn't have a leaderboard."
            )
            return

    answer = f"**{map_name.upper()} PERSONAL BEST**\n"
    # If there's no one in the leaderboard
    if len(leaderboard) <= 0:
        answer += "```ansi\n"
        answer += f"[2;41m[2;30m[0m[2;41m[0m[2;41m[2;30m[2;37m[1;37m[4;37m{player_name} HAS NO SUBMISSIONS[0m[1;37m[1;41m[0m[2;37m[2;41m[0m[2;30m[2;41m[0m[2;41m[0m"
        answer += "```"
        await interaction.response.send_message(answer)
        return

    # If there's at least 1 player in the leaderboard
    else:
        answer += table_constructor(leaderboard)
        await interaction.response.send_message(answer)


client.run(TOKEN)

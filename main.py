from modules import utils, dbIntegration
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime
import discord
import json
import os
import re

load_dotenv()
TOKEN = os.getenv("TOKEN")
ROLES_CHANNEL_ID = int(os.getenv("ROLES_CHANNEL_ID"))
MODERATOR_ROLES_ID = {int(id) for id in os.getenv("MODERATOR_ROLES_ID").split(",")}
LEADERBOARD_CHANNEL_ID = int(os.getenv("LEADERBOARD_CHANNEL_ID"))
PLAYERS_ONLINE_CHANNEL_ID = int(os.getenv("PLAYERS_ONLINE_CHANNEL_ID"))
LEADERBOARD_MESSAGE_ID = int(os.getenv("LEADERBOARD_MESSAGE_ID"))
LEADERBOARD_FIRSTMAP_ID = int(os.getenv("LEADERBOARD_FIRSTMAP_ID"))
LEADERBOARD_GYMMAP_ID = int(os.getenv("LEADERBOARD_GYMMAP_ID"))
LEADERBOARD_MANTLEJUMPMAP_ID = int(os.getenv("LEADERBOARD_MANTLEJUMPMAP_ID"))
LEADERBOARD_ITHURTSMAP_ID = int(os.getenv("LEADERBOARD_ITHURTSMAP_ID"))
LEADERBOARD_STRAFEIT_ID = int(os.getenv("LEADERBOARD_STRAFEIT_ID"))
PLATFORM_ROLE_MESSAGE_ID = int(os.getenv("PLATFORM_ROLE_MESSAGE_ID"))
CONTENT_ROLE_MESSAGE_ID = int(os.getenv("CONTENT_ROLE_MESSAGE_ID"))
EXTRA_ROLE_MESSAGE_ID = int(os.getenv("EXTRA_ROLE_MESSAGE_ID"))
NEW_RUNS_CHANNEL_ID = int(os.getenv("NEW_RUNS_CHANNEL_ID"))
MAP_NAMES = ["Mantle Jump Map", "Doorbounce Map", "First Map", "Gym Map", "It Hurts Map", "Strafe It Map"]
TWITTER_PATTERN = r"https://twitter\.com/(\S+)"
X_PATTERN = r"https://x\.com/(\S+)"
REDDIT_PATTERN = r"https://www\.reddit\.com/r/(\S+)"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)


@bot.slash_command(
    guid_ids=[839992880293478400],
    description="Returns information about the functionalities of this bot.",
)
async def help(ctx):
    await ctx.response.send_message(utils.help_message)
    return


@bot.slash_command(
    guid_ids=[839992880293478400],
    description="Returns the top 10 fastest players for a specific movement map.",
)
async def leaderboard(ctx):
    channel_name = ctx.channel.name
    leaderboard = []

    if channel_name in MAP_NAMES:
        leaderboard = dbIntegration.read_leaderboard(
            ("".join(channel_name.lower().split()))
        )

    if len(leaderboard) <= 0:
        await ctx.response.send_message(
            f"**{channel_name}** doesn't have a leaderboard or it is empty."
        )
        return

    else:
        answer = f"**{channel_name.upper()} LEADERBOARD**\n"
        answer += dbIntegration.table_constructor(leaderboard)

        await ctx.response.send_message(answer)
    return


@bot.slash_command(
    guid_ids=[839992880293478400],
    description="Returns 10 fastest runs of a specific player for a specific movement map.",
)
async def personal_best(ctx, player_name: str):
    channel_name = ctx.channel.name
    leaderboard = []

    if len(player_name) <= 0:
        await ctx.response.send_message("**Player nickname** cannot be empty.")
        return

    elif channel_name not in MAP_NAMES:
        await ctx.response.send_message(
            f"**{channel_name}** doesn't have a leaderboard or it is empty."
        )
        return

    else:
        leaderboard = dbIntegration.read_personal_best(
            player_name, "".join(channel_name.lower().split())
        )

        if len(leaderboard) <= 0:
            await ctx.response.send_message(
                f"**{player_name}** doesn't have any submission on **{channel_name}**."
            )
            return

        else:
            answer = f"**{player_name}** personal best times in **{channel_name.upper()}**\n"
            answer += utils.table_constructor(leaderboard)

            await ctx.response.send_message(answer)
            return


@bot.slash_command(
    guid_ids=[839992880293478400],
    description="Returns the total amount of completed runs of a specific player for a specific movement map.",
)
async def personal_total_runs(ctx, player_name: str):
    channel_name = ctx.channel.name

    if len(player_name) <= 0:
        await ctx.response.send_message("**Player nickname** cannot be empty.")
        return

    elif channel_name not in MAP_NAMES:
        await ctx.response.send_message(
            f"**{channel_name}** doesn't have a leaderboard or it is empty."
        )
        return

    else:
        leaderboard = dbIntegration.read_personal_best(
            player_name, "".join(channel_name.lower().split())
        )

        if len(leaderboard) <= 0:
            await ctx.response.send_message(
                f"**{player_name}** doesn't have any submission on **{channel_name}**."
            )
            return

        else:
            rank, run_amount = dbIntegration.read_personal_total(
                player_name, "".join(channel_name.lower().split())
            )
            answer = utils.table_constructor_total_runs( rank, player_name, run_amount)

            await ctx.response.send_message(answer)
            return


@bot.command(name="add")
async def add_to_db(
    ctx,
    player_name: str = "empty",
    time_score: str = "empty",
    table_name: str = "empty",
):
    if any(x == "empty" for x in [player_name, time_score, table_name]):
        await ctx.reply("usage: >add `player_name` time_score table_name")
        return

    elif ctx.message.author.id != 192774874077331465:
        await ctx.reply("Nice try, jackass! Only Loy can use this command.")
        return

    elif not player_name[0] == "`" or not player_name[-1] == "`":
        await ctx.reply("player_name format, make sure to envelop the variable in `.")
        return

    elif not re.fullmatch(r"^\d+:\d{2}$", time_score):
        await ctx.reply("Wrong time format, the correct format is: `min:sec`.")
        return

    elif table_name not in [
        "".join(map_name.lower().split()) for map_name in MAP_NAMES
    ]:
        await ctx.reply(
            "Wrong table name. Tables available: mantlejumpmap, firstmap, gymmap, doorbouncemap, ithurtsmap, strafeitmap"
        )

    else:
        player_name = player_name[1:-1]
        seconds = utils.time_to_seconds(time_score)
        dbIntegration.insert_into_db(player_name, seconds, table_name)

        await ctx.reply(f"New entry: `{player_name}` ({seconds}) - {table_name}")
        return


@bot.command(name="remove")
async def remove_from_db(
    ctx,
    player_name: str = "empty",
    time_score: str = "empty",
    table_name: str = "empty",
):
    if any(x == "empty" for x in [player_name, time_score, table_name]):
        await ctx.reply("usage: >remove `player_name` time_score table_name")
        return

    elif ctx.message.author.id != 192774874077331465:
        await ctx.reply("Nice try, jackass! Only Loy can use this command.")
        return

    elif not player_name[0] == "`" or not player_name[-1] == "`":
        await ctx.reply("player_name format, make sure to envelop the variable in `.")
        return

    elif not re.fullmatch(r"^\d+:\d{2}$", time_score):
        await ctx.reply("Wrong time format, the correct format is: `min:sec`.")
        return

    elif table_name not in [
        "".join(map_name.lower().split()) for map_name in MAP_NAMES
    ]:
        await ctx.reply(
            "Wrong table name. Tables available: mantlejumpmap, firstmap, gymmap, doorbouncemap, ithurtsmap, strafeitmap"
        )
        return

    else:
        player_name = player_name[1:-1]
        seconds = utils.time_to_seconds(time_score)
        dbIntegration.delete_from_db(player_name, seconds, table_name)

        await ctx.reply(f"Deleted: `{player_name}` ({seconds}) - {table_name}")
        return


@bot.command(name="swap_nick")
async def swap_nick(ctx, old_nick: str = "empty", new_nick: str = "empty"):

    failures = []
    success = []
    if any(x == "empty" for x in [old_nick, new_nick]):
        await ctx.reply("usage: >swap_nick `old_nickname` `new_nickname`")
        return
    
    elif not old_nick[0] == "`" or not old_nick[-1] == "`":
        await ctx.reply("Make sure to envelop the old nick in `.")
        return

    elif not new_nick[0] == "`" or not new_nick[-1] == "`":
        await ctx.reply("Make sure to envelop the old nick in `.")
        return

    elif ctx.message.author.id != 192774874077331465:
        await ctx.reply("Nice try, jackass! Only Loy can use this command.")
        return
    
    for map_name in MAP_NAMES:
        table = "".join(map_name.lower().split())

        if dbIntegration.change_nickname_in_db(old_nick[1:-1], new_nick[1:-1], table):
            success.append(map_name)
        else:
            failures.append(map_name)

    if len(failures) > 0:
        await ctx.reply(f"""
Failed to update nick for the maps: {', '.join(failures)}
Successfully updated nick for the maps: {', '.join(success)}
""")
        return
    
    else:
        await ctx.reply(f"Nickname updated from `{old_nick}` to `{new_nick}` successfully.")


@bot.command(name="placeholder")
async def empty(ctx):
    channel = bot.get_channel(ctx.channel.id)
    if channel:
        await channel.send("placeholder message")
    return


# @bot.event
async def on_guild_available(guild):
    channel = bot.get_channel(ROLES_CHANNEL_ID)

    try:
        platform = await channel.fetch_message(PLATFORM_ROLE_MESSAGE_ID)
    except discord.NotFound:
        platform = None

    if platform:
        await platform.edit(view=utils.RoleSelectView(utils.RoleSelectPlatform))
    else:
        platform = await channel.send(
            "Select the platforms you play on:",
            view=utils.RoleSelectView(utils.RoleSelectPlatform),
        )
        print(f"New platform message id: {platform.id}")

    try:
        content = await channel.fetch_message(CONTENT_ROLE_MESSAGE_ID)
    except discord.NotFound:
        content = None

    if content:
        await content.edit(view=utils.RoleSelectView(utils.RoleSelectContent))
    else:
        content = await channel.send(
            "Select the type of content to get notified about:",
            view=utils.RoleSelectView(utils.RoleSelectContent),
        )
        print(f"New platform message id: {content.id}")

    try:
        extra = await channel.fetch_message(EXTRA_ROLE_MESSAGE_ID)
    except discord.NotFound:
        extra = None

    if extra:
        await extra.edit(view=utils.RoleSelectView(utils.RoleSelectExtra))
    else:
        await channel.send(
            "Select extra roles:", view=utils.RoleSelectView(utils.RoleSelectExtra)
        )
        print(f"New platform message id: {extra.id}")
    return


@tasks.loop(seconds=60)
async def update_leaderboard(self):
    channel = self.get_channel(LEADERBOARD_CHANNEL_ID)
    mjm = dbIntegration.read_leaderboard("mantlejumpmap")
    fm = dbIntegration.read_leaderboard("firstmap")
    gm = dbIntegration.read_leaderboard("gymmap")
    ih = dbIntegration.read_leaderboard("ithurtsmap")
    si = dbIntegration.read_leaderboard("strafeitmap")
    empty = "```ansi\n[2;41m[2;30m[0m[2;41m[0m[2;41m[2;30m[2;37m[1;37m[4;37mNO SUBMISSIONS[0m[1;37m[1;41m[0m[2;37m[2;41m[0m[2;30m[2;41m[0m[2;41m[0m```"

    mjm = utils.table_constructor(mjm) or empty
    fm = utils.table_constructor(fm) or empty
    gm = utils.table_constructor(gm) or empty
    ih = utils.table_constructor(ih) or empty
    si = utils.table_constructor(si) or empty

    # Updates the info about the leaderboards (1st message)
    try:
        leaderboard_message = await channel.fetch_message(LEADERBOARD_MESSAGE_ID)
        answer = utils.leaderboard_message

        if answer != leaderboard_message.content:
            await leaderboard_message.edit(content=answer)

    except: # noqa: E722
        print("Leaderboard message not found or unable to access.")

    # Updates the First Map leaderboard (2nd message)
    try:
        leaderboard_message = await channel.fetch_message(LEADERBOARD_FIRSTMAP_ID)
        answer = f"""### First Map
{fm}
post: https://discord.com/channels/839992880293478400/1100536422450073690"""

        if answer != leaderboard_message.content:
            await leaderboard_message.edit(content=answer)

    except:   # noqa: E722
        print("First Map Leaderboard message not found or unable to access.")

    # Updates the Gym Map leaderboard (3rd message)
    try:
        leaderboard_gymmap_message = await channel.fetch_message(LEADERBOARD_GYMMAP_ID)
        answer = f"""### Gym Map
{gm}
post: https://discord.com/channels/839992880293478400/1180733536676880396"""

        if answer != leaderboard_gymmap_message.content:
            await leaderboard_gymmap_message.edit(content=answer)

    except: # noqa: E722
        print("Gym Map Leaderboard message not found or unable to access")

    # Updates the Strafe It Map leaderboard (4th message)
    try:
        leaderboard_strafeitmap_message = await channel.fetch_message(
            LEADERBOARD_STRAFEIT_ID
        )
        answer = f"""### Strafe It
{si}
post: https://discord.com/channels/839992880293478400/1324802169878085702"""

        if answer != leaderboard_strafeitmap_message.content:
            await leaderboard_strafeitmap_message.edit(content=answer)

    except: # noqa: E722
        print("Strafe It Map Leaderboard message not found or unable to access")

    # Updates the It Hurts Map leaderboard (5th message)
    try:
        leaderboard_ithurtsmap_message = await channel.fetch_message(LEADERBOARD_ITHURTSMAP_ID)
        answer = f"""### It Hurts Map
{ih}
post: https://discord.com/channels/839992880293478400/1235449388147544074"""

        if answer != leaderboard_ithurtsmap_message.content:
            await leaderboard_ithurtsmap_message.edit(content=answer)

    except: # noqa: E722
        print("It Hurts Map Leaderboard message not found or unable to access")

    return


@tasks.loop(seconds=180)
async def update_online_players(self):
    channel = self.get_channel(PLAYERS_ONLINE_CHANNEL_ID)

    if channel is None:
        print("Channel **Players online** not found.")

    else:
        with open("info.json", "r") as file:
            data = json.load(file)
            players = data.get("players", "Z")

        new_name = f"{players} Players online"

        if channel.name != new_name:
            try:
                await channel.edit(name=f"{players} Players online")
            except:
                print(f"Error while editing channel during `update_online_players` function execution.")

    return


@tasks.loop(seconds=60)
async def log_runs(self):
    channel = self.get_channel(NEW_RUNS_CHANNEL_ID)

    if channel is None:
        print("Channel **New Runs** not found.")

    else:
        player_amount = "0"

        with open("info.json", "r") as file:
            data = json.load(file)
            now = datetime.now()
            player_amount = data.get("players", "0")

            for map_name, players in data.get("new_runs").items():
                if players:
                    chunks = [players[i:i + 10] for i in range(0, len(players), 10)]

                    for chunk in chunks:
                        answer = (
                            f"**{map_name.upper()}** - {now.strftime('%Y-%m-%d %H:%M')}\n"
                        )
                        answer += utils.log_runs_table(chunk)

                        try:
                            await channel.send(answer)
                        except:
                            print("Error sending chunk while executing `log_runs` function loop.")

        utils.reset_info_file(player_amount)
    return


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Ban spammers that uses @everyone and @here
    if "@everyone" in message.content or "@here" in message.content or "steamcommunity" in message.content:
        if utils.is_spammer(message, MODERATOR_ROLES_ID):
            try:
                await message.guild.ban(
                    message.author,
                    reason="Banned by Golden Sapling. Probably a hacked account.",
                    delete_message_seconds=604800,
                )

                now = datetime.now()
                print(
                    f"{message.author} was banned for spamming. Date: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                )

            except discord.Forbidden:
                print("I tried to ban but I do not have permission to do it.")

            except discord.HTTPException:
                print("Banning failed.")

    # Reply messages that contain twitter links with a better embed link
    match_twitter = re.search(TWITTER_PATTERN, message.content)
    match_x = re.search(X_PATTERN, message.content)
    match_reddit = re.search(REDDIT_PATTERN, message.content)

    if match_twitter or match_x:
        content = match_x.group(1) if match_x else match_twitter.group(1)

        answer = f"Here's a better version of the link: https://vxtwitter.com/{content}"

        await message.reply(answer)

    if match_reddit:
        content = match_reddit.group(1)

        answer = f"Here's a better version of the link: https://rxddit.com/r/{content}"

        await message.reply(answer)

    if message.channel.id == 1334921740866031770:
        try:
            await message.guild.ban(
                message.author,
                reason="Banned by Golden Sapling. Probably a hacked account.",
                delete_message_seconds=604800,
            )

            now = datetime.now()
            print(
                f"{message.author} was banned for spamming. Date: {now.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        except discord.Forbidden:
            print("I tried to ban but I do not have permission to do it.")

        except discord.HTTPException:
            print("Banning failed.")


    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")
    await bot.sync_commands()
    update_leaderboard.start(bot)
    update_online_players.start(bot)
    log_runs.start(bot)

    guilds = [guild.name for guild in bot.guilds]
    for guild in guilds:
        print(f"I'm on: '{guild}'' server")

bot.run(TOKEN)

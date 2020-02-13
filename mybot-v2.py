# imports
import discord
from discord.ext import commands
from random import randint
import time
import datetime
import json
from json_classes import *
import crypto_tracker


#------------------------------------------------#
#   Todo:                                        #
#  - ON CHANNEL ADD OR REMOVE UPDATE SERVER JSON #
#  - ADD ADMIN PARAMETER TO THE USERS            #
#  - IMPLEMENT USER NAME IN USER OBJECT          #
#  - IMPLEMENT XP SYSYTEM TOGGLE PER SERVER      #
#  - IMPLEMENT FAVORITE GAMES PER SERVER         #
#  - CUSTOMIZED MESSAGES                         #
#  - SAME CHANNEL NAME PROOF                     #
#  - UPDATE ALL CHANNELS ON_READY                #
#  - CHANGE UP THE NAMING                        #
#------------------------------------------------#


def json_load(file_path):
# Helper function for json loading
    with open(file_path, "r") as f:
        data = json.load(f)
        f.close()
    return data

def json_dump(data, file_path):
# Helper function for json dumping
    with open(file_path, "w") as f:
        json.dump(data, f)
        f.close()

# Setting it up
# Getting Secret Token and Default Prefix
settings = json_load("settings.json")
token = settings["token"]
default_prefix = settings["default_prefix"]

# Finding what prefix to use
def get_prefix(client, message):
    # Helper function for getting server specific prefix
    guilds_ids = json_load("servers/guilds.json")
    if str(message.guild.id) in guilds_ids:
        file_path = "servers/" + str(message.guild.id) + ".json"
        guild = json_guild(json_load(file_path))
        return guild.get_prefix()
    else:
        return default_prefix
client = commands.Bot(command_prefix = get_prefix)


@client.event
async def on_ready():
    # Helper function to add new entries in the JSON
    def empty_channel():
        res = {}
        res["listened"] = True
        return res
    def empty_guild(guild):
        output = {}
        output["id"] = str(guild.id)
        output["name"] = guild.name
        output["prefix"] = default_prefix
        output["users"] = {}
        output["channels"] = {}
        output["games"] = []
        for channel in guild.channels:
            output["channels"][str(channel.name)] = empty_channel()
        return json_guild(output)
    # Fetching data from all the guilds
    guilds_ids = json_load("servers/guilds.json")
    # Updating guilds data
    for connected_guild in client.guilds:
        file_path = "servers/" + str(connected_guild.id) + ".json"
        if str(connected_guild.id) not in guilds_ids:
            guilds_ids[str(connected_guild.id)] = connected_guild.name
            json_dump(empty_guild(connected_guild).dict(),file_path)
            json_dump(guilds_ids, "servers/guilds.json")
        else:
            guild = json_guild(json_load(file_path))
            connected_guild_channels = [] for channel in connected_guild.channels: if str(channel.name) not in guild.get_channels():
                    print("kek")
                    guild.add_channel(str(channel.name), json_channel(empty_channel()))
                connected_guild_channels.append(str(channel.name))
            for channel_name in guild.get_channels():
                if channel_name not in connected_guild_channels:
                    guild.remove_channel(channel_name)
            json_dump(guild.dict(), file_path)
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_member_join(member):
    print(str(member.guild.name) + ": " + member.id + " has joined the server.")

@client.event

@client.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        # Elo added per message sent
        # Updating user xp
        guild_id = str(message.author.guild.id)
        file_path = "servers/" + guild_id + ".json"
        guild = json_guild(json_load(file_path))
        if not message.content.startswith(guild.get_prefix()):
            # Fetching data from the guild
            if str(message.author.id) in guild.get_users():
                prev_xp = guild.get_user(str(message.author.id)).xp
                guild.get_user(str(message.author.id)).set_xp(prev_xp + 1)              
            else:
                def empty_user(member):
                    # Helper Function for adding new users to the JSON
                    data = {}
                    data["name"] = member.name
                    data["xp"] = 1
                    data["admin"] = False
                    data["last_vc"] = None
                    return json_user(data)
                # User is not registered yet
                guild.add_user(str(message.author.id), empty_user(message.author))
            json_dump(guild.dict(), file_path)
            print(str(message.author.guild.name) + ": " + "+1 elo to " + str(message.author))
        await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    await ctx.send("I don't know that command.")

@client.event
async def on_voice_state_update(member, before, after):
    
    def empty_user(member):
        # Helper Function for adding new users to the JSON
        data = {}
        data["name"] = member.name
        data["xp"] = 1
        data["admin"] = False
        data["last_vc"] = None
        return json_user(data)

    guild_id = str(member.guild.id)
    author_id = str(member.id)
    file_path = file_path = "servers/" + guild_id + ".json"

    # Quando entra num channel
    if str(before.channel) == "None" and str(after.channel) != "None":
        now_str = str(datetime.datetime.now())
        # Updating vc join time
        guild = json_guild(json_load(file_path))
        # Verify if user is already registered
        if author_id in guild.get_users():
            guild.get_user(author_id).set_last_vc(now_str)
        else:
            guild.add_user(author_id, empty_user(member))
            guild.get_user(author_id).set_last_vc(now_str)
        print(member.name + " joined a voice channel at " + now_str[0:19])
    # Quando sai do channel
    elif str(before.channel) != "None" and str(after.channel) == "None":
        now = datetime.datetime.now()
        now_str = str(now)
        author_id = author_id
        # Fetch previous time
        guild = json_guild(json_load(file_path))
        # Converting date string to datetime obj
        previous_time_obj = datetime.datetime.strptime(guild.get_user(author_id).get_last_vc(), '%Y-%m-%d %H:%M:%S.%f')
        # Updating JSON
        guild.get_user(author_id).set_last_vc(now_str)
        # Calculating xp to be given to the user
        delta = now - previous_time_obj
        seconds = delta.seconds + delta.days * 24 * 3600
        prev_xp = guild.get_user(author_id).get_xp()
        guild.get_user(author_id).set_xp(prev_xp + int(seconds/5))
        print(member.name + " left a voice channel at " + now_str[0:19])
    # Updating JSON with new "last_vc" and posible new "xp"
    json_dump(guild.dict(), file_path)


# COMMANDS SECTION
# HELPER FUNCTIONS FOR COMMANDS
def listening_channel(ctx):
    # Helper function for checking if channel should be or not listened
    guild_id = str(ctx.message.guild.id)
    file_path = file_path = "servers/" + guild_id + ".json"
    channel_name = ctx.channel.name
    guild = json_guild(json_load(file_path))
    return guild.get_channel(channel_name).is_listened() == True

# Admin Commands
@client.command()
async def prefix(ctx):
    guild_id = str(ctx.message.guild.id)
    file_path = file_path = "servers/" + guild_id + ".json"
    guild = json_guild(json_load(file_path))
    if listening_channel(ctx):
        msg = ctx.message.content.split(" ")
        if len(msg) != 2:
            await ctx.send("Usage: " + guild.get_prefix() + "prefix <desired_prefix>")
        else:
            new_prefix = msg[1]
            guild.set_prefix(new_prefix)
            json_dump(guild.dict(), file_path)
            await ctx.send("Server prefix changed to " + "\"" + new_prefix + "\"")

@client.command()
async def ignore(ctx):
    guild_id = str(ctx.message.guild.id)
    file_path = file_path = "servers/" + guild_id + ".json"
    channel_name = ctx.channel.name
    msg = ctx.message.content.strip(" ")
    if not isinstance(msg, str):
        await ctx.send("Usage example: .ignore")
    else:
        guild = json_guild(json_load(file_path))
        if guild.get_channel(channel_name).is_listened() == True:
            guild.get_channel(channel_name).set_listened(False)
            json_dump(guild.dict(), file_path)
            await ctx.send(channel_name + " added to the ignore list")
        else:
            guild.get_channel(channel_name).set_listened(True)
            json_dump(guild.dict(), file_path)
            await ctx.send(channel_name + " removed from the ignore list")


@client.command()
async def clear(ctx, amount = 5):
    if listening_channel(ctx):
        await ctx.channel.purge(limit = amount)

# Fun
@client.command()
async def ping(ctx):
    if listening_channel(ctx):
        await ctx.send("Pong!")


# Utils
@client.command()
async def eth(ctx):
    if listening_channel(ctx):
        crypto_tuple = crypto_tracker.get_latest_crypto_price("ethereum")[0]
        await ctx.send(crypto_tuple[0]  + ": $" + str(int(crypto_tuple[1])))

@client.command()
async def btc(ctx):
    if listening_channel(ctx):
        crypto_tuple = crypto_tracker.get_latest_crypto_price("bitcoin")[0]
        await ctx.send(crypto_tuple[0]  + ": $" + str(int(crypto_tuple[1])))

@client.command()
async def echo(ctx):
    if listening_channel(ctx):
        msg = ctx.message.content.split(" ")
        output = ""
        for word in msg[1:]:
            output += word
            output += " "
        await ctx.send(output)

@client.command()
async def wtp(ctx):
    if listening_channel(ctx):
        guild_id = str(ctx.message.guild.id)
        file_path = file_path = "servers/" + guild_id + ".json"
        guild = json_guild(json_load(file_path))
        if guild.get_games() != []:
            variations_list = ["I think it's time for {}.","Why not {}.", "{} is my favourite."]
            random_game_index, random_variation_index = randint(0, len(guild.get_games())-1), randint(0, len(variations_list)-1)
            await ctx.send(variations_list[random_variation_index].format(guild.get_games()[random_game_index]))
        else:
            await ctx.send("There's no games for me to choose from.")
@client.command()
async def wtp_add(ctx, game):
    guild_id = str(ctx.message.guild.id)
    file_path = file_path = "servers/" + guild_id + ".json"
    guild = json_guild(json_load(file_path))
    if game not in guild.get_games():
        guild.add_game(game)
        json_dump(guild.dict(), file_path)
        await ctx.send(game + " added to the server games list.")
    else:
        await ctx.send(game + " is already added to the server games list.")
    else:
        await ctx.send(game + " is already added to the server games list.")

@client.command()
async def wtp_remove(ctx, game):
    guild_id = str(ctx.message.guild.id)
    file_path = file_path = "servers/" + guild_id + ".json"
    guild = json_guild(json_load(file_path))
    if game in guild.get_games():
        guild.remove_game(game)
        json_dump(guild.dict(), file_path)
        await ctx.send(game + " removed from the server games list.")
    else:
        await ctx.send(game + " wasn't already on the server games list.")


@client.command()
async def wtp_list(ctx):
    guild_id = str(ctx.message.guild.id)
    file_path = file_path = "servers/" + guild_id + ".json"
    guild = json_guild(json_load(file_path))
    await ctx.send("List of games in the server: " + str(guild.get_games()))

@client.command()
async def xp(ctx):
    if listening_channel(ctx):
        guild_id = str(ctx.message.guild.id)
        file_path = file_path = "servers/" + guild_id + ".json"
        author_id = str(ctx.message.author.id)
        guild = json_guild(json_load(file_path))
        # Veryfing there's content to display for that user.
        if author_id in guild.get_users():
            await ctx.send("You have " + str(guild.get_user(author_id).get_xp()) + " xp.")
        else:
            await ctx.send(ctx.message.author.name + " you have no xp yet.")

@client.command()
async def king(ctx):
    if listening_channel(ctx):
        guild_id = str(ctx.message.guild.id)
        file_path = file_path = "servers/" + guild_id + ".json"
        author_id = str(ctx.message.author.id)
        guild = json_guild(json_load(file_path))
        max = 0
        for user_id in guild.get_users():
            if guild.get_user(user_id).get_xp() > max:
                king = guild.get_user(user_id).get_name()
                king_id = user_id
                max = guild.get_user(user_id).get_xp()
        if king_id == author_id:
            await ctx.send("You are the king " + ctx.message.author.name + "!")
        else:
            await ctx.send(king + " is the king.")

# WIPS
client.run(token)



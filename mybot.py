# Imports
import discord
from discord.ext import commands
from random import randint
import time
import datetime
import json
import json_classes
import crypto_tracker


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
        guild_info = json_load(file_path)
        return guild_info["prefix"]
    else:
        return default_prefix
client = commands.Bot(command_prefix = get_prefix)


#--------------------------------------------
#   Todo:
#  - ON CHANNEL ADD OR REMOVE UPDATE SERVER JSON
#  - ADD ADMIN PARAMETER TO THE USERS
#  - IMPLEMENT USER NAME IN USER OBJECT
#  - IMPLEMENT XP SYSYTEM TOGGLE PER SERVER
#  - IMPLEMENT FAVORITE GAMES PER SERVER
#  - CUSTOMIZED MESSAGES
#--------------------------------------------


@client.event
async def on_ready():
    # Helper function to add new entries in the JSON
    def add_guild(guild):
        output = {}
        output["id"] = str(guild.id)
        output["name"] = guild.name
        output["prefix"] = default_prefix
        output["users"] = {}
        output["channels"] = {}
        for channel in guild.channels:
            output["channels"][str(channel.name)] = True
        return output
    # Fetching data from all the guilds
    guilds_ids = json_load("servers/guilds.json")
    # Updating guilds data
    for guild in client.guilds:
        if str(guild.id) not in guilds_ids:
            guilds_ids[str(guild.id)] = guild.name
            file_path = "servers/" + str(guild.id) + ".json"
            json_dump(add_guild(guild),file_path)
            json_dump(guilds_ids, "servers/guilds.json")
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_member_join(member):
    print(str(member.guild.name) + ": " + member.id + " has joined the server.")

@client.event
async def on_member_remove(member):
    print(str(member.guild.name) + ": " + member.id + " has left the server.")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        # Elo added per message sent
        # Updating user xp
        guild_id = str(message.author.guild.id)
        file_path = "servers/" + guild_id + ".json"
        guild_info = json_load(file_path)
        prefix = guild_info["prefix"]
        users = guild_info["users"]
        if not message.content.startswith(prefix):
            # Fetching data from the guild
            if str(message.author.id) in users:
                users[str(message.author.id)]["xp"] += 1
                guild_info["users"] = users               
            else:
                def add_user(member):
                    # Helper Function for adding new users to the JSON
                    user = {}
                    user["name"] = member.name
                    user["xp"] = 1
                    user["admin"] = False
                    user["last_vc"] = None
                    return user
                # User is not registered yet
                users[str(message.author.id)] = add_user(message.author)
            json_dump(guild_info, file_path)
            print(str(message.author.guild.name) + ": " + "+1 elo to " + str(message.author))
        await client.process_commands(message)
    
@client.event
async def on_command_error(ctx, error):
    await ctx.send("I don't know that command.")

@client.event
async def on_voice_state_update(member, before, after):
    def add_user(member):
        # Helper Function for adding new users to the JSON
        user = {}
        user["name"] = member.name
        user["xp"] = 1
        user["admin"] = False
        user["last_vc"] = None
        return user
    guild_id = str(member.guild.id)
    member_id = str(member.id)
    file_path = file_path = "servers/" + guild_id + ".json"
    # Quando entra num channel
    if str(before.channel) == "None" and str(after.channel) != "None":
        now_str = str(datetime.datetime.now())
        # Updating vc join time
        guild_info = json_load(file_path)
        # Verify if user is already registered
        if member_id in guild_info["users"]:
            guild_info["users"][member_id]["last_vc"] = now_str
        else:
            guild_info["users"][member_id] = add_user(member)
            guild_info["users"][member_id]["last_vc"] = now_str
    # Quando sai do channel
    if str(before.channel) != "None" and str(after.channel) == "None":
        now = datetime.datetime.now()
        now_str = str(now)
        # Fetch previous time
        guild_info = json_load(file_path)
        previous_time_str = guild_info["users"][str(member.id)]["last_vc"]
        # Converting date string to datetime obj
        previous_time_obj = datetime.datetime.strptime(previous_time_str, '%Y-%m-%d %H:%M:%S.%f')
        # Updating JSON
        guild_info["users"][str(member.id)]["last_vc"] = now_str
        # Calculating xp to be given to the user
        delta = now - previous_time_obj
        seconds = delta.seconds + delta.days * 24 * 3600
        guild_info["users"][str(member.id)]["xp"] += int(seconds/5)
    # Updating JSON with new "last_vc" and posible new "xp"
    json_dump(guild_info, file_path)
    print(member.name + " joined a voice channel at " + now_str)


# COMMANDS SECTION

# HELPER FUNCTIONS FOR COMMANDS
def listening_channel(ctx):
    # Helper function for checking if channel should be or not listened
    guild_id = str(ctx.message.guild.id)
    file_path = file_path = "servers/" + guild_id + ".json"
    channel_name = ctx.channel.name

    guild_info = json_load(file_path)

    return guild_info["channels"][channel_name] == True

"""@client.command()
async def admin(member):
    print(str(member.administrator))"""

# Admin Commands
@client.command()
async def prefix(ctx):
    guild_id = str(ctx.message.guild.id)
    file_path = file_path = "servers/" + guild_id + ".json"
    guild_info = json_load(file_path)
    guild_prefix = guild_info["prefix"]
    if listening_channel(ctx):
        msg = ctx.message.content.split(" ")
        if len(msg) != 2:
            await ctx.send("Usage: " + guild_prefix + "prefix <desired_prefix>")
        else:
            new_prefix = msg[1]
            guild_info["prefix"] = new_prefix
            json_dump(guild_info, file_path)
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
        guild_info = json_load(file_path)
        state = guild_info["channels"][channel_name]
        if state == True:
            guild_info["channels"][channel_name] = False
            json_dump(guild_info, file_path)
            await ctx.send(channel_name + " added to the ignore list")
        else:
            guild_info["channels"][channel_name] = True
            json_dump(guild_info, file_path)
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
        game_list = ["PlayerUnknown's Battlegrounds", "CS:GO", "Overwatch","League of Legends", "Team Fight Tactics", "Minecraft", "No Man's sky"]
        variations_list = ["I think it's time for {}.","Why not {}.", "{} is my favourite."]
        random_game_index, random_variation_index = randint(0, len(game_list)-1), randint(0, len(variations_list)-1)
        await ctx.send(variations_list[random_variation_index].format(game_list[random_game_index]))

@client.command()
async def xp(ctx):
    if listening_channel(ctx):
        guild_id = str(ctx.message.guild.id)
        file_path = file_path = "servers/" + guild_id + ".json"
        user_id = str(ctx.message.author.id)
        guild_info = json_load(file_path)
        # Veryfing there's content to display for that user.
        if user_id in guild_info["users"]:
            await ctx.send("You have " + str(guild_info["users"][user_id]["xp"]) + " xp.")
        else:
            await ctx.send(ctx.message.author.name + " you have no xp yet.")

@client.command()
async def king(ctx):
    if listening_channel(ctx):
        guild_id = str(ctx.message.guild.id)
        file_path = file_path = "servers/" + guild_id + ".json"
        user_id = str(ctx.message.author.id)
        guild_info = json_load(file_path)
        max = 0
        for user in guild_info["users"]:
            if guild_info["users"][user]["xp"] > max:
                king = guild_info["users"][user]["name"]
                king_id = user
                max = guild_info["users"][user]["xp"]
        if king_id == user_id:
            await ctx.send("You are the king " + ctx.message.author.name + "!")
        else:
            await ctx.send(king + " is the king.")

# WIPS
client.run(token)
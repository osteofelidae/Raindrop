# DEPENDENCIES

import discord
import json



# VARIABLES

# Embed color
DISCORD_EMBED_COLOR = 0x87CEEB
CTX_SUCCESS_COLOR = 0x00FF00
CTX_FAILURE_COLOR = 0xFF0000

# Config file name
CONFIG_FILENAME = "config.json"

# TODO Bot token
BOT_TOKEN = open("TOKEN.txt").read()

# Intents
intents = discord.Intents.default()
intents.message_content = True;

# Client
bot = discord.Bot(intents=intents)

# User data (settings)
user_data = {}



# FUNCTIONS

# Console print
def console_print(msgType: str, msgText: str):

    # Print
    print(f"[{msgType.upper()}] {msgText}")

# Function to save settings
def save_dict(dictIn: dict, fileName: str):
    # Open file
    file_object = open(fileName, "w")

    # Try dumping
    try:

        # Dump to file
        json.dump(dictIn, file_object)

    except:

        # Return error
        console_print("error", "Critical error writing to savefile.")

    # Close file
    file_object.close()

# def get_dict(dictIn: dict):
def get_dict(fileName: str):

    # Open file
    file_object = open(fileName)

    # Read to dict
    dictIn = json.loads(file_object.read())

    # Close file
    file_object.close()

    # Return
    return dictIn

# Fix dict
def fix_user_data_dict():

    # Globals
    global user_data

    # Temp var
    tempDict = {}

    # Iterate through dict
    for key in user_data:

        tempDict[int(key)] = user_data[key]

    user_data = tempDict

# Format number
def number_format(input: str, decimals: int):

    # Change to str
    input = str(input)

    if len(input) < decimals:

        input = "0" * (decimals-len(input)) + input

    # Return
    return input

# Propagate embed
async def propagate_embed(handle, embed):

    # Try send message to own server
    try:

        # Send message
        await bot.get_channel(user_data[handle.guild.id]["announcement_channel"]).send(embed=embed)

    except:

        # Console print error
        console_print("warning", f"Could not propagate event in server {handle.guild.name}")

        # Stop function because args or handle is wrong
        return

    # Iterate through all channels
    for guild_id in user_data:

        # If guild is on the same sync list and is not in the same server
        if user_data[guild_id]["sync_list"] == user_data[handle.guild.id]["sync_list"] and guild_id != handle.guild.id:

            # Try send message
            try:

                # Send message
                await bot.get_channel(user_data[guild_id]["announcement_channel"]).send(embed=embed)

            # Except: continue
            except:

                # Continue
                pass

# Propagate embed
async def propagate_message(handle, message):

    # Iterate through all channels
    for guild_id in user_data:

        # If guild is on the same sync list and is not in the same server
        if user_data[guild_id]["sync_list"] == user_data[handle.guild.id]["sync_list"] and guild_id != handle.guild.id:

            # Try send message
            try:

                # Send message
                await bot.get_channel(user_data[guild_id]["announcement_channel"]).send(content=message.content,
                                                                                        files=[await file.to_file() for file in message.attachments])

            # Except: continue
            except:

                # Continue
                pass

# Respond to command context
async def ctx_respond(ctx, type: str, text: str):

    # Try create embed object
    try:

        # Determine color. If success:
        if type.lower() == "success":

            # Set color
            embed_color = CTX_SUCCESS_COLOR

        # If failure
        elif type.lower() == "failure" or type.lower() == "error":

            # Set color
            embed_color = CTX_FAILURE_COLOR

        # If neither
        else:

            # Set color
            embed_color = DISCORD_EMBED_COLOR


        # Create embed
        embed = discord.Embed(title=f"{type.capitalize()}",
                              description=f"{text}",
                              color=embed_color)

        # Respond
        await ctx.respond(embed=embed)

    except:

        # Continue
        pass

# Check admin perms
async def verify_admin(ctx):

    # Check whether admin perms
    if ctx.author.guild_permissions.administrator:

        return True

    else:

        return False

# Check server setup
def check_setup(ctx):

    # Required fields array
    required_fields = ["announcement_channel",
                       "bot_channel",
                       "sync_list"]

    # Try calling all required fields
    try:

        # Iterate through required fields
        for field in required_fields:

            user_data[ctx.guild.id][field]

        return True

    except:

        return False



# EVENTS

# On bot load
@bot.event
async def on_ready():

    # Globals
    global user_data

    # Get user data
    user_data = get_dict(CONFIG_FILENAME)
    fix_user_data_dict()

    # Print status
    console_print("success", f"Logged in as {bot.user}")

# On event creation
@bot.event
async def on_scheduled_event_create(event: discord.ScheduledEvent):

    # Try check enabled
    try:

        if not (user_data[event.guild.id]["auto_event"]):
            return

    except:

        pass

    # Variables
    timing_text = ""

    # Try create timing text
    try:

        # Create timing text
        timing_text = (f"{number_format(event.start_time.hour, 2)}:" +
                      f"{number_format(event.start_time.minute, 2)}," +
                      f" {number_format(event.start_time.month, 2)}/" +
                      f"{number_format(event.start_time.day, 2)}/" +
                      f"{number_format(event.start_time.year, 2)}")

        # Try add end time
        timing_text += (f" - {number_format(event.end_time.hour, 2)}:" +
                       f"{number_format(event.end_time.minute, 2)}," +
                       f" {number_format(event.end_time.month, 2)}/" +
                       f"{number_format(event.end_time.day, 2)}/" +
                       f"{number_format(event.end_time.year, 2)}")

    except:

        # Continue
        pass

    # Try create embed object
    embed = discord.Embed()

    try:

        # Create embed
        embed = discord.Embed(title=f"Event: {event.name}",
                              url=event.url,
                              description=f"{timing_text}",
                              color=DISCORD_EMBED_COLOR)

        # Add location field
        embed.add_field(name="Location:",
                        value=event.location.value)

        # Add description field
        embed.add_field(name="Description:",
                        value=event.description)

        # Set author
        embed.set_author(
            name=event.guild.name,
            url=event.url
        )
        embed.set_author(
            name=event.guild.name,
            url=event.url,
            icon_url=event.guild.icon.url
        )

    except:

        # Continue
        pass

    # Propagate embed (error handling is within function)
    await propagate_embed(event, embed)

# On message send
@bot.event
async def on_message(message):

    # Check setup of server
    if not (check_setup(message)):

        # Stop function
        return

    # TODO tester
    if message.channel.id == user_data[message.guild.id]["announcement_channel"] and not(message.author.bot):

        # Try check enabled
        try:

            if not (user_data[message.guild.id]["auto_announce"]):
                return

        except:

            pass

        await propagate_message(message, message)



# SLASH COMMANDS

# About command
@bot.slash_command()
async def about(ctx):

    # Variables
    DESCRIPTION = "Tool suite designed for synchronizing announcements and events between Discord servers."

    # Create embed
    embed = discord.Embed(title="About Raindrop",
                          description=DESCRIPTION,
                          url="https://github.com/osteofelidae/Raindrop",
                          color=DISCORD_EMBED_COLOR)

    # Set author
    embed.set_author(
        name="Made with pride by osteofelidae",
        url="https://osteofelidae.github.io/",
        icon_url="https://avatars.githubusercontent.com/u/115187283?s=40&v=4"
    )

    # Add field
    embed.add_field(name="GitHub repo/readme:",
                    value="https://github.com/osteofelidae/Raindrop")

    # Send message
    await ctx.respond(embed=embed)



# Setup command
@bot.slash_command()
async def setup(ctx,
              announcement_channel: discord.TextChannel = "",
              bot_channel: discord.TextChannel = "",
              sync_list: str = "",
              auto_event: bool = "",
              auto_announce: bool = ""):

    # Globals
    global user_data

    # Check admin
    if not (await verify_admin(ctx)):
        # Return error message
        await ctx_respond(ctx, "error", "Insufficient permissions.")

        # Stop function
        return

    # If dict does not exist, create it
    try:

        user_data[ctx.guild.id]

    except:

        user_data[ctx.guild.id] = {}

    if announcement_channel != "":

        # Variables
        set_type = "announcement_channel"

        # Try to setup
        try:

            # Set user data
            user_data[int(ctx.guild.id)][set_type] = announcement_channel.id

            # Save dict
            save_dict(user_data, CONFIG_FILENAME)

            # Console print
            console_print("success", f"Successfully set {set_type} to {announcement_channel.name}")

            # Send confirmation
            await ctx_respond(ctx, "success", f"Successfully set {set_type} to {announcement_channel.mention}")


        except:

            # Console print
            console_print("warning", f"Failed to setup {set_type} in {ctx.guild.name}")

            # Respond
            await ctx_respond(ctx, "error",
                              f"Could not set up {set_type}. Try running '/setup init' first, then try again.")

    if bot_channel != "":

        # Variables
        set_type = "bot_channel"

        # Try to setup
        try:
            # Set user data
            user_data[int(ctx.guild.id)][set_type] = bot_channel.id

            # Save dict
            save_dict(user_data, CONFIG_FILENAME)

            # Console print
            console_print("success", f"Successfully set {set_type} to {bot_channel.name}")

            # Send confirmation
            await ctx_respond(ctx, "success", f"Successfully set {set_type} to {bot_channel.mention}")

        except:

            # Console print
            console_print("warning", f"Failed to setup {set_type} in {ctx.guild.name}")

            # Respond
            await ctx_respond(ctx, "error",
                              f"Could not set up {set_type}. Try running '/setup init' first, then try again.")

    if sync_list != "":

        # Variables
        set_type = "sync_list"

        # Try to setup
        try:

            # Set user data
            user_data[int(ctx.guild.id)][set_type] = sync_list

            # Save dict
            save_dict(user_data, CONFIG_FILENAME)

            # Console print
            console_print("success", f"Successfully set {set_type} to {sync_list}")

            # Send confirmation
            await ctx_respond(ctx, "success", f"Successfully set {set_type} to {sync_list}")


        except:

            # Console print
            console_print("warning", f"Failed to setup {set_type} in {ctx.guild.name}")

            # Respond
            await ctx_respond(ctx, "error",
                              f"Could not set up {set_type}. Try running '/setup init' first, then try again.")

    if auto_event != "":

        # Variables
        set_type = "auto_event"

        # Try to setup
        try:

            # Set user data
            user_data[int(ctx.guild.id)][set_type] = auto_event

            # Save dict
            save_dict(user_data, CONFIG_FILENAME)

            # Console print
            console_print("success", f"Successfully set {set_type} to {auto_event}")

            # Send confirmation
            await ctx_respond(ctx, "success", f"Successfully set {set_type} to {auto_event}")


        except:

            # Console print
            console_print("warning", f"Failed to setup {set_type} in {ctx.guild.name}")

            # Respond
            await ctx_respond(ctx, "error",
                              f"Could not set up {set_type}. Try running '/setup init' first, then try again.")

    if auto_announce != "":

        # Variables
        set_type = "auto_announce"

        # Try to setup
        try:

            # Set user data
            user_data[int(ctx.guild.id)][set_type] = auto_announce

            # Save dict
            save_dict(user_data, CONFIG_FILENAME)

            # Console print
            console_print("success", f"Successfully set {set_type} to {auto_announce}")

            # Send confirmation
            await ctx_respond(ctx, "success", f"Successfully set {set_type} to {auto_announce}")


        except:

            # Console print
            console_print("warning", f"Failed to setup {set_type} in {ctx.guild.name}")

            # Respond
            await ctx_respond(ctx, "error",
                              f"Could not set up {set_type}. Try running '/setup init' first, then try again.")



# Do commands
do = discord.SlashCommandGroup("do", "Create something")

# Announcement command
@do.command()
async def announce(ctx,
                   title: str,
                   content: str,
                   url = "",
                   ping_role: discord.Role = ""):

    # Check setup of server
    if not(check_setup(ctx)):

        # Return error message
        await ctx_respond(ctx, "error", "Server is not fully set up. Please run all setup commands.")

        # Stop function
        return

    # Check admin
    if not (await verify_admin(ctx)):

        # Return error message
        await ctx_respond(ctx, "error", "Insufficient permissions.")

        # Stop function
        return

    # Try create embed
    try:

        # Create embed
        embed = discord.Embed(title=title,
                              description=content,
                              color=DISCORD_EMBED_COLOR)

        # Set url if exists
        if url != "":

            embed.url = url

        # Set author
        embed.set_author(
            name=ctx.guild.name,
        )
        embed.set_author(
            name=ctx.guild.name,
            icon_url=ctx.guild.icon.url
        )

    except:

        # Continue
        pass

# Ping
    try:

        if ping_role != "":

            # Send ping
            await bot.get_channel(user_data[int(ctx.guild.id)]["announcement_channel"]).send(ping_role.mention)

    except:

        # Return error
        await ctx_respond(ctx, "error", "Could not announce. This could be because the server is not properly set up.")

        # Stop function
        return

    # Propagate embed (error handling is within function)
    await propagate_embed(ctx, embed)

    # Send confirmation
    await ctx_respond(ctx, "success", f"Successfully sent announcement.")

# Cross ban command
@do.command()
async def cross_ban(ctx,
                    user: discord.User,
                    reason: str = ""):

    # Check setup of server
    if not (check_setup(ctx)):
        # Return error message
        await ctx_respond(ctx, "error", "Server is not fully set up. Please run all setup commands.")

        # Stop function
        return

    # Check admin
    if not (await verify_admin(ctx)):
        # Return error message
        await ctx_respond(ctx, "error", "Insufficient permissions.")

        # Stop function
        return

    # Try ban
    try:

        # Ban in own server
        await ctx.guild.ban(user)

    except:

        # Return error
        await ctx_respond(ctx, "error", "Could not ban.")

        # Exit function
        return


    # Iterate through all channels
    for guild_id in user_data:

        # If guild is on the same sync list and is not in the same server
        if user_data[guild_id]["sync_list"] == user_data[ctx.guild.id]["sync_list"] and guild_id != ctx.guild.id:

            # Try send message
            try:

                # Ban user
                await bot.get_guild(guild_id).ban(user, reason=reason)

            # Except: continue
            except:

                # Continue
                pass

    # Send confirmation
    await ctx_respond(ctx, "success", f"Successfully cross banned {user.name}.")



# REGISTER COMMAND GROUPS
bot.add_application_command(do)



# RUN BOT

bot.run(BOT_TOKEN)
# TODO cmd for creating invite

# DEPENDENCIES

import discord
import json



# VARIABLES

# Embed color
DISCORD_EMBED_COLOR = 0x87CEEB
CTX_SUCCESS_COLOR = 0x00FF00
CTX_FAILURE_COLOR = 0xFF0000

# Save file names
CONFIG_FILENAME = "config.json"
LOCKED_FILENAME = "locked.json" # List of locked sync codes
BLACKLIST_FILENAME = "blacklist.json" # List of blacklisted servers


# File opened
file_open = False

# TBot token
BOT_TOKEN = open("TOKEN.txt").read()

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Client
bot = discord.Bot(intents=intents)

# User data (settings)
user_data = {}
locked_codes = {}
blacklist = {}



# FUNCTIONS

# Console print
def console_print(msgType: str, msgText: str):

    # Print
    print(f"[{msgType.upper()}] {msgText}")

# Function to save settings
def save_dict(dictIn: dict, fileName: str):

    # Globals
    global file_open

    # If file is not open
    if not(file_open):

        # Set file open
        file_open = True

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

        # Set file closed
        file_open = False

# def get_dict(dictIn: dict):
def get_dict(fileName: str):

    # Open file
    file_object = open(fileName)

    # Read to dict
    dictIn = json.loads(file_object.read())

    # Close file
    file_object.close()

    # Return
    return fix_dict(dictIn)

# Fix dict
def fix_dict(dict_in: dict):

    # Temp var
    tempDict = {}

    try:

        # Iterate through dict
        for key in dict_in:

            tempDict[int(key)] = dict_in[key]

    except:

        tempDict = dict_in

    return tempDict

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

        # Ctx respond
        await ctx_respond(handle, "error", "Could not send message. This may be because the server is not fully set up.")

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
                await bot.get_channel(user_data[guild_id]["promotion_channel"]).send(embed=embed)


            # Except: try announcement channel
            except:

                try:
                    # Send message
                    await bot.get_channel(user_data[guild_id]["announcement_channel"]).send(embed=embed)

                except:

                    # Continue
                    pass

# Propagate  message
async def propagate_message(handle, message):

    # Iterate through all channels
    for guild_id in user_data:

        # If guild is on the same sync list and is not in the same server
        if user_data[guild_id]["sync_list"] == user_data[handle.guild.id]["sync_list"] and guild_id != handle.guild.id:

            # Try send message
            try:

                # Send message
                await bot.get_channel(user_data[guild_id]["promotion_channel"]).send(content=f"*Via {message.guild.name}:*\n" + message.content,
                                                                                        files=[await file.to_file() for file in message.attachments])

            # Except: continue
            except:

                try:
                    # Send message
                    await bot.get_channel(user_data[guild_id]["announcement_channel"]).send(content=f"*Via {message.guild.name}:*\n" + message.content,
                                                                                            files=[await file.to_file()
                                                                                                   for file in
                                                                                                   message.attachments])

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

# Check if osteofelidae
async def verify_osteofelidae(ctx):

    # Check if it is me
    if ctx.author.id == 446592818136219648:

        return True

    else:

        return False

# Check blacklist - return false if blacklisted
def check_blacklist(ctx):

    # try
    try:

        # If guild id is blocked (blacklist[id] true if blocked)
        if blacklist[int(ctx.guild.id)]:

            return False

    except:

        pass

    # Return
    return True



# EVENTS

# On bot load
@bot.event
async def on_ready():

    # Globals
    global user_data, blacklist, locked_codes

    # Get user data
    user_data = get_dict(CONFIG_FILENAME)
    blacklist = get_dict(BLACKLIST_FILENAME)
    locked_codes = get_dict(LOCKED_FILENAME)

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

    # Try propagate
    try:

        # Propagate announcement
        if message.channel.id == user_data[message.guild.id]["announcement_channel"] and not(message.author.bot):

            # Try check enabled
            try:

                if not (user_data[message.guild.id]["auto_announce"]):
                    return

            except:

                pass

            await propagate_message(message, message)

            console_print("success", f"Propagated announcement from {message.guild.name}")

    except:

        console_print("error", f"Failed to propagate announcement from {message.guild.name}")



# SLASH COMMANDS

# About command
@bot.slash_command(description="Returns info about the bot.")
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
@bot.slash_command(description="Setup command for the bot.")
async def setup(ctx,
              announcement_channel: discord.TextChannel = "",
              promotion_channel: discord.TextChannel = "",
              sync_list: str = "",
              auto_event: bool = "",
              auto_announce: bool = ""):

    # Output variable
    output_string = ""
    error_exists = False

    # Globals
    global user_data

    # Check admin
    if not (await verify_admin(ctx)):
        # Return error message
        await ctx_respond(ctx, "error", "Insufficient permissions.")

        # Stop function
        return

    # Check blacklist
    if not (check_blacklist(ctx)):
        # Return error message
        await ctx_respond(ctx, "error", "Server is not permitted to use this bot.")

        # Stop function
        return

    # If dict does not exist, create it
    try:

        user_data[ctx.guild.id]

    except:

        user_data[ctx.guild.id] = {}

        # Console print
        console_print("success", f"{ctx.guild.name}: Successfully initialized")

        # Send confirmation
        output_string += "Successfully initialized server\n"

    if announcement_channel != "":

        # Variables
        set_type = "announcement_channel"

        # Try to setup
        try:

            # Set user data
            user_data[int(ctx.guild.id)][set_type] = announcement_channel.id

            # Console print
            console_print("success", f"{ctx.guild.name}: Successfully set {set_type} to {announcement_channel.name}")

            # Send confirmation
            output_string += f"Successfully set {set_type} to {announcement_channel.mention}\n"


        except:

            # Console print
            console_print("warning", f"{ctx.guild.name}: Failed to setup {set_type}")

            # Respond
            output_string += f"Could not set up {set_type}.\n"

            # Set error
            error_exists = True

    if promotion_channel != "":

        # Variables
        set_type = "promotion_channel"

        # Try to setup
        try:
            # Set user data
            user_data[int(ctx.guild.id)][set_type] = promotion_channel.id

            # Console print
            console_print("success", f"{ctx.guild.name}: Successfully set {set_type} to {promotion_channel.name}")

            # Send confirmation
            output_string += f"Successfully set {set_type} to {promotion_channel.mention}\n"

        except:

            # Console print
            console_print("warning", f"{ctx.guild.name}: Failed to setup {set_type}")

            # Respond
            output_string += f"Could not set up {set_type}.\n"

            # Set error
            error_exists = True

    if sync_list != "":

        # Variables
        set_type = "sync_list"
        do_sync = True

        # Check if blocked
        try:

            if locked_codes[sync_list]:

                # Console print
                console_print("warning", f"{ctx.guild.name}: Failed to setup {set_type} as it is locked")

                # Respond
                output_string += f"Could not set up {set_type} as this sync list is locked.\n"

                # Set error
                error_exists = True
                do_sync = False


        except:

            pass

        # Try to setup
        if do_sync:
            try:

                # Set user data
                user_data[int(ctx.guild.id)][set_type] = sync_list

                # Console print
                console_print("success", f"{ctx.guild.name}: Successfully set {set_type} to {sync_list}")

                # Send confirmation
                output_string += f"Successfully set {set_type} to {sync_list}\n"


            except:

                # Console print
                console_print("warning", f"{ctx.guild.name}: Failed to setup {set_type}")

                # Respond
                output_string += f"Could not set up {set_type}.\n"

                # Set error
                error_exists = True

    if auto_event != "":

        # Variables
        set_type = "auto_event"

        # Try to setup
        try:

            # Set user data
            user_data[int(ctx.guild.id)][set_type] = auto_event

            # Console print
            console_print("success", f"{ctx.guild.name}: Successfully set {set_type} to {auto_event}")

            # Send confirmation
            output_string += f"Successfully set {set_type} to {auto_event}\n"


        except:

            # Console print
            console_print("warning", f"{ctx.guild.name}: Failed to setup {set_type}")

            # Respond
            output_string += f"Could not set up {set_type}.\n"

            # Set error
            error_exists = True

    if auto_announce != "":

        # Variables
        set_type = "auto_announce"

        # Try to setup
        try:

            # Set user data
            user_data[int(ctx.guild.id)][set_type] = auto_announce

            # Console print
            console_print("success", f"{ctx.guild.name}: Successfully set {set_type} to {auto_announce}")

            # Send confirmation
            output_string += f"Successfully set {set_type} to {auto_announce}\n"


        except:

            # Console print
            console_print("warning", f"{ctx.guild.name}: Failed to setup {set_type}")

            # Respond
            output_string += f"Could not set up {set_type}.\n"

            # Set error
            error_exists = True

    # Save dict
    save_dict(user_data, CONFIG_FILENAME)

    # Check for errors
    if error_exists:

        error_string = "error"

    else:

        error_string = "success"

    # Respond
    await ctx_respond(ctx, error_string, output_string)



# Do commands
do = discord.SlashCommandGroup("do", "Create something")

# Announcement command
@do.command(description="Sends an announcement to all servers.")
async def announce(ctx,
                   title: str,
                   content: str,
                   url = "",
                   ping_role: discord.Role = ""):

    # Check setup of server
    if not(check_setup(ctx)):

        # Console print
        console_print("warning", f"{ctx.guild.name}: Attempted to announce when server was not set up")

        # Return error message
        await ctx_respond(ctx, "error", "Server is not fully set up. Please run all setup commands.")

        # Stop function
        return

    # Check admin
    if not (await verify_admin(ctx)):

        # Console print
        console_print("warning", f"{ctx.guild.name}: Attempted to announce, but the user had insufficient permissions")

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

        # Console print
        console_print("warning", f"{ctx.guild.name}: Attempted to announce when server was not set up")

        # Return error
        await ctx_respond(ctx, "error", "Could not announce. This could be because the server is not properly set up.")

        # Stop function
        return

    # Propagate embed (error handling is within function)
    await propagate_embed(ctx, embed)

    # Send confirmation
    await ctx_respond(ctx, "success", f"Successfully sent announcement.")

@do.command(description="Sends an announcement to this server only.")
async def local_announce(ctx,
                   title: str,
                   content: str,
                   url = "",
                   ping_role: discord.Role = ""):

    # Check setup of server
    if not(check_setup(ctx)):

        # Console print
        console_print("warning", f"{ctx.guild.name}: Attempted to announce when server was not set up")

        # Return error message
        await ctx_respond(ctx, "error", "Server is not fully set up. Please run all setup commands.")

        # Stop function
        return

    # Check admin
    if not (await verify_admin(ctx)):

        # Console print
        console_print("warning", f"{ctx.guild.name}: Attempted to announce, but the user had insufficient permissions")

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

        # Console print
        console_print("warning", f"{ctx.guild.name}: Attempted to announce when server was not set up")

        # Return error
        await ctx_respond(ctx, "error", "Could not announce. This could be because the server is not properly set up.")

        # Stop function
        return

    # Try send message to own server
    try:

        # Send message
        await bot.get_channel(user_data[ctx.guild.id]["announcement_channel"]).send(embed=embed)

    except:

        # Console print error
        console_print("warning", f"Could not send announcement in server {ctx.guild.name}")

        # Return error
        await ctx_respond(ctx, "error", "Could not announce. This could be because the server is not properly set up.")

        # Stop function because args or handle is wrong
        return

    # Send confirmation
    await ctx_respond(ctx, "success", f"Successfully sent announcement.")

# Cross ban command
@do.command(description="Bans a user across all servers.")
async def cross_ban(ctx,
                    user: discord.User,
                    reason: str = ""):

    # Check setup of server
    if not (check_setup(ctx)):

        # Console print
        console_print("warning", f"{ctx.guild.name}: Attempted to cross ban when server was not set up")

        # Return error message
        await ctx_respond(ctx, "error", "Server is not fully set up. Please run all setup commands.")

        # Stop function
        return

    # Check admin
    if not (await verify_admin(ctx)):

        # Console print
        console_print("warning", f"{ctx.guild.name}: Attempted to cross ban but user had insufficient permissions")

        # Return error message
        await ctx_respond(ctx, "error", "Insufficient permissions.")

        # Stop function
        return

    # Try ban
    try:

        # Ban in own server
        await ctx.guild.ban(user)

    except:

        # Console print
        console_print("error", f"{ctx.guild.name}: Failed to ban user")

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

# Admin commands
admin = discord.SlashCommandGroup("admin", "Admin slash commands")

# Rollback
@admin.command(description="Delete last x messages in announcement channels")
async def rollback(ctx,
                   sync_list: str,
                   message_count: int = 1,):

    # Output variable
    output_string = ""
    error_exists = False

    # Check if me
    if not (await verify_osteofelidae(ctx)):
        # Console print
        console_print("warning", f"{ctx.guild.name}: Attempted to run an admin command, but the user had insufficient permissions")

        # Return error message
        await ctx_respond(ctx, "error", "Insufficient permissions.")

        # Stop function
        return

    # Iterate through all channels
    for guild_id in user_data:

        # If guild is on the same sync list and is not in the same server
        if user_data[guild_id]["sync_list"] == sync_list:

            # Try send message
            try:

                # Loop n times for n messages
                for index in range(message_count):

                    # Delete message
                    await (await bot.get_channel(user_data[guild_id]["announcement_channel"]).history(limit=1).flatten())[0].delete()

                # Print
                console_print("success",
                              f"Rolled back {bot.get_guild(guild_id).name} (id {guild_id})")

                # Respond
                output_string += f"Rolled back {bot.get_guild(guild_id).name} (id {guild_id}).\n"

            # Except: continue
            except:

                # Warn
                console_print("warning", f"Could not roll back server {bot.get_guild(guild_id).name} (id {guild_id})")

                # Respond
                output_string += f"Failed to roll back {bot.get_guild(guild_id).name} (id {guild_id}).\n"

                # Set error
                error_exists = True

    # Check for errors
    if error_exists:

        error_string = "error"

    else:

        error_string = "success"

    # Respond
    await ctx_respond(ctx, error_string, output_string)

# Blacklist
@admin.command(description="Edit server blacklist")
async def blacklist_edit(ctx,
                    server_id: str,
                    blacklisted: bool = True):

    # Check admin
    if not (await verify_osteofelidae(ctx)):
        # Console print
        console_print("warning",
                      f"{ctx.guild.name}: Attempted to run an admin command, but the user had insufficient permissions")

        # Return error message
        await ctx_respond(ctx, "error", "Insufficient permissions.")

        # Stop function
        return

    # Set blacklist to input (default true)
    blacklist[int(server_id)] = blacklisted

    # Reset server settings
    user_data[int(server_id)] = {}

    # Update savefiles
    save_dict(user_data, CONFIG_FILENAME)
    save_dict(blacklist, BLACKLIST_FILENAME)

    # Console print
    console_print("success", f"Successfully blacklisted server id {server_id}")

    # Return success
    await ctx_respond(ctx, "success", f"Successfully blacklisted server id {server_id}")

# Lock syncgroup
@admin.command(description="Edit locked codes")
async def sync_group_edit(ctx,
                    sync_code: str,
                    locked: bool = True):

    # Check admin
    if not (await verify_osteofelidae(ctx)):

        # Console print
        console_print("warning",
                      f"{ctx.guild.name}: Attempted to run an admin command, but the user had insufficient permissions")

        # Return error message
        await ctx_respond(ctx, "error", "Insufficient permissions.")

        # Stop function
        return

    # Set blacklist to true
    locked_codes[sync_code] = locked

    # Update savefile
    save_dict(locked_codes, LOCKED_FILENAME)

    # Console print
    console_print("success", f"Successfully edited {sync_code}")

    # Return success
    await ctx_respond(ctx, "success", f"Successfully edited {sync_code}")

# Return logs
# TODO this
@admin.command(description="Get logs")
async def get_logs(ctx):

    # Check admin
    if not (await verify_osteofelidae(ctx)):
        # Console print
        console_print("warning",
                      f"{ctx.guild.name}: Attempted to run an admin command, but the user had insufficient permissions")

        # Return error message
        await ctx_respond(ctx, "error", "Insufficient permissions.")

        # Stop function
        return


# Return report (all logs in a readable manner)
# TODO this
@admin.command(description="Get report")
async def get_report(ctx):

    # Check admin
    if not (await verify_osteofelidae(ctx)):
        # Console print
        console_print("warning",
                      f"{ctx.guild.name}: Attempted to run an admin command, but the user had insufficient permissions")

        # Return error message
        await ctx_respond(ctx, "error", "Insufficient permissions.")

        # Stop function
        return




# REGISTER COMMAND GROUPS

bot.add_application_command(do)
bot.add_application_command(admin)



# RUN BOT

bot.run(BOT_TOKEN)
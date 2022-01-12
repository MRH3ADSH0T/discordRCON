
# Requirements: pip install mcrcon, discord.py, discord-py-slash-command, py-dotenv

from mcrcon import MCRcon
from discord import Intents
from discord.ext import commands
from socket import gethostname as IP
from datetime import datetime as datet
from discord_slash import SlashCommand
from discord_slash import SlashContext
from dotenv import dotenv_values as denv
from discord_slash.utils.manage_commands import create_option

# Find secrets
secrets=dict(denv(".env"))
TOKEN=secrets["BotToken"]
PASSWD=secrets["RCONPassword"]
USERID=secrets["discordID"]
# Server IDs that the bot accepts commands on.
SERVERS=[int(serverID) for serverID in secrets["serverIDs"].split(" ")]
# Stores machine's IP address. Unfortunately, "localhost" doesn't work with MCRcon
HOST=IP()

# Configure bot and slash module
client=commands.Bot(
    command_prefix="",
    intents=Intents.all()
)
slash=SlashCommand(client, sync_commands=True)

@client.event
async def on_ready():
    """
    Loads client configurations and establishes connection to RCON server.
    """
    # Specifies bot owner
    client.accountID=USERID
    client.username=client.get_user(client.accountID).display_name

    # Following lines establish connection to the Minecraft Server
    print("Establishing RCON connection...")
    client.rcon=MCRcon(HOST,PASSWD)
    client.rcon.connect()

    # Return success message at finish time. Performance monitoring.
    _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S")
    print(f"{_dt} - Init success.")

@slash.slash(
    name="rcon",
    description="Runs input through RCON console and returns the output.",
    guild_ids=SERVERS,
    options=[
        create_option(
            name="cmd",
            description="Minecraft command. Specific command support coming soon.",
            option_type=3,
            required=True
        )
    ])
async def _RCON(ctx:SlashContext, cmd:str, **other:str):
    """
    Handles /rcon command. Will accept minecraft slash command, returns output from RCON console.
    cmd: the base command, if null, then execute other as command.
    other: optional arguments or replacement command if it is not listed.
    """

    if ctx.author.id==client.accountID:

        # Execute command and capture response.
        response:str=client.rcon.command(cmd)

        # Following 2 conditions handle invalid responses
        if len(response)==0:
            response="Success!"
        elif len(response)>2000:
            response=response[:2000]
        
        # Finally, send message
        await ctx.send(f"```{response}```")

        # Safe shutdown
        if cmd=="stop":
            client.rcon.disconnect()
    
    # Invalid permissions
    else:
        await ctx.send(f"```Only for {client.username}.```")

@slash.slash(
    name="Whitelist",
    description="Adds a player to the whitelist",
    guild_ids=SERVERS,
    options=[
        create_option(
            name="Player",
            option_type=3,
            description="The player to be whitelisted",
            required=True,
        )
    ])
async def _whitetlist(ctx:SlashContext,player:str):
    """
    Handles /whitelist add. Will not check if the player is already in the whitelisted members file.
    To remove a player from the whitelist, manually run `/rcon cmd: whitelist remove [username]` from Discord.
    """

    if ctx.author.id==client.accountID:
        
        response:str=client.rcon.command(f"whitelist add {player}")

        await ctx.send(f"```{response}```")

    # Invalid permissions
    else:
        ctx.send(f"```Only for {client.username}.```")

if __name__=="__main__":
    client.run(TOKEN)

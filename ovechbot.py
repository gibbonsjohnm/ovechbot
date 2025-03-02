import requests
import json
import discord
from discord.ext import tasks
import logging
import os

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger("discord.gateway").setLevel(logging.CRITICAL)

client = discord.Client(intents=discord.Intents.default())
TOKEN  = os.environ['DISCORD_TOKEN']

INITIAL_TOTAL        = 853
SEASON_TOTAL         = 0
SEASON_TOTAL_SET     = set([])
OVECHKIN_GOAL        = False
OVECHKIN_GAME_ACTIVE = False
HOME_TEAM = ""
AWAY_TEAM = ""

@client.event
async def on_ready():
    logging.info(f'{client.user} has connected to Discord!')
    check.start()

@tasks.loop(seconds=60)
async def check():
    global OVECHKIN_GOAL
    global OVECHKIN_GAME_ACTIVE
    channel = client.get_channel(int(os.environ['DISCORD_CHANNEL']))
    first = []
    get_goals(first)
    if OVECHKIN_GAME_ACTIVE:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{HOME_TEAM} vs {AWAY_TEAM}'))
    else:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="no Caps games :("))
    if not first:
        pass
    else:
        for goal in first:
            json_obj = convert_to_json(goal)
            detect_ovechkin_goal(json_obj)
            if OVECHKIN_GOAL:
                logging.info(f"Ovechkin scored goal #{INITIAL_TOTAL + SEASON_TOTAL}! Sending messages.")
                goals = INITIAL_TOTAL + SEASON_TOTAL

                base_message = (
                    f":rotating_light: **Alexander Ovechkin has scored goal #{goals}** :rotating_light:\n"
                    "```\n"
                    f"Goals remaining: {895 - goals if goals < 895 else 0}\n"
                    "```"
                )

                special_message = None
                if goals == 894:
                    special_message = (
                        "@here ⚠️ **Alexander Ovechkin has tied Wayne Gretzky's all-time goal record** ⚠️"
                    )
                elif goals == 895:
                    special_message = (
                        "@here 🥳 **Alexander Ovechkin has passed the Trump-loving, overrated doofus Wayne Gretzky "
                        "for most goals in NHL history!!!** 🥳"
                    )

                # Send the base message
                await channel.send(content=base_message)

                # Send the special message separately if applicable
                if special_message:
                    await channel.send(content=special_message)

                OVECHKIN_GOAL = False

def get_goals(list):
    global OVECHKIN_GAME_ACTIVE
    global HOME_TEAM
    global AWAY_TEAM
    url = 'https://api-web.nhle.com/v1/score/now'
    resp = requests.get(url=url)
    data = resp.json()
    try:
        games = data['games']
        for game in games:
            if game['awayTeam']['abbrev'] == "WSH" or game['homeTeam']['abbrev'] == "WSH":
                HOME_TEAM = game['homeTeam']['abbrev']
                AWAY_TEAM = game['awayTeam']['abbrev']
                if game['gameState'] == "LIVE" or game['gameState'] == "CRIT":
                    OVECHKIN_GAME_ACTIVE = True
                else:
                    OVECHKIN_GAME_ACTIVE = False
                goals = game['goals']
                for goal in goals:
                    list.append(str(goal))
                break;
            else:
                OVECHKIN_GAME_ACTIVE = False
    except (TypeError, KeyError) as error:
        pass
        
def convert_to_json(string):
    dbl_string = string.replace("'", '"')
    try:
        json_str = json.loads(dbl_string)
        return json_str
    except ValueError:
        pass

def detect_ovechkin_goal(json):
    global OVECHKIN_GOAL
    global SEASON_TOTAL
    try:
        if json['playerId'] == 8471214:
            SEASON_TOTAL = json['goalsToDate']
            if SEASON_TOTAL in SEASON_TOTAL_SET:
                pass
            else:
                logging.info(json)
                logging.info("Ovechkin scored!")
                OVECHKIN_GOAL = True
                SEASON_TOTAL_SET.add(SEASON_TOTAL)
        else:
            pass
    except (TypeError, KeyError) as error:
        pass

client.run(TOKEN)

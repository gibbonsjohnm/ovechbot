import requests
import json
import discord
import asyncio
from discord.ext import tasks
import pytz
import logging
import os

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger("discord.gateway").setLevel(logging.CRITICAL)

TOKEN = os.environ['DISCORD_TOKEN']

TOTAL = 780
OVECHKIN_GOAL = False

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    logging.info(f'{client.user} has connected to Discord!')
    channel = client.get_channel(int(os.environ['DISCORD_CHANNEL']))
    check.start()

@tasks.loop()
async def check():
    global OVECHKIN_GOAL
    channel = client.get_channel(os.environ['DISCORD_CHANNEL'])
    first = []
    second = []
    get_goals(first)
    if not first:
        pass
    else:
        await asyncio.sleep(60)
        get_goals(second)
        if not second:
            pass
        difference = set(first) ^ set(second)
        if (len(difference) == 0):
            pass
        else:
            logging.info("Goal(s) detected")
            for goal in difference:
                logging.info(goal)
                json_obj = convert_to_json(goal)
                detect_ovechkin_goal(json_obj)
            if OVECHKIN_GOAL:
                logging.info("Sending message to discord")
                await channel.send(f':rotating_light: **Alexander Ovechkin has scored goal #{TOTAL}** :rotating_light:')
                OVECHKIN_GOAL = False

def get_goals(list):
    url = 'https://nhl-score-api.herokuapp.com/api/scores/latest'
    resp = requests.get(url=url)
    data = resp.json()

    try:
        games = data['games']
        for game in games:
            if game['status']['state'] == "LIVE":
                goals = game['goals']
                for goal in goals:
                    list.append(str(goal))
            else:
                pass
    except TypeError:
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
    global TOTAL
    global SEASON_TOTAL
    global SEASON_TOTAL_SET
    try:
        if json['scorer']['player'] == "Alex Ovechkin":
            SEASON_TOTAL = json['scorer']['seasonTotal']
            if SEASON_TOTAL in SEASON_TOTAL_SET:
                pass
            else:
                logging.info("Ovechkin scored!")
                OVECHKIN_GOAL = True
                SEASON_TOTAL_SET.add(SEASON_TOTAL)
                TOTAL = TOTAL + SEASON_TOTAL
        else:
            pass
    except TypeError:
        pass

client.run(TOKEN)
import requests
import json
import discord
import asyncio
from discord.ext import tasks
import logging
import os
import datetime
import pytz
from pytz import timezone

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger("discord.gateway").setLevel(logging.CRITICAL)

CLIENT = discord.Client(intents=discord.Intents.default())
TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL = CLIENT.get_channel(os.environ['DISCORD_CHANNEL'])

TOTAL = 780
SEASON_TOTAL_SET= set([])
OVECHKIN_GOAL = False

@CLIENT.event
async def on_ready():
    logging.info(f'{CLIENT.user} has connected to Discord!')
    check.start()

@tasks.loop()
async def check():
    global OVECHKIN_GOAL
    first = []
    second = []
    get_goals(first)
    await asyncio.sleep(60)
    if not first:
        pass
    else:
        get_goals(second)
        if not second:
            pass
        else:
            difference = set(first) ^ set(second)
            if (len(difference) == 0):
                pass
            else:
                logging.info("Goal(s) detected")
                for goal in difference:
                    logging.info(goal)
                    json_obj = convert_to_json(goal)
                    detect_ovechkin_goal(json_obj)
        ### double check in case we missed the goal ###
        for goal in first:
            json_obj = convert_to_json(goal)
            detect_ovechkin_goal(json_obj)
        if OVECHKIN_GOAL:
            logging.info("Sending message to discord")
            await CHANNEL.send(f':rotating_light: **Alexander Ovechkin has scored goal #{TOTAL}** :rotating_light:')
            OVECHKIN_GOAL = False

def get_goals(list):
    url = 'https://nhl-score-api.herokuapp.com/api/scores/latest'
    resp = requests.get(url=url)
    data = resp.json()

    current_time = datetime.datetime.now(pytz.timezone('US/Pacific'))
    current_date = current_time.strftime("%Y-%m-%d")

    try:
        games_date = data['date']['raw']
        if str(current_date) == games_date:
            games = data['games']
            for game in games:
                if game['status']['state'] == "LIVE":
                    goals = game['goals']
                    for goal in goals:
                        list.append(str(goal))
                else:
                    pass
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

CLIENT.run(TOKEN)
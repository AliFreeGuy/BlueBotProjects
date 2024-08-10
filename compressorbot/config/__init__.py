# Bot Configs

from dotenv import load_dotenv
load_dotenv(override = True)
from utils.cache import *
from os import environ as env
from utils.connection import Connection


API_KEY = env.get('API_KEY')
API_URL = env.get('API_URL')
BOT_USERNAME = env.get('BOT_USERNAME')
BOT_TYPE = env.get('BOT_TYPE')
con = Connection(api_key=API_KEY, api_url=API_URL, bot_username=BOT_USERNAME)
setting = con.setting()


BOT_SESSION = setting.bot.session_string
API_ID = setting.bot.api_id
API_HASH = setting.bot.api_hash
BOT_TOKEN = setting.bot.bot_token

WORK_DIR = env.get('WORK_DIR') or '/tmp'
PROXY = {"scheme": env.get("PROXY_SCHEME"),
         "hostname": env.get("PROXY_HOSTNAME"),
         "port": int(env.get("PROXY_PORT"))}
DEBUG = env.get('BOT_DEBUG')
REDIS_HOST = env.get('REDIS_HOST')
REDIS_PORT = env.get('REDIS_PORT')
REDIS_DB= env.get('REDIS_DB')
REDIS_PASS = env.get('REDIS_PASS')


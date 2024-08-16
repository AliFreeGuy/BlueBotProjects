import requests
from dotmap import DotMap
from os import environ as env
import redis
import json

# تنظیمات مربوط به Redis
REDIS_HOST = env.get('REDIS_HOST', 'localhost')
REDIS_PORT = env.get('REDIS_PORT', 6379)
REDIS_DB = env.get('REDIS_DB', 0)
CACHE_TTL = int(env.get('CACHE_TTL', 1))  # زمان زندگی کش به ثانیه (به طور پیش‌فرض 1 ساعت)

# اتصال به Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

API_KEY = env.get('API_KEY')
API_URL = env.get('API_URL')
BOT_USERNAME = env.get('BOT_USERNAME')
BOT_TYPE = env.get('BOT_TYPE')

class Connection:

    def __init__(self, api_key, api_url, bot_username) -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.bot_username = bot_username
        self.headers = {'Authorization': f'Token {self.api_key}', 'Content-Type': 'application/json'}

    def link(self, pattern):
        return f'{self.api_url}/{pattern}/'

    def setting(self, lang=''):
        redis_key = f'setting:{self.bot_username}:{lang}'
        cached_setting = redis_client.get(redis_key)
        if cached_setting:
            return DotMap(json.loads(cached_setting))
        else:
            pattern = 'setting'
            data = {'bot': self.bot_username, 'lang': lang}
            res = requests.post(self.link(pattern), json=data, headers=self.headers)
            setting_data = res.json()
            redis_client.setex(redis_key, CACHE_TTL, json.dumps(setting_data))
            return DotMap(setting_data)



    def user(self, **kwargs):
        pattern = 'user'
        data = kwargs
        data['type'] = BOT_TYPE
        res = requests.post(self.link(pattern), json=data, headers=self.headers).json()
        user_data = res.pop('user')
        merged_data = {**user_data, **res}
        return DotMap(merged_data)

    def payment(self, chat_id, amount, plan_id, bot_id):
        pattern = 'create-payment'
        data = {
            'chat_id': chat_id,
            'amount': amount,
            'plan_id': plan_id,
            'bot_id': bot_id
        }
        res = requests.post(self.link(pattern), json=data, headers=self.headers)
        
        if res.status_code == 200:
            return DotMap(res.json())
        else:
            # Print error response for debugging
            print(f"Error: {res.status_code}, {res.text}")
            return None

con = Connection(api_key=API_KEY, api_url=API_URL, bot_username=BOT_USERNAME)

import requests
from dotmap import DotMap

class Connection:

    def __init__(self, api_key, api_url, bot_username) -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.bot_username = bot_username
        self.headers = {'Authorization': f'Token {self.api_key}', 'Content-Type': 'application/json'}

    def link(self, pattern):
        return f'{self.api_url}/{pattern}/'

    def setting(self, lang=''):
        pattern = 'setting'
        data = {'bot': self.bot_username, 'lang': lang}
        res = requests.post(self.link(pattern), json=data, headers=self.headers)
        return DotMap(res.json())

    def user(self, **kwargs):
        pattern = 'user'
        data = kwargs
        data['type'] = BOT_TYPE
        res = requests.post(self.link(pattern), json=data, headers=self.headers)
        return DotMap(res.json())

    def payment(self, chat_id, amount, plan_id, bot_id):
        pattern = 'payment'
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

# Example usage
API_KEY = '793ffda4ab247abd847102cc17ce3aeeb540114e'
API_URL = 'http://127.0.0.1:8000/api'
BOT_USERNAME = 'showbluebot'
BOT_TYPE = 'compressor'

con = Connection(api_key=API_KEY, api_url=API_URL, bot_username=BOT_USERNAME)

# Example payment call
payment_response = con.payment(
    chat_id=123456789,
    amount=1000,
    plan_id=1,
    bot_id=1
)

print(payment_response.url)
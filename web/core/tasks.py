
from celery import shared_task
import logging
from core.models import SendMessage , BotsModel
from compressor.models import CompressorUser
from collections import defaultdict
from pyrogram import Client 
from pyrogram.types import InlineKeyboardButton , InlineKeyboardMarkup
from django.conf import settings
import time
import random

logger = logging.getLogger(__name__)
PROXY = {"scheme": 'socks5',
            "hostname": '127.0.0.1',
            "port": 1080}




@shared_task
def message_sender(message_id):
    try:
        message = SendMessage.objects.get(pk=message_id)
        print(message)
        users = message.users.all()
        bots = message.bots.all()
        btns = message.btns.all()
        languages = message.languages.all()  # Get selected languages
        message_list = []

        if users.exists():
            if languages.exists():
                # Filter users by language
                users = users.filter(compressor__lang__in=languages)
            
            for user in users:
                for bot in bots:
                    if bot.type == 'compressor':
                        message_list.append({
                            "bot_token": bot.bot_token,
                            'session': bot.session_string,
                            "api_id": bot.api_id,
                            "api_hash": bot.api_hash,
                            "chat_id": user.chat_id,
                            "message": message.message
                        })
        else:
            if languages.exists():
                # Filter compressor users by language
                bot_users = CompressorUser.objects.filter(bot__in=bots, lang__in=languages)
            else:
                bot_users = CompressorUser.objects.filter(bot__in=bots)

            for compressor_user in bot_users:
                message_list.append({
                    "bot_token": compressor_user.bot.bot_token,
                    'session': compressor_user.bot.session_string,
                    "api_id": compressor_user.bot.api_id,
                    "api_hash": compressor_user.bot.api_hash,
                    "chat_id": compressor_user.user.chat_id,
                    "message": message.message
                })

        grouped_data = defaultdict(dict)

        for item in message_list:
            token = item['bot_token']
            user_chat_id = item['chat_id']
            if user_chat_id not in grouped_data[token]:
                grouped_data[token][user_chat_id] = item
        result = [list(group.values()) for group in grouped_data.values()]

        print(result)

        for bot in result:
            time.sleep(random.randint(1, 3))
            for msg_data in bot:
                if settings.DEBUG:
                    client = Client(
                        msg_data['bot_token'],
                        session_string=msg_data['session'],
                        api_id=int(msg_data['api_id']),
                        api_hash=msg_data['api_hash'],
                        proxy=PROXY
                    )
                else:
                    client = Client(
                        msg_data['bot_token'],
                        session_string=msg_data['session'],
                        api_id=int(msg_data['api_id']),
                        api_hash=msg_data['api_hash']
                    )

                with client:
                    try:
                        if msg_data['message'].startswith('https://t.me/c/'):
                            msg_id = msg_data['message'].split('/')[-1]
                            chat_id = f'-100{msg_data["message"].split("/")[-2]}'
                            message = client.get_messages(chat_id=int(chat_id), message_ids=int(msg_id))
                            if btns:
                                message.copy(int(msg_data['chat_id']), reply_markup=ads_btn(btns))
                            else:
                                message.copy(int(msg_data['chat_id']))

                        elif msg_data['message'].startswith('https://t.me/'):
                            msg_id = msg_data['message'].split('/')[-1]
                            chat_id = f'{msg_data["message"].split("/")[-2]}'
                            message = client.get_messages(chat_id=chat_id, message_ids=int(msg_id))
                            if btns:
                                message.copy(int(msg_data['chat_id']), reply_markup=ads_btn(btns))
                            else:
                                message.copy(int(msg_data['chat_id']))

                        else:
                            if btns:
                                client.send_message(
                                    chat_id=int(msg_data['chat_id']),
                                    text=msg_data['message'],
                                    reply_markup=ads_btn(btns)
                                )
                            else:
                                client.send_message(
                                    chat_id=int(msg_data['chat_id']),
                                    text=msg_data['message']
                                )

                    except Exception as e:
                        logging.warning(e)

    except SendMessage.DoesNotExist:
        logging.error(f"No SendMessage found with id {message_id}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")


def ads_btn(ads):
    buttons = []
    for  ad in ads:
        buttons.append([InlineKeyboardButton(text=ad.btn_name, url=ad.btn_url)])
    return InlineKeyboardMarkup(buttons)








@shared_task
def send_message(chat_id, text , bot_id):
    bot = BotsModel.objects.get(id = bot_id)
    if settings.DEBUG:
            client = Client(
                'send_payment_message',
                session_string=bot.session_string,
                api_id=bot.api_id,
                api_hash=bot.api_hash,
                proxy=PROXY
            )
    else:
            client = Client(
                'send_payment_message',
                session_string=bot.session_string,
                api_id=bot.api_id,
                api_hash=bot.api_hash,
            )
    try:
        with client :
            client.send_message(int(chat_id) , text = text)

    except Exception as e :
        # Handle the case where the user does not exist
        print(f'send payment message error : {str(e)}')
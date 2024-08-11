from pyrogram import filters
from utils.connection import con
from utils.logger import logger
import config
from datetime import datetime
from utils.utils import join_checker



async def bot_is_on(_ , cli , msg ):
    setting = con.setting()
    if setting.bot_status is  True : 
        return True
    return False


async def bot_is_off(_ , cli , msg ):
    setting = con.setting()
    if setting.bot_status is  True : 
        return False
    return True


async def user_is_join(_ , cli , msg ):

    setting = con.setting()
    channels = setting.channels
    is_join = await join_checker(cli , msg , channels)
    if not is_join : return True
    else :return False



async def user_not_join(_ , cli , msg ):
    setting = con.setting()
    channels = setting.channels
    is_join = await join_checker(cli , msg , channels)
    if not is_join : return False
    else :return True



async def user_is_active(_ , cli , msg ):
    user = con.user(chat_id=msg.from_user.id , full_name=msg.from_user.first_name)
    if user.is_active == True :return True
    return False


async def user_not_active(_ , cli , msg ):
    user = con.user(chat_id=msg.from_user.id , full_name=msg.from_user.first_name)
    if user.is_active == False:return True
    return False


# async def is_admin(_ , cli , msg ):
#     if int(msg.from_user.id) == config.ADMIN :
#         return True
#     return False

# async def user_not_admin(_ , cli , msg ):
#     if int(msg.from_user.id) == config.ADMIN :
#         return False
    # return True





user_not_join=filters.create(user_not_join)
user_is_join = filters.create(user_is_join)
bot_is_on = filters.create(bot_is_on)
bot_is_off = filters.create(bot_is_off)
user_is_active = filters.create(user_is_active)
user_not_active = filters.create(user_not_active)


# updater = filters.create(updater)
# is_admin = filters.create(is_admin)
# user_not_admin = filters.create(user_not_admin)
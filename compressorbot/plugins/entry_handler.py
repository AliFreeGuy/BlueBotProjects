from pyrogram import Client, filters
from utils import logger , cache , btn
from utils.connection import con
from utils import filters as f
import time
from utils.utils import join_checker






@Client.on_message(filters.private & f.bot_is_off , group=0)
async def bot_is_off(bot, msg):
    user = con.user(chat_id = msg.from_user.id )
    if user.lang :setting = con.setting(lang = user.lang)
    else :setting = con.setting()
    await msg.reply_text(setting.texts.bot_not_active_text , quote = True)


@Client.on_message(filters.private & f.user_not_active , group=0)
async def user_not_active(bot, msg):
    user = con.user(chat_id = msg.from_user.id )
    if user.lang :setting = con.setting(lang = user.lang)
    else :setting = con.setting()
    await bot.send_message(msg.from_user.id , setting.texts.user_not_active_text)



@Client.on_message(filters.private & f.user_not_join , group=0)
async def user_not_join(client , message ):
    user = con.user(chat_id = message.from_user.id )
    if user.lang :setting = con.setting(lang = user.lang)
    else :setting = con.setting()
    channels = setting.channels
    not_join_channels = await join_checker(client , message ,channels)
    if not_join_channels :
        await message.reply_text(text = setting.texts.force_join_text  , reply_markup = btn.join_channels_url(not_join_channels , setting.texts.i_joined_btn_text))




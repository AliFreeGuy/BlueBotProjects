from pyrogram import Client, filters
from utils import logger, cache, btn, txt
from utils.connection import con
from utils import filters as f
import time
from utils.utils import join_checker







@Client.on_message(filters.private & f.bot_is_on & f.user_is_join & f.user_is_active, group=1)
async def handler_manager(bot, msg):
    
    user = con.user(chat_id=msg.from_user.id)
    if user.lang:setting = con.setting(lang=user.lang)
    else:setting = con.setting()

    print(setting)
    btns = {
        f'🎫 {setting.texts.profile_btn}': profile_handler,
        f'🆘 {setting.texts.help_btn}': help_handler,
        f'🧑‍✈️ {setting.texts.support_btn}': support_handler,
        f'⚙️ {setting.texts.setting_btn}': setting_handler,
        f'🎖 {setting.texts.plans_btn}': plans_handler,
        '/privacy': privacy_handler ,
        '/start' : start_handler ,
        '/help' : help_handler,
        '/support' : support_handler ,
        '/setting' : setting_handler,
        '/plans' : plans_handler,
    }

    if msg and msg.text:
        handler_func = btns.get(msg.text)
        if handler_func:
            await handler_func(bot, msg, user, setting)


async def start_handler(bot , msg , user , setting ):
    await msg.reply_text(setting.texts.start_text, quote=True, reply_markup = btn.user_panel_menu(setting))


async def privacy_handler(bot, msg, user, setting):
    await msg.reply_text(stext = setting.texts.privacy_text, quote=True )


async def help_handler(bot, msg, user, setting):
    await msg.reply_text(setting.texts.help_text, quote=True)


async def support_handler(bot, msg, user, setting):
    await msg.reply_text(setting.texts.support_text, quote=True)







async def setting_handler(bot, msg, user, setting):    
    await msg.reply_text(text=setting.texts.setting_text, reply_markup=btn.setting_btn(user), quote=True)


async def plans_handler(bot, msg, user, setting):
    plans = setting.plans
    await msg.reply_text(text=setting.texts.plans_text, quote=True , reply_markup = btn.plans_btn(plans , setting , user ))



async def profile_handler(bot, msg, user, setting):
    print('proifle text')
    # ads = con.setting.ads
    # user = con.user(chat_id=msg.from_user.id, full_name=msg.from_user.first_name)
    # if ads:
    #     await msg.reply_text(txt.profile_text(user), quote=True, reply_markup=btn.ads_btn(ads))
    # else:
        # await msg.reply_text(txt.profile_text(user), quote=True)

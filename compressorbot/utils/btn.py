

from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,InlineKeyboardButton , KeyboardButton , WebAppInfo)
import config
import jdatetime
from utils.connection import con




def plans_btn(plans , setting , user ):
    buttons = []
    for  plan in plans:
        if user.lang and user.lang != 'fa' and plan.tag != 'free':
            buttons.append([InlineKeyboardButton(text=plan.name_en,callback_data=f'plans:{plan.id}')])
        if user.lang and user.lang == 'fa' and plan.tag != 'free':
            buttons.append([InlineKeyboardButton(text=plan.name,callback_data=f'plans:{plan.id}')])
    return InlineKeyboardMarkup(buttons)




def payment_plan_btn(url , lang ):
    buttons = []

    if lang == 'fa' :
        buttons.append([
                        InlineKeyboardButton(text='برگشت 🔙', callback_data='back_plans'),
                        InlineKeyboardButton(text='پرداخت صورتحساب', url=url),
                        ])
    else :
        buttons.append([
                        InlineKeyboardButton(text='back 🔙', callback_data='back_plans'),
                        InlineKeyboardButton(text='payment', url=url),
                        ])

    return InlineKeyboardMarkup(buttons)




def user_panel_menu(setting):
    # دکمه‌ها را از تنظیمات دریافت کنید
    setting_text = f'⚙️ {setting.texts.setting_btn}'
    help_text = f'🆘 {setting.texts.help_btn}'
    support_text = f'🧑‍✈️ {setting.texts.support_btn}'
    profile_text = f'🎫 {setting.texts.profile_btn}'
    plans_text = f'🎖 {setting.texts.plans_btn}'

    marks = [
        [setting_text, profile_text],
        [support_text, help_text, plans_text]
    ]
    return ReplyKeyboardMarkup(marks, resize_keyboard=True)




def join_channels_url(channels , btn_name):
    buttons = []
    for  channel in channels:
        text = channel.name
        buttons.append([InlineKeyboardButton(text=text, url=channel.link)])
    buttons.append([InlineKeyboardButton(text=btn_name,callback_data='join:joined')])
    return InlineKeyboardMarkup(buttons)


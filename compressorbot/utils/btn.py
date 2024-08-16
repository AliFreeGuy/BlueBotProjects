

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




def user_panel_menu(setting , user ):
    setting_text = f'⚙️ {setting.texts.setting_btn}'
    help_text = f'🆘 {setting.texts.help_btn}'
    support_text = f'🧑‍✈️ {setting.texts.support_btn}'
    profile_text = f'🎫 {setting.texts.profile_btn}'
    plans_text = f'🎖 {setting.texts.plans_btn}'

    marks = [
        [setting_text, profile_text],
        [plans_text],
        [support_text, help_text],]
    
    for miniapp in setting.ads:
        if not miniapp.url.startswith('https://t.me/'):
            miniapp_url = WebAppInfo(url=miniapp.url)
            marks.insert(0, [KeyboardButton(miniapp.name, web_app=miniapp_url)])
        

    if user.chat_id in [admin.chat_id for admin in setting.admin]:
        miniapp_url = WebAppInfo(url=config.ADMIN_PANEL)
        marks.append([KeyboardButton('ورود به ادمین پنل', web_app=miniapp_url)])


    return ReplyKeyboardMarkup(marks, resize_keyboard=True, placeholder=setting.texts.placeholder_text)




def join_channels_url(channels , btn_name):
    buttons = []
    for  channel in channels:
        text = channel.name
        buttons.append([InlineKeyboardButton(text=text, url=channel.link)])
    buttons.append([InlineKeyboardButton(text=btn_name,callback_data='join:joined')])
    return InlineKeyboardMarkup(buttons)




def ads_btn(ads):
    buttons = []
    for  ad in ads:
        if ad.url.startswith('https://t.me/'):
            buttons.append([InlineKeyboardButton(text=ad.name, url=ad.url)])
    return InlineKeyboardMarkup(buttons)




def block_user_btn(chat_id):
    buttons = [[InlineKeyboardButton(text='بلاک کاربر',callback_data=f'block_user:{chat_id}')]]
    return InlineKeyboardMarkup(buttons)

def unblock_user(chat_id):
    buttons = [[InlineKeyboardButton(text='آنبلاک کاربر',callback_data=f'unblock_user:{chat_id}')]]
    return InlineKeyboardMarkup(buttons)



def vid_editor_quality( vid_key ):

    buttons = []
    q1= 'کیفیت خوب'
    q2='کیفیت متوسط'
    q3= 'کیفیت کم'
    quality_btn = [
        InlineKeyboardButton(text=q1,callback_data=f'editor_1:{vid_key}'),
        InlineKeyboardButton(text=q2,callback_data=f'editor_2:{vid_key}'),
        InlineKeyboardButton(text=q3,callback_data=f'editor_3:{vid_key}'),
        ] 
    buttons.append(quality_btn)
    

    return InlineKeyboardMarkup(buttons)


def vid_editor_btn(vid_data , setting):
    
    buttons = []
    buttons.append([
        InlineKeyboardButton(text='❌ کنسل',callback_data=f'cancel-editor:{vid_data}'),
        InlineKeyboardButton(text='♻️ وضعیت',callback_data=f'status-editor:{vid_data}') ,
                    ])
    
    for ad in setting.ads :
        buttons.append(
        [InlineKeyboardButton(text=ad.name,url=ad.url),]

        )
    return InlineKeyboardMarkup(buttons)







def setting_btn(user, setting):
    user_lang = user.lang
    user_quality = user.quality

    print(user_quality)
    buttons = []

    # تنظیم دکمه‌های کیفیت
    if user_lang == 'fa':
        q1 = f'✔️ کیفیت خوب' if user_quality == 'quality_1' else 'کیفیت خوب'
        q2 = f'✔️ کیفیت متوسط' if user_quality == 'quality_2' else 'کیفیت متوسط'
        q3 = f'✔️ کیفیت کم' if user_quality == 'quality_3' else 'کیفیت کم'
        quality_btn = [
            InlineKeyboardButton(text=q1, callback_data='setting:quality_1'),
            InlineKeyboardButton(text=q2, callback_data='setting:quality_2'),
            InlineKeyboardButton(text=q3, callback_data='setting:quality_3'),
        ]
    else:
        q1 = f'✔️ good quality' if user_quality == 'quality_1' else 'good quality'
        q2 = f'✔️ mid quality' if user_quality == 'quality_2' else 'mid quality'
        q3 = f'✔️ low quality' if user_quality == 'quality_3' else 'low quality'
        quality_btn = [
            InlineKeyboardButton(text=q1, callback_data='setting:quality_1'),
            InlineKeyboardButton(text=q2, callback_data='setting:quality_2'),
            InlineKeyboardButton(text=q3, callback_data='setting:quality_3'),
        ]

    buttons.append(quality_btn)

    # تنظیم دکمه‌های زبان
    lang_buttons = []
    for i in range(0, len(setting.langs), 2):
        row_buttons = []
        for j in range(i, min(i + 2, len(setting.langs))):
            lang_code = setting.langs[j]
            text = f'✔️ {lang_code.name}' if lang_code.code == user_lang else lang_code.name
            callback_data = f'setting:lang_{lang_code.code}'[:64]  # محدود کردن طول callback_data
            row_buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        lang_buttons.append(row_buttons)

    # افزودن دکمه‌های زبان به لیست دکمه‌ها
    buttons.extend(lang_buttons)

    # تبدیل لیست دکمه‌ها به InlineKeyboardMarkup
    return InlineKeyboardMarkup(buttons)

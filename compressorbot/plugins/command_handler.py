from pyrogram import Client, filters
from utils import logger, cache, btn, txt
from utils.connection import con
from utils import filters as f
import time
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent,
                            InlineKeyboardMarkup, InlineKeyboardButton)
from utils.utils import join_checker , file_checker , b_to_mb
import random
from utils.tasks import editor






@Client.on_message(filters.private & f.bot_is_on & f.user_is_join & f.user_is_active, group=1)
async def handler_manager(bot, msg):
    
    user = con.user(chat_id=msg.from_user.id)
    if user.lang:setting = con.setting(lang=user.lang)
    else:setting = con.setting()

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
    print(setting.admin)
    await msg.reply_text(setting.texts.start_text, quote=True, reply_markup = btn.user_panel_menu(setting))


async def privacy_handler(bot, msg, user, setting):
    await msg.reply_text(stext = setting.texts.privacy_text, quote=True )


async def help_handler(bot, msg, user, setting):
    await msg.reply_text(setting.texts.help_text, quote=True)


async def support_handler(bot, msg, user, setting):
    await msg.reply_text(setting.texts.support_text, quote=True)


async def plans_handler(bot, msg, user, setting):
    plans = setting.plans
    await msg.reply_text(text=setting.texts.plans_text, quote=True , reply_markup = btn.plans_btn(plans , setting , user ))

async def profile_handler(bot, msg, user, setting):
    ads = setting.ads
    if ads:await msg.reply_text(txt.profile_text(user , setting), quote=True, reply_markup=btn.ads_btn(ads))
    else:await msg.reply_text(txt.profile_text(user , setting), quote=True)


async def setting_handler(bot, msg, user, setting):    
    await msg.reply_text(text=setting.texts.setting_text, reply_markup=btn.setting_btn(user = user , setting=setting), quote=True)








@Client.on_message(filters.private &f.user_is_join &filters.video & f.user_is_active , group=2)
async def video_editor_handler(bot, msg):
    if msg.from_user.id == msg.chat.id :
        user = con.user(chat_id=msg.from_user.id)
        if user.lang:setting = con.setting(lang=user.lang)
        else:setting = con.setting()

        if user.plan != None :await editor_manager(bot , msg  ,user , setting )
        else :await msg.reply_text(setting.texts.user_not_sub_text, quote=True)



async def editor_manager(bot, msg, user, setting):
    
    data = {}
    video_size = b_to_mb(msg.video.file_size)

    if user.plan.tag == 'free':
        max_limit = int(setting.max_limit_free_video)
    else:
        max_limit = int(setting.max_limit_video)

    if user.volume > video_size:

        if video_size <= max_limit:  

            user_data_text = f'{msg.caption}\n\n{txt.user_information(user)}'
            backup_vid = await msg.copy(int(setting.backup_channel), caption=user_data_text, reply_markup=btn.block_user_btn(msg.from_user.id))
            file_size = b_to_mb(msg.video.file_size)
            data['backup_msg_id'] = backup_vid.id
            data['chat_id'] = msg.from_user.id
            data['backup_file_id'] = backup_vid.video.file_id
            data['backup_caption'] = backup_vid.caption
            data['bot_msg_id'] = msg.id
            data['file_size'] = file_size
            data['unique_id'] = msg.video.file_unique_id
            data['caption'] = 'none' if not msg.caption else msg.caption
            update_user_volume = user.volume - file_size
            user = con.user(chat_id=msg.from_user.id, full_name=msg.from_user.first_name, volume=update_user_volume)

            if user:
                file_checker_data = file_checker(unique_id=msg.video.file_unique_id, quality=user.quality)
                if file_checker_data:
                    await bot.send_video(msg.from_user.id, video=file_checker_data['file_id'])

                elif not file_checker_data and user.quality != 'quality_0':
                    data['quality'] = user.quality
                    random_code = str(random.randint(9999, 999999))
                    data['id'] = random_code
                    vid_data_key = f'vid_data:{random_code}'
                    data['task_id'] = 'none'
                    data['width'] = msg.video.width
                    data['height'] = msg.video.height
                    data['duration'] = msg.video.duration
                    data['thumb'] = msg.video.thumbs[0].file_id if msg.video.thumbs else 'none'
                    task = editor.delay(data)
                    data['task_id'] = task.id
                    cache.redis.hmset(vid_data_key, data)
                    await msg.reply_text(setting.texts.editor_progress_text, quote=True, reply_markup=btn.vid_editor_btn(vid_data=vid_data_key, setting=setting))

                else:
                    data['task_id'] = 'none'
                    data['width'] = msg.video.width
                    data['height'] = msg.video.height
                    data['duration'] = msg.video.duration
                    data['thumb'] = msg.video.thumbs[0].file_id if msg.video.thumbs else 'none'
                    random_code = str(random.randint(9999, 999999))
                    data['id'] = random_code
                    vid_data_key = f'vid_data:{random_code}'
                    cache.redis.hmset(vid_data_key, data)
                    await msg.reply_text(setting.texts.editor_progress_text, quote=True, reply_markup=btn.vid_editor_quality(vid_key=vid_data_key))

            else:
                user_not_sub_text = setting.user_not_sub_text
                await msg.reply_text(user_not_sub_text, quote=True)

        else:
            await msg.reply_text(setting.max_limit_text, quote=True)

    else:
        user_not_sub_text = setting.user_not_sub_text
        await msg.reply_text(user_not_sub_text, quote=True)




# @Client.on_inline_query()
# async def answer(client, inline_query):
#     setting = con.setting()
#     random_sub_code = 'ffff'
#     results = []
#     admins_chat_id = [admin.chat_id for admin in setting.admin ]
#     query = inline_query.query.split(' ')
#     # if len(query) == 1 :
        
#     # for plan in plans :
#     #         if inline_query.query == plan['tag']:
#     #             sub_data = {'user' : 'none' , 'plan' : plan["tag"]}
#     #             cache.redis.hmset(f'sub:{random_sub_code}' , sub_data)
#     #             des_text = f'🌟 برای فعال سازی اشتراک خودتون بر روی دکمه زیر بزنید '
#     #             results.append(
#     #                     InlineQueryResultArticle(
#     #                         title=plan['name_fa'],
#     #                         input_message_content=InputTextMessageContent(f"{plan['des_fa']}\n\n{des_text}"),
#     #                         description=plan['des_fa'],
#     #                         reply_markup=btn.admin_inline_query(sub_code=random_sub_code)))

#     if inline_query.from_user.id == admins_chat_id :
#         await inline_query.answer(results ,cache_time=1)
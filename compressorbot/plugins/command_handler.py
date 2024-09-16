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
import json





@Client.on_message(filters.private & f.bot_is_on & f.user_is_join & f.user_is_active, group=1)
async def handler_manager(bot, msg):
    print('hi user mtoerh ')
    
    user = con.user(chat_id = msg.from_user.id )
    if user.lang:setting = con.setting(lang=user.lang)
    else:setting = con.setting()

    btns = {
        f'{setting.texts.profile_btn}': profile_handler,
        f'{setting.texts.help_btn}': help_handler,
        f'{setting.texts.support_btn}': support_handler,
        f'{setting.texts.setting_btn}': setting_handler,
        f'{setting.texts.plans_btn}': plans_handler,
        f'{setting.texts.add_volume_with_join_btn}' : add_volume_with_join_btn_handler,
        f'{setting.texts.add_volume_with_ref_btn}' : add_volume_with_ref_btn_handler,
        f'{setting.texts.add_volume_with_payment_btn}'  : add_volume_with_payment_btn_handler,
        '/privacy': privacy_handler ,
        '/start' : start_handler ,
        '/help' : help_handler,
        '/support' : support_handler ,
        '/setting' : setting_handler,
        '/plans' : plans_handler,
        '/profile' : profile_handler,
        '🔙' : start_handler
    }

    if msg and msg.text:
        handler_func = btns.get(msg.text)

        if msg.text.startswith('/start ref_'):
            await user_ref_handler(bot , msg ,user , setting )

        if handler_func:
            await handler_func(bot, msg, user, setting)
        
        




async def add_volume_with_join_btn_handler(bot , msg , user , setting ):
    channels = setting.add_volume_channels
    text = setting.texts.add_volume_with_join_text
    await msg.reply_text(text , quote=True  , reply_markup = btn.add_volume_join_btn(channels))




async def user_ref_handler(bot, msg, user, setting):
    refer = msg.text.replace('/start ref_', '')
    redis = cache.redis
    ads = setting.ads
    ref_key = f"user_ref:{refer}:{msg.from_user.id}"

    if str(refer) != str(msg.from_user.id):
        ref_user_data = redis.get(ref_key)
        if not ref_user_data:
            redis.set(ref_key, 'miomio')
            ref_user = con.user( chat_id= int(refer))
            new_volume = ref_user.volume + setting.ref_volume            
            user = con.user(chat_id=ref_user.chat_id, volume=new_volume)
            text = setting.texts.user_ref_text
            text = text.replace('refuser', msg.from_user.first_name)
            text = text.replace('user', user.full_name)
            text = text.replace('volume', str(setting.ref_volume))
            await bot.send_message(chat_id=int(refer), text=text, reply_markup=btn.ads_btn(ads))

        await start_handler(bot, msg, user, setting)
    else:
        await start_handler(bot, msg, user, setting)




async def add_volume_with_payment_btn_handler(bot ,msg , user , setting ):
    plans = setting.plans
    await msg.reply_text(text=setting.texts.plans_text, quote=True , reply_markup = btn.plans_btn(plans , setting , user ))




async def add_volume_with_ref_btn_handler(bot , msg , user , setting):
    user_ref_link = f'https://t.me/{setting.bot.username}?start=ref_{msg.from_user.id}'
    ref_text = f'{setting.texts.add_volume_with_ref_text}\n\n`{user_ref_link}`'
    share_text = f'{setting.texts.add_volume_with_ref_text_share}%0A%0A{user_ref_link}'
    share_link = f'https://t.me/share/url?url={share_text.replace(" " , "+")}'
    await msg.reply_text(ref_text , quote = True , reply_markup = btn.ref_link(share_link))



async def start_handler(bot , msg , user , setting ):
    await msg.reply_text(setting.texts.start_text, quote=True, reply_markup = btn.user_panel_menu(setting , user))


async def privacy_handler(bot, msg, user, setting):
    await msg.reply_text(stext = setting.texts.privacy_text, quote=True )


async def help_handler(bot, msg, user, setting):
    await msg.reply_text(setting.texts.help_text, quote=True)


async def support_handler(bot, msg, user, setting):
    await msg.reply_text(setting.texts.support_text, quote=True)


async def plans_handler(bot, msg, user, setting):
    plans = setting.plans
    await msg.reply_text(text=setting.texts.plans_text, quote=True , reply_markup = btn.add_volume_btn(plans , setting , user ))



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

            username = msg.from_user.username
            user_data_text = f'{msg.caption}\n\n{txt.user_information(user = user , username = str(username))}'
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
                    editor_msg_id = await msg.reply_text(setting.texts.editor_progress_text, quote=True, reply_markup=btn.vid_editor_btn(vid_data=vid_data_key, setting=setting))
                    await editor_msg_id.pin(both_sides =True)
                    data['bot_msg_id'] = editor_msg_id.id
                    print(editor_msg_id.id)
                    task = editor.delay(data)
                    print(task)
                    data['task_id'] = task.id
                    cache.redis.hmset(vid_data_key, data)

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
                    editor_msg = await msg.reply_text(setting.texts.editor_progress_text, quote=True, reply_markup=btn.vid_editor_quality(vid_key=vid_data_key))
                    
                    
            else:
                await msg.reply_text(setting.texts.user_not_sub_text, quote=True)

        else:
            await msg.reply_text(setting.texts.max_limit_text, quote=True)

    else:
        await msg.reply_text(setting.texts.user_not_sub_text, quote=True)





















@Client.on_chat_member_updated()
async def join_listener(client, message):

    user = con.user(chat_id=message.from_user.id)
    if user.lang:setting = con.setting(lang=user.lang)
    else:setting = con.setting()

    channels = setting.add_volume_channels
    channel_chat_ids =[int(channel.chat_id) for channel in setting.add_volume_channels]
    
 
    if int(message.chat.id ) in channel_chat_ids :

        if message.new_chat_member :
            await user_joined(client , message , setting , user  )
        
        elif message.old_chat_member :
            await user_leaved(client , message , setting , user  )



async def user_joined(client, message, setting, user):
    join_key = f'join_ref:{message.from_user.id}:{message.chat.id}'
    if not cache.redis.get(join_key):
        print(user.volume)
        new_volume = user.volume + setting.join_volume
        print(new_volume)
        user = con.user(chat_id=message.from_user.id, volume=new_volume)
        print(user)
        cache.redis.set(join_key, 'joined')
        text = setting.texts.user_join_text
        text = text.replace('user', user.full_name)
        text = text.replace('volume', str(setting.join_volume))
        await client.send_message(chat_id=message.from_user.id, text=text)


async def user_leaved(client, message, setting, user):
    leave_key = f'leave_ref:{message.from_user.id}:{message.chat.id}'
    if not cache.redis.get(leave_key):
        new_volume = max(user.volume - setting.join_volume, 0)
        user = con.user(chat_id=message.from_user.id, volume=new_volume)
        cache.redis.set(leave_key, 'leaved')
















@Client.on_inline_query()
async def answer(client, inline_query):
    setting = con.setting()
    admins = [admin.chat_id for admin in setting.admin]
    query_words = inline_query.query.strip().split(' ')

    results = []

    if len(query_words) == 1 and query_words[0] and query_words[0].isdigit(): 
        user = con.user(chat_id = query_words[0] )
  
        results.append(
            InlineQueryResultArticle(
                title=f"{user.full_name} - {user.chat_id}",
                input_message_content=InputTextMessageContent(
                   txt.user_information(user)
                ),
                description= f"حجم کاربر : {user.volume}",
          
            )
        )
    elif len(query_words) == 2 and query_words[1].isdigit():  
        user = con.user(chat_id=query_words[0], volume=query_words[1]) 
        print(user)
        user = con.user(chat_id=query_words[0])
        results.append(
            InlineQueryResultArticle(
                title=f"کاربر {user.full_name} - {user.chat_id}",
                input_message_content=InputTextMessageContent(
                   txt.user_information(user)
                ),
                description=f"حجم جدید کاربر: {user.volume}",
            )
        )

    if inline_query.from_user.id in admins:
        await inline_query.answer(results, cache_time=1)

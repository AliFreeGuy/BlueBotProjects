from pyrogram import Client, filters
from utils import logger , cache , btn , txt
from utils.connection import con
from utils import filters as f
from utils.tasks import app 
from flower.utils.broker import Broker
import time
from utils.tasks import editor
from utils.utils import join_checker , deleter , alert , file_checker
from celery.result import AsyncResult
import subprocess
from flower.utils.broker import Broker
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton




@Client.on_callback_query(f.bot_is_on, group=0)
async def callback_manager(bot, call):

    logger.warning(call.data)
    status = call.data.split(':')[0]
    
    user = con.user(chat_id=call.from_user.id)
    if user.lang:setting = con.setting(lang=user.lang)
    else:setting = con.setting()

    print(status)

    if status == 'join' :
        await joined_handler(bot , call , user , setting  )
    

    elif status.startswith('editor_'):
        await set_editor_quality(bot ,call  , user , setting )


    
    elif status == 'setting':
        await setting_handler(bot , call , user , setting  )
    
    elif status == 'plans' :
        await plans_call_handler(bot , call , user , setting )
    
    elif status == 'back_plans' :
        await back_to_plans(bot , call, user , setting  )
    
    elif status == 'status-editor' :
        await status_editor(bot , call )
    
    elif status == 'cancel-editor' : 
        await cancel_editor(bot , call )

#     elif status.startswith('editor_'):
#         await set_editor_quality(bot ,call  )

    elif status == 'block_user' :
        await block_user(bot , call )
    
    elif status == 'unblock_user' :
        await unblock_user(bot , call )
    
    elif status == 'add_volume' : 
        await add_volume_handler(bot , call , user , setting )
    





async def add_volume_handler(bot , call , user , setting ):
    status = call.data.split(':')[1]
    
    if status == 'channel' : 
        
        user_ref_link = f'https://t.me/{setting.bot.username}?start=ref_{call.from_user.id}'
        ref_text = f'{setting.texts.add_volume_with_ref_text}\n\n`{user_ref_link}`'
        share_text = f'{setting.texts.add_volume_with_ref_text_share}%0A%0A{user_ref_link}'
        share_link = f'https://t.me/share/url?url={share_text.replace(" " , "+")}'
        await bot.edit_message_text(chat_id = call.from_user.id , message_id = call.message.id  ,text = ref_text  , reply_markup = btn.ref_link(share_link))


    elif status == 'join' : 
        
        channels = setting.add_volume_channels
        text = setting.texts.add_volume_with_join_text
        await bot.edit_message_text(chat_id = call.from_user.id , message_id = call.message.id ,text = text , reply_markup = btn.add_volume_join_btn(channels))


    elif status == 'back' :
            plans = setting.plans
            await bot.edit_message_text(chat_id = call.from_user.id , text=setting.texts.add_vlime_text, message_id=call.message.id , reply_markup = btn.add_volume_btn(plans , setting , user ))


async def block_user(bot , call ):
    user_data=int(call.data.split(':')[1])
    user = con.user(chat_id=user_data  , is_active=False)
    await bot.edit_message_text(chat_id = call.message.chat.id , message_id = call.message.id , text = call.message.caption , reply_markup = btn.unblock_user(call.from_user.id))


async def unblock_user(bot , call ):
    user_data=int(call.data.split(':')[1])
    user = con.user(chat_id=user_data  , is_active=True)
    await bot.edit_message_text(chat_id = call.message.chat.id , message_id = call.message.id , text = call.message.caption , reply_markup = btn.block_user_btn(call.from_user.id))



async def set_editor_quality(bot, call, user, setting):
    vid_key = f'vid_data:{call.data.split(":")[2]}'
    vid_data = cache.redis.hgetall(vid_key)
    video_quality = call.data.split(':')[0].replace('editor_', '')
    
    
    if vid_data:
        file_checker_data = file_checker(unique_id=vid_data['unique_id'], quality=f'quality_{video_quality}')
        print(file_checker_data)
        
        if file_checker_data:
            await bot.delete_messages(call.from_user.id, call.message.id)
            await bot.send_video(call.from_user.id, video=file_checker_data['file_id'])
        else:
            # Update quality and other properties
            cache.redis.hset(vid_key, 'quality', f"quality_{video_quality}")
            data = cache.redis.hgetall(vid_key)
            
            # Convert string fields to appropriate types
            data['quality'] = f'quality_{video_quality}'
            data['task_id'] = 'none'
            data['width'] = int(data.get('width', '0'))
            data['height'] = int(data.get('height', '0'))
            data['duration'] = float(data.get('duration', '0.0'))            
            

            try:
                vid_editor_text = setting.texts.editor_progress_text
                editor_msg = await bot.edit_message_text(
                    chat_id=call.from_user.id,
                    text=vid_editor_text,
                    message_id=call.message.id,
                    reply_markup=btn.vid_editor_btn(vid_data=vid_key , setting = setting)
                )
                data['bot_msg_id'] = editor_msg.id
                print('#############################################')
                
                print(editor_msg.id)
                print('#############################################')
                await editor_msg.pin(both_sides=True)
                
                task = editor.delay(data)
                data['task_id'] = task.id
                cache.redis.hmset(vid_key , data)
                
            except Exception as e:
                logger.warning(e)






async def status_editor(bot , call ):
    broker = Broker(
        app.connection(connect_timeout=1.0).as_uri(include_password=True),
        broker_options=app.conf.broker_transport_options,
        broker_use_ssl=app.conf.broker_use_ssl,
    )
    async def queue_length():
        queues = await broker.queues(["celery"])
        print(queues)
        return queues[0].get("messages")
    await alert(bot , call , msg =txt.task_status(task_count=await queue_length()))
    
    

    
  




async def cancel_editor(bot , call ):
    try :
        user = con.user(chat_id=call.from_user.id , full_name=call.from_user.first_name)
        vid_data = cache.redis.hgetall(call.data.replace('cancel-editor:' , ''))
        task_id = vid_data['task_id']
        task = AsyncResult(task_id)
        task.revoke(terminate=True)
        user_file_size= int(float(vid_data['file_size']))
        con.user(chat_id=call.from_user.id , full_name=call.from_user.first_name , volume= user.volume + user_file_size)
        cache.redis.delete(call.data.replace('cancel-editor:' , ''))
        await alert(bot  ,call , msg= 'عملیات با موفقیت کنسل شد')
        await bot.delete_messages(call.from_user.id , call.message.id)
    except Exception as e :
        logger.error(e)













async def back_to_plans(bot , call , user, setting  ):
    plans = setting.plans
    await bot.edit_message_text(chat_id = call.from_user.id ,text=setting.texts.plans_text , message_id = call.message.id , reply_markup = btn.plans_btn(plans , setting , user ))



async def setting_handler(bot , call , user , setting  ):
    data = call.data.split(":")[1]


    if data.startswith('lang_'):
        lang = data.replace('lang_' , '')
        if user.lang != lang :
            user= con.user(chat_id = call.from_user.id , lang = lang)
            setting = con.setting(lang=user.lang)
            await bot.send_message(chat_id = call.from_user.id ,text = setting.texts.start_text, reply_markup = btn.user_panel_menu(setting , user ))
            await bot.edit_message_text(chat_id = call.from_user.id , text=setting.texts.setting_text, reply_markup=btn.setting_btn(user = user , setting=setting), message_id = call.message.id)

    elif data.startswith('quality_'):

   
        if data == user.quality :
            user = con.user(chat_id = call.from_user.id , quality = 'quality_0')
        else :
            user = con.user(chat_id = call.from_user.id , quality =data)
        await bot.edit_message_text(chat_id = call.from_user.id , text=setting.texts.setting_text, reply_markup=btn.setting_btn(user = user , setting=setting), message_id = call.message.id)




async def joined_handler(bot , call  , user , setting ):
        

        user = con.user(chat_id = call.from_user.id )
        if user.lang :setting = con.setting(lang = user.lang)
        else :setting = con.setting()

        channels = setting.channels
        not_join_channels = await join_checker(bot , call ,channels)
        if not_join_channels :
            await bot.send_message(call.from_user.id   , text = setting.texts.force_join_text  , reply_markup = btn.join_channels_url(not_join_channels , setting.texts.i_joined_btn_text))
            await alert(bot , call ,setting.texts.user_not_join_text)
            logger.info(f'user not join channel : {str(call.from_user.id)}')
        else :
            await bot.delete_messages(call.from_user.id , call.message.id)
            await bot.send_message(call.from_user.id , text = setting.texts.start_text)
            logger.info(f'user is join channel : {str(call.from_user.id)}')


async def plans_call_handler(bot , call  , user , setting ):
    call_plan_data = call.data.replace('plans:' , '')
    bot_id = setting.bot.id
    plan = None 
    for plan in setting.plans :
        if int(plan.id) ==  int(call_plan_data):
            payment = con.payment(amount=plan.price , chat_id=call.from_user.id , plan_id=plan.id , bot_id=bot_id)
            if user.lang and user.lang != 'fa' :await bot.edit_message_text(chat_id = call.from_user.id ,message_id = call.message.id ,  text = plan.description_en ,reply_markup = btn.payment_plan_btn(payment.url , user.lang) )
            else :await bot.edit_message_text(chat_id = call.from_user.id ,message_id = call.message.id ,  text = plan.description ,reply_markup = btn.payment_plan_btn(payment.url , user.lang) )
















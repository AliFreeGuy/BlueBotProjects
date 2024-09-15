# utils/tasks.py
from celery import Celery
import redis
import sys
from os.path import abspath, dirname
from dotenv import load_dotenv
from pathlib import Path
from pyrogram import Client
from pyrogram.errors import MessageIdInvalid
from datetime import datetime
from pyrogram.types import InlineKeyboardButton , InlineKeyboardMarkup , InputMediaVideo
import random
from celery.result import AsyncResult
from ffmpeg_progress_yield import FfmpegProgress
load_dotenv(override = True)
from os import environ as env
from celery.exceptions import SoftTimeLimitExceeded
import time


REDIS_HOST = env.get('REDIS_HOST')
REDIS_PORT = env.get('REDIS_PORT')
REDIS_DB= env.get('REDIS_DB')
REDIS_PASS = env.get('REDIS_PASS')
DEBUG = env.get('BOT_DEBUG')
PROXY = {"scheme": env.get("PROXY_SCHEME"),
         "hostname": env.get("PROXY_HOSTNAME"),
         "port": int(env.get("PROXY_PORT"))}
EDITOR_TTL = int(env.get('EDITOR_TTL'))


parent_dir = dirname(dirname(abspath(__file__)))
sys.path.insert(0, parent_dir)
from utils.connection import con 
from utils import cache , logger , btn
from utils.utils import delet_dir  , convert_data_types  , b_to_mb


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
app = Celery('tasks', broker=f'redis://localhost:6379/5', backend=f'redis://localhost:6379/5')
app.conf.timezone = 'UTC'

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json',],
    worker_concurrency=16,
    worker_prefetch_multiplier=1,
)


def progressbar(current, total , task_id=None ):
    percentage = current * 100 // total
    progress_bar = ""
    for i in range(20):
        if percentage >= (i + 1) * 5:progress_bar += "█"
        elif percentage >= i * 5 + 2:progress_bar += "▒"
        else:progress_bar += "░"
        date = datetime.now()
    progress_data = {'progress' : progress_bar ,'percentage' : percentage , 'text' :f"{progress_bar} {percentage} ",'date' : str(date) }
    if not r.exists(task_id):
        r.hmset(task_id, progress_data)
        progress_data['is_update'] = 'True'
    elif r.exists(task_id ):
        if int(float(r.hgetall(task_id)['percentage'])) != percentage :
            p = r.hgetall(task_id)
            last_pdate = datetime.strptime(p['date'], '%Y-%m-%d %H:%M:%S.%f')
            time_difference = date - last_pdate
            seconds_difference = time_difference.total_seconds()
            if int(seconds_difference) >= EDITOR_TTL :
                progress_data['is_update'] = 'True'
                r.hmset(task_id, progress_data)
            else :
                progress_data['is_update'] = 'Fasle'
        else :
            r.hmset(task_id, progress_data)
            progress_data['is_update'] = 'False'
    return progress_data



def cancel_markup( callback_data , setting ):
    btns = [[InlineKeyboardButton(text = '❌ کنسل', callback_data=callback_data),]]
    ads = setting.ads
    for ad in ads :
        if ad.url.startswith('https://t.me/'):
            btns.append([InlineKeyboardButton(text = ad.name, url=ad.url),])
    return InlineKeyboardMarkup(btns) 



@app.task(name='tasks.editor', bind=True, default_retry_delay=1)
def editor(self, data ):
    try :
        main_data = data
        setting = con.setting(lang='fa')
        data = convert_data_types(data)
        videos_folder = Path.cwd() / 'videos'
        videos_folder.mkdir(exist_ok=True)
        file_path = videos_folder / str(self.request.id)
        file_path.mkdir(exist_ok=True)
        cache.redis.hset(f'vid_data:{data["id"]}', 'task_id', str(self.request.id))
        video_name = f'{file_path}/{random.randint(999, 999999)}.mp4'
        thumb_name = f'{file_path}/{random.randint(999, 999999)}.jpeg'
        if DEBUG == 'True':bot = Client(f'editor-task_{random.randint(0 , 555)}', api_hash=setting.bot.api_hash, api_id=setting.bot.api_id, session_string=setting.bot.session_string)
        else:bot = Client('editor-task', api_hash=setting.bot.api_hash, api_id=setting.bot.api_id, session_string=setting.bot.session_string)


        with bot:
            cache.redis.hset(f'vid_data:{data["id"]}', 'file_path', str(file_path))
            message = bot.get_messages(int(setting.backup_channel), int(data['backup_msg_id']))
            def download_progress(current, total):
                pdata = int(float(f"{current * 100 / total:.1f}"))
                progress = progressbar(pdata, 400, str(self.request.id))
                if progress['is_update'] == 'True':
                    pbar = progress['text']
                    vid_editor_text = setting.texts.editor_progress_text
                    text = f'{vid_editor_text}\n\n📥{str(pbar)}'
                    msg_id = int(data['bot_msg_id'])
                    try:
                        bot.edit_message_text(chat_id=int(data['chat_id']), text=text, message_id=msg_id,
                                            reply_markup=cancel_markup(callback_data=f'cancel-editor:vid_data:{str(data["id"])}' , setting=setting))
                    
                    except Exception as e:
                        logger.warning(e)

            bot.download_media(message, progress=download_progress, file_name=video_name)



                #     # Apply video filters and settings
            quality =data['quality']
            crf_value = getattr(setting, quality, 30)  # پیش‌فرض به 30 تنظیم شده است
            logger.info(f'crf : {crf_value}')

            watermark = setting.watermark_text
            watermark_color = setting.watermark_color
            watermark_size = setting.watermark_size


            watermark = setting.watermark_text
            watermark_color = setting.watermark_color
            watermark_size = setting.watermark_size
            watermark_position = setting.watermark_position



            cmd = [
                "ffmpeg", "-i", video_name,    # نام فایل ورودی
                "-vcodec", "libx264",          # کدک ویدیو libx264
                "-crf", str(crf_value), 
                "-c:a", "aac",
                "-b:a", "64k",
                "-preset", "fast",             # استفاده از preset سریع‌تر
                # "-tune", "film",               # تنظیمات مخصوص فیلم
                                   # نام فایل خروجی
            ]
        #     cmd = [
        #     "ffmpeg", "-i", video_name,
        #     "-c:v", "libx265", 
        #     "-crf", str(crf_value),
        #     "-preset", "medium", 
        #     "-c:a", "aac",
        #     "-b:a", "96k",
        #     "-map_metadata", "0",
        #     "-movflags", "+faststart",
        #     "-threads", "16",
        #     '-tune' ,'film',
        # ]

            if watermark:
                position_mapping = {
                    'top_left': "x=10:y=10",
                    'top_right': "x=w-tw-10:y=10",
                    'bottom_left': "x=10:y=h-th-10",
                    'bottom_right': "x=w-tw-10:y=h-th-10",
                    'center': "x=(w-tw)/2:y=(h-th)/2"
                }

                position = position_mapping.get(watermark_position, "x=w-tw-10:y=h-th-10")
                
                cmd.extend([
                    "-vf", f"drawtext=text='{watermark}':fontcolor={watermark_color}@1.0:fontsize={watermark_size}:{position}"
                ])

            cmd.append(f'{file_path}/output.mp4')
            # # Process the video with ffmpeg and track progress
            ff = FfmpegProgress(cmd)
            for progress in ff.run_command_with_progress():
                pdata = int(str(progress).split('.')[0])
                pbar = progressbar(pdata * 2 + 100, 400, str(self.request.id))
                pbar_text = pbar['text']
                if pbar['is_update'] == 'True':
                    vid_editor_text = setting.texts.editor_progress_text
                    text = f'{vid_editor_text}\n\n📥{str(pbar_text)}'
                    msg_id = int(data['bot_msg_id']) 
                    try:
                        bot.edit_message_text(chat_id=int(data['chat_id']), text=text, message_id=msg_id,
                                            reply_markup=cancel_markup(callback_data=f'cancel-editor:vid_data:{str(data["id"])}' ,setting=setting))
                        
                    except MessageIdInvalid as e :
                        logger.error(data)
                        logger.error('messag ei dinvalid fuck you ')
                    
                    except Exception as e:
                        print(e)

            



            def upload_progress(current, total):
                pdata = int(float(f"{current * 100 / total:.1f}"))
                progress = progressbar(pdata + 300, 402, str(self.request.id))
                if progress['is_update'] == 'True':
                    pbar = progress['text']
                    vid_editor_text = setting.texts.editor_progress_text
                    text = f'{vid_editor_text}\n\n📥{str(pbar)}'
                    msg_id = int(data['bot_msg_id']) 
                    try:
                        bot.edit_message_text(chat_id=int(data['chat_id']), text=text, message_id=msg_id,
                                            reply_markup=cancel_markup(callback_data=f'cancel-editor:vid_data:{str(data["id"])}' , setting=setting))
                    except Exception as e:
                        logger.warning(e)

            
            ads = setting.ads
            logger.info(data)


            # بررسی و تبدیل duration
            duration = data.get('duration')
            if duration and isinstance(duration, str) and duration.isdigit():
                duration = int(duration)
            elif duration and isinstance(duration, str) and duration.replace('.', '', 1).isdigit():
                duration = int(float(duration))
            elif isinstance(duration, (int, float)):
                duration = int(duration)
            else:
                duration = 0  # در صورتی که مقدار معتبر نباشد، مقدار پیش‌فرض

            # output_data = bot.send_video(
            #     int(data['chat_id']),
            #     video=f'{file_path}/output.mp4',
            #     progress=upload_progress,
                
            # )
            ads = setting.ads
            logger.info(data)

            # بررسی و تبدیل duration
            duration = data.get('duration')
            if duration and isinstance(duration, str) and duration.isdigit():
                duration = int(duration)
            elif duration and isinstance(duration, str) and duration.replace('.', '', 1).isdigit():
                duration = int(float(duration))
            elif isinstance(duration, (int, float)):
                duration = int(duration)
            else:
                duration = None  # مقدار پیش‌فرض در صورت نامعتبر بودن

            # بررسی و تبدیل height
            height = data.get('height')
            if height and isinstance(height, str) and height.isdigit():
                height = int(height)
            elif isinstance(height, (int, float)):
                height = int(height)
            else:
                height = None  # مقدار پیش‌فرض در صورت نامعتبر بودن

            # بررسی و تبدیل width
            width = data.get('width')
            if width and isinstance(width, str) and width.isdigit():
                width = int(width)
            elif isinstance(width, (int, float)):
                width = int(width)
            else:
                width = None  # مقدار پیش‌فرض در صورت نامعتبر بودن

            # پارامترهای ارسال
            send_params = {
                'chat_id': int(data['chat_id']),
                'video': f'{file_path}/output.mp4',
                'progress': upload_progress,
                'reply_markup': btn.ads_btn(ads) if ads else [],
                
            }

            if duration is not None:
                send_params['duration'] = duration
            if height is not None:
                send_params['height'] = height
            if width is not None:
                send_params['width'] = width
            if data['thumb'] != 'none':
                file_id = data['thumb']
                thumb = bot.download_media(file_id, f'{file_path}/thumb.jpg')
                send_params['thumb'] = thumb
            
            
            
            
            
            if data['caption'] != 'none' :
                caption = f'{data["caption"]}\n\n{setting.texts.sign_text}'
         
            else :
                caption = setting.texts.sign_text
            
            send_params['caption'] = caption
            
            
            


            # ارسال ویدیو
            output_data = bot.send_video(**send_params)

            
            try :
                backup_caption = (main_data['backup_caption'] +f'\n❎ حجم قبلی: {main_data["file_size"]}\n✅ حجم جدید: {b_to_mb(output_data.video.file_size)}')
                bot.edit_message_media(
                    chat_id = int(setting.backup_channel),
                    message_id=int(main_data['backup_msg_id']),
                    media=InputMediaVideo(media = output_data.video.file_id ,caption=backup_caption ) , reply_markup  = btn.block_user_btn(int(data['chat_id'])))
            except Exception as e :print(e)
            cache.redis.hset(f'vid_data:{data["id"]}', 'file_id', output_data.video.file_id)
            bot.delete_messages(int(data["chat_id"]), int(data['bot_msg_id']))

        delet_dir(file_path)



    except Exception as e :
        delet_dir(file_path)
    
        logger.error(str(e))


def revoke_task(task_id):
    task_result = AsyncResult(task_id)
    task_result.revoke(terminate=True)  

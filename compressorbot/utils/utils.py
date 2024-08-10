from pyrogram.errors import UserNotParticipant
import os
import uuid
import jdatetime
from utils import cache
from utils.connection import con





def megabytes_to_gigabytes(mb):

    if mb is None:
        return 'نامشخص'
    try:
        return round(mb / 1024, 2)
    except (TypeError, ValueError):
        return 'نامشخص'


async def join_checker(cli , msg , channels ):
    not_join = []
    for channel in channels : 
        try :
            data = await cli.get_chat_member(int(channel.chat_id), msg.from_user.id )
        except UserNotParticipant :
            not_join.append(channel)
        except Exception as e  : print(e)
    return not_join




async def alert(client ,call , msg = None ):
    try :
        if msg is None : await call.answer('خطا لطفا دوباره تلاش کنید', show_alert=True)
        else : await call.answer(msg , show_alert = True)
    except Exception as e : print('alert ' , str(e))
    



async def deleter(client , call , message_id ):
    try :
        message_id = message_id
        msg_ids = []
        for x in range(100) :
            msg_ids.append(message_id + x)
        await client.delete_messages(call.from_user.id  ,msg_ids )
    except :pass












def b_to_mb(data):
    file_size_in_megabytes = data / (1024 * 1024)
    file_size = (f"{file_size_in_megabytes:.2f}")
    return float(file_size)


def delet_dir(path):
        os.system(f"rm -rf {path}")

def random_code():
    return uuid.uuid4()

def m_to_g(data):
    try :
        number = data
        result = number / 1000
        formatted_result = "{:.1f}".format(result)
        return formatted_result
    except Exception as e : print('m to g utils  ' , str(e))

def jdate(date_miladi):
    try :
        try :date_time = jdatetime.datetime.strptime(date_miladi, "%Y-%m-%dT%H:%M:%S.%fZ")
        except : date_time = jdatetime.datetime.strptime(date_miladi, "%Y-%m-%dT%H:%M:%SZ")
        date_shamsi = jdatetime.datetime.fromgregorian(datetime=date_time).replace(hour=0, minute=0, second=0, microsecond=0)
        current_date_shamsi = jdatetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        remaining_days = (date_shamsi - current_date_shamsi).days
        date = date_shamsi.strftime('%Y-%m-%d').split('-')
        date = f'{date[2]}-{date[1]}-{date[0]}'
        print(date)
        result = {
            'date': date,
            'day': remaining_days
        }
        return result
    except Exception as e : print('jdate utils ' , str(e))




def file_checker(unique_id , quality):
    vids_data = [cache.redis.hgetall(i) for i in cache.redis.keys(f'vid_data:*')]
    vid_data = None 
    for vid in vids_data :
        if vid.get('unique_id') == unique_id and vid.get('quality') == quality and vid.get('file_id') :
            vid_data = vid
    return vid_data





   





import jdatetime





def profile_text(user, setting):
    print(user)
    user_id = user.chat_id
    full_name = user.full_name
    plan_id = user.plan.id
    volume = user.volume
    expiry = user.expiry

    # تنظیم نام پلن
    plan_name = user.plan.name_en or user.plan.name or "Unknown Plan"

    # تبدیل حجم به گیگابایت
    volume_gb = volume / 1024

    # بررسی تگ پلن برای نمایش تاریخ پایان
    if user.plan.tag == 'free':
        if user.lang == 'fa':
            persian_date_str = 'نامحدود'
            date_label = '📅 تاریخ پایان اشتراک :'
        else:
            persian_date_str = 'Unlimited'
            date_label = '📅 Subscription Expiry Date:'
    elif expiry:
        expiry_date = expiry.split('T')[0]
        year, month, day = map(int, expiry_date.split('-'))

        if user.lang == 'fa':
            gregorian_date = jdatetime.date(year, month, day)
            persian_date_str = gregorian_date.strftime('%d-%m-%Y')
            date_label = '📅 تاریخ پایان اشتراک :'
        else:
            persian_date_str = expiry_date
            date_label = '📅 Subscription Expiry Date:'
    else:
        persian_date_str = '0'
        date_label = '📅 Subscription Expiry Date:' if user.lang != 'fa' else '📅 تاریخ پایان اشتراک :'
        if user.lang == 'fa':
            plan_name = 'خالی'

    # تولید متن پروفایل
    if user.lang == 'fa':
        text = f'''
🆔 آیدی اختصاصی : `{user_id}`
👤 نام کاربر : {full_name}
📦 پلن فعال : {plan_name if expiry else 'خالی'}
📊 حجم مانده : {volume_gb:.2f} گیگ
{date_label} {persian_date_str}

{setting.texts.user_profile_text}'''
    else:
        text = f'''
🆔 User ID: `{user_id}`
👤 Full Name: {full_name}
📦 Active Plan: {plan_name if expiry else 'No Active Plan'}
📊 Available Volume: {volume_gb:.2f} GB
{date_label} {persian_date_str}

{setting.texts.user_profile_text}'''

    return text



def task_status( task_count):
    return f'ویدیو های در صف انتظار {str(task_count)} لطفا صبور باشید'




def volume_limit(limit) :
    return f'حجم ویدیو بیشتر از حجم مجاز {str(limit)} مگ است برای حذف محدودیت ها بروروی افزایش حجم بزنید .' 



def help_iniline_text():
    text = f'''
برایه افزودن حجم به یک نفر به این شکل عمل کنید :

 @usernamebot chat_id +1000 

با زدن این و تایید کردن مقدار 1000 مگابایت به کاربر مورد نظر که چت ایدی انرا وارد کردید افزوده میشود 
و اگر میخاهید حجم کم کنید فقط کافیه - بزارید به جایه +'''
    
    return text



def user_information(user , username=None):
    user_id = user.chat_id
    full_name = user.full_name
    plan_id = user.plan
    volume = user.volume
    expiry = user.expiry

    plan_name = "نامشخص" if user.plan == None else user.plan
    volume_gb = volume / 1024
    if expiry:
        expiry_date = expiry.split('T')[0]
        year, month, day = map(int, expiry_date.split('-'))
        gregorian_date = jdatetime.date(year, month, day)
        persian_date_str = gregorian_date.strftime('%d-%m-%Y')
        date_label = '📅 تاریخ پایان اشتراک :'
    else:
        persian_date_str = 'بدون تاریخ'
        date_label = '📅 تاریخ پایان اشتراک :'
        plan_name = 'خالی'

    text = f'''
🆔 آیدی اختصاصی : `{user_id}`
🆔 یوزرنیم : @{str(username)}
👤 نام کاربر : {full_name}
📦 پلن فعال : {user.plan.name}
📊 حجم مانده : {volume_gb:.2f} گیگ

{date_label} {persian_date_str}'''

    return text
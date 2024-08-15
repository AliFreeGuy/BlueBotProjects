import jdatetime

def profile_text(user, setting):
    user_id = user.chat_id
    full_name = user.full_name
    plan_id = user.plan
    volume = user.volume
    expiry = user.expiry

    plan_name = "Unknown Plan"
    for plan in setting.plans:
        if plan.id == plan_id:
            plan_name = plan.name_en
            break

    volume_gb = volume / 1024

    if expiry:
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

    if user.lang == 'fa':
        text = f'''
🆔 آیدی اختصاصی : `{user_id}`
👤 نام کاربر : `{full_name}`
📦 پلن فعال : `{plan_name}`
📊 حجم قابل استفاده : `{volume_gb:.2f} گیگ`
{date_label} `{persian_date_str}`

`{setting.texts.user_profile_text}`'''

    else:
        text = f'''
🆔 User ID: `{user_id}`
👤 Full Name: `{full_name}`
📦 Active Plan: `{plan_name if expiry else 'No Active Plan'}`
📊 Available Volume: `{volume_gb:.2f} GB`
{date_label} `{persian_date_str}`

`{setting.texts.user_profile_text}`'''

    return text


def task_status( task_count):
    return f'ویدیو های در صف انتظار {str(task_count)} لطفا صبور باشید'




def volume_limit(limit) :
    return f'حجم ویدیو بیشتر از حجم مجاز {str(limit)} مگ است برای حذف محدودیت ها بروروی افزایش حجم بزنید .' 



def user_information(user):
    user_id = user.chat_id
    full_name = user.full_name
    plan_id = user.plan
    volume = user.volume
    expiry = user.expiry

    # تعیین نام پلن فعال
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

    # ساخت متن نهایی به زبان فارسی
    text = f'''
🆔 آیدی اختصاصی : `{user_id}`
👤 نام کاربر : `{full_name}`
📦 پلن فعال : `{plan_name}`
📊 حجم قابل استفاده : `{volume_gb:.2f} گیگ`
{date_label} `{persian_date_str}`'''

    return text
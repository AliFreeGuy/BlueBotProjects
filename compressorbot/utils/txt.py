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
            print(year)
            print(month)
            print(day)
            gregorian_date = jdatetime.date(year, month, day)
            persian_date_str = gregorian_date.strftime('%d-%m-%Y')
            date_label = 'تاریخ پایان اشتراک :'
        else:
            persian_date_str = expiry_date
            date_label = 'Subscription Expiry Date:'
    else:
        persian_date_str = '0'
        date_label = 'Subscription Expiry Date:' if user.lang != 'fa' else 'تاریخ پایان اشتراک :'
        if user.lang == 'fa':
            plan_name = 'خالی'

    if user.lang == 'fa':
        text = f'''
آیدی اختصاصی : `{user_id}`
نام کاربر : `{full_name}`
پلن فعال : `{plan_name}`
حجم قابل استفاده : `{volume_gb:.2f} گیگ`
{date_label} `{persian_date_str}`

`{setting.texts.user_profile_text}`'''

    else:
        text = f'''
User ID: `{user_id}`
Full Name: `{full_name}`
Active Plan: `{plan_name if expiry else 'No Active Plan'}`
Available Volume: `{volume_gb:.2f} GB`
{date_label} `{persian_date_str}`

`{setting.texts.user_profile_text}`'''

    return text

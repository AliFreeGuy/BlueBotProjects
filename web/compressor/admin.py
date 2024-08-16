import jdatetime
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import CompressorSettingModel, CompressorPlansModel, CompressorUser, CompressorTextModel

# تابع تبدیل تاریخ میلادی به شمسی
def to_jalali(date):
    if date:
        return jdatetime.datetime.fromgregorian(datetime=date).strftime('%Y/%m/%d %H:%M:%S')
    return '-'

# فیلتر سفارشی برای اشتراک‌ها
class SubscriptionFilter(admin.SimpleListFilter):
    title = _('فیلتر اشتراک‌ها')
    parameter_name = 'subscription'

    def lookups(self, request, model_admin):
        plans = CompressorPlansModel.objects.all()
        plan_choices = [(plan.id, plan.name) for plan in plans]
        plan_choices.append(('no_plan', _('بدون اشتراک')))
        return plan_choices

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'no_plan':
            # کاربران بدون پلن فعال
            return queryset.filter(expiry__lt=now)
        elif self.value():
            # کاربران با پلن خاص
            return queryset.filter(plan_id=self.value())
        return queryset

# ثبت مدل CompressorSettingModel در ادمین
@admin.register(CompressorSettingModel)
class CompressorSettingAdmin(admin.ModelAdmin):
    list_display = ['max_limit_video', 'quality_1', 'quality_2', 'quality_3']
    search_fields = ['max_limit_video', 'quality_1', 'quality_2', 'quality_3']
    list_filter = ['max_limit_video']

# ثبت مدل CompressorPlansModel در ادمین
@admin.register(CompressorPlansModel)
class CompressorPlansAdmin(admin.ModelAdmin):
    list_display = ['name', 'volume', 'price', 'day']
    search_fields = ['name']
    list_filter = ['price']

# ثبت مدل CompressorUser در ادمین
@admin.register(CompressorUser)
class CompressorUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'bot', 'lang', 'volume', 'expiry_jalali']
    list_filter = [SubscriptionFilter]
    
    def expiry_jalali(self, obj):
        return to_jalali(obj.expiry)
    expiry_jalali.short_description = 'expiry'

# ثبت مدل CompressorTextModel در ادمین
@admin.register(CompressorTextModel)
class CompressorTextAdmin(admin.ModelAdmin):
    list_display = ['bot', 'lang']
    search_fields = ['bot', 'lang']

# # ثبت مدل UserRefModel در ادمین
# @admin.register(UserRefModel)
# class UserRefAdmin(admin.ModelAdmin):
#     list_display = ['user', 'ref', 'bot', 'creation_jalali']
#     search_fields = ['user', 'ref', 'bot']
    
#     def creation_jalali(self, obj):
#         return to_jalali(obj.creation)
#     creation_jalali.short_description = 'creation'
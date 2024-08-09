from django.contrib import admin
from .models import LanguagesModel, ChannelsModel, AdsModels, BotsModel ,SendMessage
from django.utils.html import format_html
import jdatetime

@admin.register(LanguagesModel)
class LanguagesModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    list_filter = ['code']


@admin.register(ChannelsModel)
class ChannelsModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'link', 'chat_id']
    search_fields = ['name', 'link']
    list_filter = ['name', 'chat_id']


@admin.register(AdsModels)
class AdsModelsAdmin(admin.ModelAdmin):
    list_display = ['type', 'btn_name', 'btn_url', 'text']
    search_fields = ['type', 'btn_name']
    list_filter = ['type']


@admin.register(BotsModel)
class BotsModelAdmin(admin.ModelAdmin):
    list_display = ['type', 'username', 'bot_token', 'api_id', 'api_hash', 'session_string']
    search_fields = ['username', 'bot_token', 'api_id']
    list_filter = ['type', 'api_id']

    fieldsets = (
        ('Bot Information', {
            'fields': ('username', 'type', 'bot_token', 'api_id', 'api_hash', 'session_string')
        }),
    )








class BotsFilter(admin.SimpleListFilter):
    title = 'bots'
    parameter_name = 'bots'

    def lookups(self, request, model_admin):
        bots = BotsModel.objects.all()
        return [(bot.id, bot.username) for bot in bots]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(bots__id=self.value())
        return queryset




from django.contrib import admin
from .models import SendMessage, LanguagesModel, User, BotsModel, AdsModels

class SendMessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'creation')
    search_fields = ('message',)
    filter_horizontal = ('users',)

    # برای نمایش افقی فیلد users
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'users':
            kwargs['widget'] = admin.widgets.FilteredSelectMultiple(db_field.verbose_name, is_stacked=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(SendMessage, SendMessageAdmin)
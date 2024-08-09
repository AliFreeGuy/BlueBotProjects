from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from compressor.models import CompressorSettingModel, LanguagesModel, CompressorTextModel

@receiver(m2m_changed, sender=CompressorSettingModel.langs.through)
def handle_langs_change(sender, instance, action, pk_set, **kwargs):
    # دریافت تمام زبان‌ها بر اساس pk_set
    all_languages = LanguagesModel.objects.filter(pk__in=pk_set)

    if action == 'post_add':
        # اضافه کردن زبان‌ها
        added_languages = all_languages
        print(f"Languages added to CompressorSettingModel instance {instance.pk}:")
        for lang in added_languages:
            print(f" - {lang.name} ({lang.code})")
            # ایجاد CompressorTextModel برای زبان‌های اضافه‌شده
            if not CompressorTextModel.objects.filter(bot=instance.bot, lang=lang).exists():
                CompressorTextModel.objects.create(
                    bot=instance.bot,
                    lang=lang,)

    elif action == 'post_remove':
        # حذف زبان‌ها
        removed_languages = all_languages
        print(f"Languages removed from CompressorSettingModel instance {instance.pk}:")
        for lang in removed_languages:
            print(f" - {lang.name} ({lang.code})")
            # حذف CompressorTextModel برای زبان‌های حذف‌شده
            CompressorTextModel.objects.filter(bot=instance.bot, lang=lang).delete()

    elif action == 'post_clear':
        print(f"All languages removed from CompressorSettingModel instance {instance.pk}")
        # حذف تمام CompressorTextModel مربوط به این bot
        CompressorTextModel.objects.filter(bot=instance.bot).delete()

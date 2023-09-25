from django.contrib.admin import ModelAdmin, register

from .models import User


@register(User)
class UserAdmin(ModelAdmin):
    """Класс настройки раздела пользователей."""
    list_display = (
        'is_active',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    fields = (
        ('is_active',),
        ('username', 'email'),
        ('first_name', 'last_name'),
    )
    search_fields = ('email', 'username')
    empty_value_display = 'Значение отсутствует'
    list_filter =  ('is_active', 'first_name', 'email')
    save_on_top = True
    list_per_page = 10

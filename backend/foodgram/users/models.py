from django.contrib.auth.models import AbstractUser
from django.db import models
import unicodedata
from django.db.models import CheckConstraint, Q
from django.db.models.functions import Length

from core.validators import MinLenValidator, StrValidator

models.CharField.register_lookup(Length)


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=256,
        unique=True,
        help_text='Обязательно для заполнения.'
    )
    username = models.CharField(
        verbose_name='Уникальное имя пользователя',
        max_length=32,
        unique=True,
        help_text='Обязательно для заполнения.',
        validators=(
            MinLenValidator(min_len=3, field='username',),
            # StrValidator(field='username'),
        )
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=32,
        help_text='Обязательно для заполнения.',
        validators=(
            StrValidator(
                first_regex='[^а-яёА-ЯЁ -]+',
                second_regex='[^a-zA-Z -]+',
                field='Имя',
            ),
        ),
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=32,
        help_text='Обязательно для заполнения.',
        validators=(
            StrValidator(
                first_regex='[^а-яёА-ЯЁ -]+',
                second_regex='[^a-zA-Z -]+',
                field='Фамилия',
            ),
        ),
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=128,
        help_text='Придумайте пароль.'
    )
    is_active = models.BooleanField(
        verbose_name='Активирован',
        default=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = (
            CheckConstraint(
                check=Q(username__length__gte=3),
                name='\nusername is too short\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'

    @classmethod
    def normalize_email(cls, email: str) -> str:
        """Normalize the email address by lowercasing the domain part of it"""

        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = email_name.lower() + '@' + domain_part.lower()
        return email
    #
    # @classmethod
    # def normalize_username(cls, username: str) -> str:
    #     return unicodedata.normalize('NFKC', username).capitalize()

    def __normalize_human_names(self, name: str) -> str:
        """Нормализует имена и фамилии."""

        storage = [None] * len(name)
        title = True
        idx = 0
        for letter in name:
            letter = letter.lower()
            if title:
                if not letter.isalpha():
                    continue
                else:
                    letter = letter.upper()
                    title = False
            elif letter in ' -':
                title = True
            storage[idx] = letter
            idx += 1
        return ''.join(storage[:idx])

    def clean(self) -> None:
        self.first_name = self.__normalize_human_names(self.first_name)
        self.last_name = self.__normalize_human_names(self.last_name)
        return super().clean()


class Subscriptions(models.Model):
    """Подписки пользователей."""

    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        related_name='subscriptions',
        to=User,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name='Подписчики',
        related_name='subscribers',
        to=User,
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата подписки',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='\nПовторная подписка\n',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='\nНельзя подписаться на себя\n',
            ),
        )

    def __str__(self):
        return f'{self.user.username} подписка на {self.author.username}'

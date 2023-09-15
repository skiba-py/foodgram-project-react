from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Length
from PIL import Image

from core.validators import StrValidator, hex_color_validator

models.CharField.register_lookup(Length)

User = get_user_model()


class Tag(models.Model):
    """Тег для рецепта"""

    name = models.CharField(
        verbose_name='Тег',
        max_length=64,
        validators=(StrValidator(field='Название тэга'),),
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=8,
        unique=True,
        db_index=False,
    )
    slug = models.CharField(
        verbose_name='Слаг',
        max_length=64,
        unique=True,
        db_index=False,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, цвет — {self.color}'

    def clean(self) -> None:
        self.name = self.name.strip().lower()
        self.slug = self.slug.strip().lower()
        self.color = hex_color_validator(self.color)
        return super().clean()


class Ingredient(models.Model):
    """Ингредиент для рецепта"""

    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=64,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=16,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='поле уникально для игредиента',
            ),
            models.CheckConstraint(
                check=models.Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
            models.CheckConstraint(
                check=models.Q(measurement_unit__length__gt=0),
                name='\n%(app_label)s_%(class)s_measurement_unit is empty\n',
            ),
        )

    def __self__(self):
        return f'{self.name} {self.measurement_unit}'

    def clean(self) -> None:
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        return super().clean()


class Recipe(models.Model):
    """Модель рецепта"""

    name = models.CharField(
        verbose_name='Рецепт',
        max_length=64,
    )
    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        related_name='recipes',
        to=User,
        on_delete=models.SET_NULL,
        null=True,
    )
    tags = models.ManyToManyField(
        verbose_name='Тег',
        related_name='recipes',
        to=Tag,
    )
    ingredients = models.ManyToManyField(
        verbose_name='Ингредиенты',
        related_name='recipes',
        to=Ingredient,
        through='recipes.AmountIngredient',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes_images',
    )
    description = models.TextField(
        verbose_name='Описание блюда',
        max_length=1024,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=(
            MinValueValidator(1, 'Блюдо готово!',),
            MaxValueValidator(300, 'Очень долго(',),
        ),
    ),

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
            models.CheckConstraint(
                check=models.Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author.username}'

    def clean(self) -> None:
        self.name = self.name.capitalize()
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image.thumbnail(500, 500)
        image.save(self.image.path)


class AmountIngredient(models.Model):
    """Кол-во ингредиентов в блюде"""

    recipe = models.ForeignKey(
        verbose_name='Указывает на рецепты',
        related_name='ingredient',
        to=Recipe,
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        to=Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Кол-во ингредиентов',
        default=0,
        validators=(
            MinValueValidator(1, 'Нужно больше ингредиентов',),
            MaxValueValidator(30, 'Ингредиентов слишком много!'),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Кол-во ингредиентов'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients',),
                name='\n%(app_label)s_%(class)s ingredient alredy added\n',
            ),
        )

    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class Favorites(models.Model):
    """Избранные рецепты"""

    recipe = models.ForeignKey(
        verbose_name='Рецепты',
        related_name='favorites',
        to=Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='user_favorites',
        to=User,
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user',),
                name='\n%(app_label)s_%(class)s recipe is favorite alredy\n',
            ),
        )

    def __str__(self):
        return f'{self.user}: {self.recipe}'


class Carts(models.Model):
    """Рецепты в корзине"""
    recipe = models.ForeignKey(
        verbose_name='Рецепты в списке',
        related_name='in_carts',
        to=Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='user_carts',
        to=User,
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user',),
                name='\n%(app_label)s_%(class)s recipe is cart alredy\n',
            ),
        )

    def __str__(self):
        return f'{self.user}: {self.recipe}'

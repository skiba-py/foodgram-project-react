# Generated by Django 3.2 on 2023-09-14 11:45

import django.core.validators
from django.db import migrations, models

import core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AmountIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1, 'Нужно больше ингредиентов'), django.core.validators.MaxValueValidator(30, 'Ингредиентов слишком много!')], verbose_name='Кол-во ингредиентов')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Кол-во ингредиентов',
                'ordering': ('recipe',),
            },
        ),
        migrations.CreateModel(
            name='Carts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
            options={
                'verbose_name': 'Рецепт в списке покупок',
                'verbose_name_plural': 'Рецепты в списке покупок',
            },
        ),
        migrations.CreateModel(
            name='Favorites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
            options={
                'verbose_name': '',
                'verbose_name_plural': '',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Ингредиент')),
                ('measurement_unit', models.CharField(max_length=16, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Рецепт')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('image', models.ImageField(upload_to='recipes_images', verbose_name='Картинка')),
                ('description', models.TextField(max_length=1024, verbose_name='Описание блюда')),
            ],
            options={
                'verbose_name': ('Рецепт',),
                'verbose_name_plural': ('Рецепты',),
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, validators=[core.validators.StrValidator(field='Название тэга')], verbose_name='Тег')),
                ('color', models.CharField(max_length=8, unique=True, verbose_name='Цвет')),
                ('slug', models.CharField(max_length=64, unique=True, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
            },
        ),
    ]

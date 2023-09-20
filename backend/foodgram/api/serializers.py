from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from core.features import create_recipe_ingredients
from core.validators import ingredients_validator, tags_validator
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class ShortRecipeSerializer(ModelSerializer):
    """Сокращенный вариант сериализатора модели Recipe."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class UserSerializer(ModelSerializer):
    """Сериализтор модели User."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj: User) -> bool:
        """Проверка подписки."""

        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscriptions.filter(author=obj).exists()

    def create(self, validated_data: dict) -> User:
        """Создание нового пользователя."""

        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSubscribeSerializer(UserSerializer):
    """Вывод подписок пользователя."""

    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model= User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )
        read_only_fields = ('__all__',)

    def get_recipes_count(self, obj: User) -> int:
        return obj.recipes_count()


class TagSerializer(ModelSerializer):
    """Сериализатор модели Tag."""

    class Meta:
        model = Tag
        fields = ('__all__',)
        read_only_fields = ('__all__',)

    def validate(self, data: OrderedDict) -> OrderedDict:
        for attr, value in data.items():
            data[attr] = value.sttrip(' #').upper()
        return data


class IngredientSerializer(ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('__all__',)
        read_only_fields = ('__all__',)


class RecipeSerializer(ModelSerializer):
    """Сериализатор модели Recipe."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_cart', 'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = ('is_favorited', 'is_in_cart')

    def get_ingredients(self, recipe: Recipe):
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe: Recipe):
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_cart(self, recipe: Recipe):
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.carts.filter(recipe=recipe).exists()

    def validate(self, data: OrderedDict) -> OrderedDict:
        """Валидация данных при операциях с рецептом."""

        tags_id = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        tags = tags_validator(tags_id, Tag)
        ingredients = ingredients_validator(ingredients, Ingredient)
        data.update(
            {
                'tags': tags,
                'ingredients': ingredients,
                'author': self.context.get('request').user,
            }
        )
        return data

    def create(self, validated_data: dict) -> Recipe:
        """Создает рецепт."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.object.create(**validated_data)
        recipe.tags.set(tags)
        create_recipe_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe: Recipe, validated_data: dict):
        """Обновляет рецепт."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            create_recipe_ingredients(recipe, ingredients)
        recipe.save()
        return recipe

from collections import OrderedDict

from core.features import create_recipe_ingredients
from core.validators import ingredients_validator, tags_validator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F, QuerySet
from django.db.transaction import atomic
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    SerializerMethodField,
)

from recipes.models import Carts, Favorites, Ingredient, Recipe, Tag

User = get_user_model()


class ShortRecipeSerializer(ModelSerializer):
    """Сокращенный вариант сериализатора модели Recipe."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("__all__",)


class UserSerializer(UserCreateSerializer):
    """Сериализтор регистрации пользователя."""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class UserInfoSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователе"""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_is_subscribed(self, obj: User) -> bool:
        """Проверка подписки на пользователя."""
        request = self.context.get("request")
        return (
            request is not None
            and request.user.is_authenticated
            and obj.subscriptions.filter(user=request.user).exists()
        )


class UserSubscribeSerializer(UserInfoSerializer):
    """Вывод подписок пользователя."""

    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("__all__",)

    def get_recipes_count(self, obj: User) -> int:
        return obj.recipes.count()


class TagSerializer(ModelSerializer):
    """Сериализатор модели Tag."""

    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("__all__",)

    def validate(self, data: OrderedDict) -> OrderedDict:
        for attr, value in data.items():
            data[attr] = value.sttrip(" #").upper()
        return data


class IngredientSerializer(ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ("__all__",)


class RecipeSerializer(ModelSerializer):
    """Сериализатор модели Recipe."""

    author = UserInfoSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "is_favorited",
            "is_in_shopping_cart",
            "cooking_time",
        )

    def get_ingredients(self, recipe: Recipe) -> QuerySet[dict]:
        ingredients = recipe.ingredients.values(
            "id", "name", "measurement_unit", amount=F("recipe__amount")
        )
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and Favorites.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and Carts.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["cooking_time"] = int(data["cooking_time"])
        return data

    def validate(self, data: OrderedDict) -> OrderedDict:
        """Валидация данных при операциях с рецептом."""
        tags_id = self.initial_data.get("tags")
        ingredients = self.initial_data.get("ingredients")
        # images = self.initial_data.get("image")
        cooking_time = self.initial_data.get("cooking_time")
        if (
            not tags_id
            or not ingredients
            # or not images
            or int(cooking_time) < 1
        ):
            raise ValidationError("Недостаточно данных или данные невалидны.")
        tags = tags_validator(tags_id, Tag)
        ingredients = ingredients_validator(ingredients, Ingredient)
        data.update(
            {
                "tags": tags,
                "ingredients": ingredients,
                "author": self.context.get("request").user,
            }
        )
        return data

    @atomic
    def create(self, validated_data: dict) -> Recipe:
        """Создает рецепт."""
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        create_recipe_ingredients(recipe, ingredients)
        return recipe

    @atomic
    def update(self, recipe: Recipe, validated_data: dict):
        """Обновляет рецепт."""
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
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

from core.features import create_shopping_list
from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .mixins import AddDeleteMixin
from .pagination import PageLimitPagination
from .permissions import AuthorStaffOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer,
    UserSubscribeSerializer,
)
from recipes.models import Carts, Favorites, Ingredient, Recipe, Tag
from users.models import Subscriptions

User = get_user_model()


class UserViewSet(DjoserUserViewSet, AddDeleteMixin):
    """Вьюсет для работы с пользователями."""

    add_serializer = UserSubscribeSerializer
    link_model = Subscriptions
    pagination_class = PageLimitPagination

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request: WSGIRequest, id: int | str) -> Response:
        """Создает или удаляет связь между пользователями."""

    @subscribe.mapping.post
    def create_subscribe(self, request, id: int | str) -> Response:
        return self._create_relation(id)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id: int | str) -> Response:
        author = get_object_or_404(User, id=id)
        if not Subscriptions.objects.filter(
                user=request.user, author=author
        ).exists():
            return Response(
                {"errors": "Вы не подписаны на этого пользователя"},
                status=HTTP_400_BAD_REQUEST,
            )
        return self._delete_relation(Q(author__id=id))

    @action(methods=("get",), detail=False)
    def subscriptions(self, request) -> Response:
        """Подписки."""
        pages = self.paginate_queryset(
            User.objects.filter(subscriptions__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Вью для Тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вью для Игредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self) -> list[Ingredient]:
        """Получает queryset."""
        name: str = self.request.query_params.get("name")
        query = self.queryset
        if not name:
            return query

        starts_queryset = query.filter(name__istartswith=name)
        starts_names = (ing.name for ing in starts_queryset)
        contain_queryset = query.filter(name__icontains=name).exclude(
            name__in=starts_names
        )
        return list(starts_queryset) + list(contain_queryset)


class RecipeViewSet(ModelViewSet, AddDeleteMixin):
    """Вьюсет для Recipe."""

    queryset = Recipe.objects.select_related("author")
    serializer_class = RecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)
    add_serializer = ShortRecipeSerializer
    pagination_class = PageLimitPagination

    def get_queryset(self) -> QuerySet[Recipe]:
        """Получает queryset."""
        query = self.queryset
        tags: list = self.request.query_params.getlist("tags")
        if tags:
            query = query.filter(tags__slug__in=tags).distinct()
        author: str = self.request.query_params.get("author")
        if author:
            query = query.filter(author=author)

        if self.request.user.is_anonymous:
            return query

        is_in_shopping_cart: str = self.request.query_params.get(
            "is_in_shopping_cart"
        )
        if is_in_shopping_cart in ("1", "true"):
            query = query.filter(in_carts__user=self.request.user)
        elif is_in_shopping_cart in ("0", "false"):
            query = query.exclude(in_carts__user=self.request.user)
        is_favorited: str = self.request.query_params.get("is_favorited")
        if is_favorited in ("1", "true"):
            query = query.filter(favorites__user=self.request.user)
        elif is_favorited in ("0", "false"):
            query = query.exclude(favorites__user=self.request.user)
        return query

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request: WSGIRequest, pk: int | str) -> Response:
        """Добавляет или удаляет рецеп из Favorites."""

    @favorite.mapping.post
    def put_recipe_to_favorites(self, request, pk: int | str) -> Response:
        self.link_model = Favorites
        return self._create_relation(pk)

    @favorite.mapping.delete
    def remove_recipe_from_favorites(
        self, request: WSGIRequest, pk: int | str
    ) -> Response:
        self.link_model = Favorites
        recipe = get_object_or_404(Recipe, id=pk)
        if not Favorites.objects.filter(
                user=request.user, recipe=recipe
        ).exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        return self._delete_relation(Q(recipe__id=pk))

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk: int | str) -> Response:
        """Добавляет или удаляет рецеп из Cart."""

    @shopping_cart.mapping.post
    def put_recipe_to_cart(self, request, pk: int | str) -> Response:
        self.link_model = Carts
        return self._create_relation(pk)

    @shopping_cart.mapping.delete
    def remove_recipe_from_cart(self, request, pk: int | str) -> Response:
        self.link_model = Carts
        recipe = get_object_or_404(Recipe, id=pk)
        if not Carts.objects.filter(
                user=request.user, recipe=recipe
        ).exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        return self._delete_relation(Q(recipe__id=pk))

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request) -> Response | HttpResponse:
        """Скачивает файл Carts."""
        user = self.request.user
        filename = f"{user.username}_shopping_list.txt"
        shopping_list = create_shopping_list(user)
        response = HttpResponse(
            shopping_list, content_type="text.txt; charset=utf-8"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

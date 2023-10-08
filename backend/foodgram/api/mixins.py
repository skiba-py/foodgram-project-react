from django.contrib.auth import get_user_model
from django.db.models import Model, Q
from django.db.utils import IntegrityError
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND)

from users.models import Subscriptions

User = get_user_model()


class AddDeleteMixin:
    """Добавляет дополнительные методы: create и delete."""

    add_serializer: ModelSerializer | None = None
    link_model: Model | None = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def _create_relation(self, obj_id: int | str) -> Response:
        """Добавляет связь Many2Many."""

        if self.link_model == Subscriptions:
            try:
                author = User.objects.get(pk=obj_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Автор не существует.'},
                    status=HTTP_404_NOT_FOUND,
                )
        else:
            if not self.queryset.filter(pk=obj_id).exists():
                return Response(
                    {'error': 'Рецепт не существует.'},
                    status=HTTP_400_BAD_REQUEST,
                )

        obj = get_object_or_404(self.queryset, pk=obj_id)
        try:
            self.link_model(None, obj.pk, self.request.user.pk).save()
        except IntegrityError:
            return Response(
                {'error': 'Действие уже выполнено.'},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer: ModelSerializer = self.add_serializer(obj)
        return Response(serializer.data, HTTP_201_CREATED)

    def _delete_relation(self, q: Q) -> Response:
        """Удаляет связь Many2Many."""

        try:
            obj = self.link_model.objects.get(q & Q(user=self.request.user))
        except self.link_model.DoesNotExist:
            raise Http404(f"{self.link_model.__name__} не существует")

        if self.link_model != Subscriptions:
            if not self.queryset.filter(pk=obj.recipe.id).exists():
                return Response(
                    {'error': 'Рецепт не существует.'},
                    status=HTTP_400_BAD_REQUEST,
                )

        obj.delete()
        return Response(status=HTTP_204_NO_CONTENT)

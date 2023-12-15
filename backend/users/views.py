from django.shortcuts import get_object_or_404
from djoser import signals, views
from rest_framework import exceptions, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import CustomPaginator
from api.serializers import SubscribeUpdateSerializer, CustomUserSerializer, SubscribeSerializer

from .models import Subscribe, User


class CustomUserViewSet(views.UserViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPaginator

    def get_permissions(self):
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()


    def perform_create(self, serializer, *args, **kwargs):
        serializer.is_valid()
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        """Подписка."""
        subscriptions = User.objects.filter(
            subscribing__user=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscribeSerializer(
            page,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Добавление/удаление подписки."""
        get_object_or_404(User, id=id)
        data = {
            'author':id,
            'user':request.user.id
        }

        serializer = SubscribeUpdateSerializer(

                data=data,
                context={"request": request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        get_object_or_404(User, id=id)
        user = request.user
        obj = Subscribe.objects.filter(
            user=user, author=id
        )
        if obj.exists():
            obj.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            'Подписки не существует',
            status=status.HTTP_400_BAD_REQUEST
        )

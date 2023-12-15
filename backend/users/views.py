from django.shortcuts import get_object_or_404
from djoser import signals, views
from rest_framework import exceptions, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import CustomPaginator
from api.serializers import CustomUserSerializer, SubscribeSerializer

from .models import Subscribe, User


class CustomUserViewSet(views.UserViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPaginator

    def get_permissions(self):
        if self.action in [
            'subscribe', 'subscriptions', 'me', 'delete_subscribe'
        ]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        if (
            'first_name' not in request.data.keys()
            or request.data['first_name'] is None
        ):
            raise exceptions.ValidationError(
                detail='Отсутствует имя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if (
            'last_name' not in request.data.keys()
            or request.data['last_name'] is None
        ):
            raise exceptions.ValidationError(
                detail='Отсутствует фамилия!',
                code=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

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
    def subscribe(self, request, **kwargs):
        """Добавление/удаление подписки."""
        user = request.user
        author = get_object_or_404(
            User, id=self.kwargs.get('id')
        )

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            #serializer.save()
            Subscribe.objects.create(user=user, author=author)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(
            User, pk=self.kwargs.get('id')
        )
        try:
            Subscribe.objects.get(
                user=user, author=author
            ).delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        except Subscribe.DoesNotExist:
            return Response(
                'Подписки не существует',
                status=status.HTTP_400_BAD_REQUEST
            )

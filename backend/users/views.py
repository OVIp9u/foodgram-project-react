from api.pagination import CustomPaginator
from api.serializers import CustomUserSerializer, SubscribeSerializer
from django.shortcuts import get_object_or_404
from djoser import signals, views
from rest_framework import exceptions, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Subscribe, User


class CustomUserViewSet(views.UserViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPaginator

    def get_permissions(self):
        if self.action in ['subscribe', 'subscriptions', 'me']:
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
        if page is not None:
            serializer = SubscribeSerializer(
                page,
                context={'request': request},
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=[permissions.IsAuthenticated]
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
            Subscribe.objects.create(user=user, author=author)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            try:
                subscription = Subscribe.objects.get(
                    user=user, author=author
                )
                subscription.delete()
                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )
            except Exception:
                return Response(
                    data='Ошибка удаления подписки',
                    status=status.HTTP_400_BAD_REQUEST
                )

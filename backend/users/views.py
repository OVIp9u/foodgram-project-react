from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import CustomUserSerializer, SubscribeSerializer
from api.pagination import CustomPaginator
from .models import User, Subscribe
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly


class CustomUserViewSet(views.UserViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    pagination_class = CustomPaginator

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated,]
    )
    def subscriptions(self, request):
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
        permission_classes=[permissions.IsAuthenticated,]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(
            User, id=self.kwargs.get('id')
        )

        match request.method:
            case 'POST':
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
            case 'DELETE':
                subscription = get_object_or_404(
                    Subscribe,
                    user=user,
                    author=author
                )
                subscription.delete()
                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )

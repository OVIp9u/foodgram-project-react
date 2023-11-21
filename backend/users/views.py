from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import CustomUserSerializer, SubscribeSerializer

from .models import Subscribe, User


class CustomUserViewSet(views.UserViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        subscription = get_object_or_404(
            Subscribe,
            author=author,
            user=user,
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(
        permission_classes=(permissions.IsAuthenticated,),
        detail=False
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

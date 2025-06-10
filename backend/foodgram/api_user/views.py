from djoser.views import UserViewSet

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Subscription, User

from api.pagination import SizeLimitPagination
from api_recipes.serializers import UserWithRecipeSerializer
from .serializers import AvatarUploadSerializer, UserAccountSerializer


class UserAccountViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserAccountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = SizeLimitPagination

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['put', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def avatar(self, request, id):
        if request.method == 'PUT':
            serializer = AvatarUploadSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.user.avatar:
            request.user.avatar.delete()
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribed__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = UserWithRecipeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, id):
        subscriber = request.user
        user = self.get_object()
        sub = Subscription.objects.filter(user=subscriber, subscribed_to=user)
        if request.method == 'POST':
            if subscriber == user or sub.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(user=subscriber, subscribed_to=user)
            serializer = UserWithRecipeSerializer(
                user,
                context={
                    'request': request,
                    'recipes_limit': request.query_params.get('recipes_limit')
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not sub.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        sub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

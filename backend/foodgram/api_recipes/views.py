from django.db.models import F, Sum
from django.http import FileResponse
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from core.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart
)

from api.pagination import SizeLimitPagination
from api.permissions import IsAuthorized
from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    IngredientSerializer,
    CreateRecipeSerializer,
    RecipeSerializer,
    ShortRecipeSerializer
)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorized
    ]
    pagination_class = SizeLimitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = self.get_object()
        shopcart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if shopcart.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        if not shopcart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shopcart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = self.get_object()
        fav_obj = Favorite.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if fav_obj.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        if not fav_obj.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        fav_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__in=request.user.shopping_cart.values('recipe'))
            .values(
                name=F('ingredient__name'),
                unit=F('ingredient__measurement_unit')
            )
            .annotate(amount=Sum('amount'))
            .order_by('name')
        )
        buy_list = 'Список покупок:'
        if ingredients:
            for ingred in ingredients:
                buy_list += (
                    f'\n{ingred["name"]} - '
                    f'{ingred["amount"]} ({ingred["unit"]})'
                )
        else:
            buy_list += '\nПусто!'
        return FileResponse(
            buy_list,
            filename='shoplist.txt',
            as_attachment=True,
            content_type='text/plain'
        )

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk):
        recipe = self.get_object()
        link = reverse('short-link', kwargs={'short_link': f'{recipe.id:x}'})
        url = request.build_absolute_uri(link)
        return Response({'short-link': url}, status=status.HTTP_200_OK)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter

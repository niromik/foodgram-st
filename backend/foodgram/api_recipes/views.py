from django.db.models import F, Sum
from django.http import FileResponse
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from core.models import (
    UserFavoriteRecipe,
    Ingredient,
    RecipeIngredient,
    CulinaryRecipe,
    UserShoppingCart
)

from api.pagination import CustomPageNumberPagination
from api.permissions import IsOwnerOrReadOnly
from .filters import IngredientSearchFilter, RecipeCustomFilter
from .serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeDetailSerializer,
    RecipeSummarySerializer
)


class RecipeController(ModelViewSet):
    queryset = CulinaryRecipe.objects.all()
    serializer_class = RecipeDetailSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    ]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeCustomFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='shopping_cart'
    )
    def manage_cart(self, request, pk):
        user = request.user
        recipe = self.get_object()
        cart_item = UserShoppingCart.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if cart_item.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            UserShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeSummarySerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        if not cart_item.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='favorite'
    )
    def manage_favorites(self, request, pk):
        user = request.user
        recipe = self.get_object()
        favorite = UserFavoriteRecipe.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            UserFavoriteRecipe.objects.create(user=user, recipe=recipe)
            return Response(
                RecipeSummarySerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        if not favorite.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def export_shopping_list(self, request):
        cart_items = request.user.shopping_cart.select_related('recipe')
        recipe_ids = [item.recipe_id for item in cart_items]
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe_id__in=recipe_ids)
            .values(
                name=F('ingredient__name'),
                unit=F('ingredient__measurement_unit')
            )
            .annotate(amount=Sum('amount'))
            .order_by('name')
        )
        shopping_list = "Список покупок:\n"
        shopping_list += "\n".join(
            f"{item['name']} - {item['amount']} ({item['unit']})"
            for item in ingredients
        ) if ingredients else "Ваша корзина пуста"
        return FileResponse(
            shopping_list,
            filename='shopping_list.txt',
            as_attachment=True,
            content_type='text/plain'
        )

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def generate_shareable_link(self, request, pk):
        recipe = self.get_object()
        hex_id = f"{recipe.id:x}"
        path = reverse('short-link', kwargs={'short_link': hex_id})
        full_url = request.build_absolute_uri(path)
        return Response(
            {'short-link': full_url},
            status=status.HTTP_200_OK
        )


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientSearchFilter

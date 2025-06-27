from django_filters.filters import CharFilter, ChoiceFilter
from django_filters.rest_framework import FilterSet

from core.models import Ingredient, CulinaryRecipe


class IngredientSearchFilter(FilterSet):
    """
    Фильтр для поиска ингредиентов по частичному совпадению имени.
    """

    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeCustomFilter(FilterSet):
    """
    Кастомный фильтр для рецептов с дополнительными булевыми флагами.
    """
    CHOICES = (
        (0, False),
        (1, True)
    )
    is_favorited = ChoiceFilter(
        choices=CHOICES,
        method='filter_is_favorited',
        label='Is in favorites'
    )
    is_in_shopping_cart = ChoiceFilter(
        choices=CHOICES,
        method='filter_is_in_shopping_cart',
        label='Is in shopping cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        """
        Фильтрация рецептов, добавленных в избранное текущим пользователем.
        """
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(users_in_favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрация рецептов, добавленных в корзину текущим пользователем."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(users_in_shopcart__user=user)
        return queryset

    class Meta:
        model = CulinaryRecipe
        fields = [
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        ]

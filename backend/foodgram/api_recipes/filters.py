from django_filters.filters import CharFilter, ChoiceFilter
from django_filters.rest_framework import FilterSet

from core.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    STATUS_CHOICES = (
        (0, False),
        (1, True),
        (False, False),
        (True, True)
    )
    is_favorited = ChoiceFilter(
        choices=STATUS_CHOICES,
        method='get_is_favorited'
    )
    is_in_shopping_cart = ChoiceFilter(
        choices=STATUS_CHOICES,
        method='get_is_in_shopping_cart'
    )

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return Recipe.objects.filter(users_in_favorite__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return Recipe.objects.filter(users_in_shopcart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = [
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        ]

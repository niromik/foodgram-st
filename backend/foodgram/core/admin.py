from django.contrib import admin
from django.contrib.admin import register, ModelAdmin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Subscription,
    User
)


@register(Favorite)
class FavoriteConfig(ModelAdmin):
    list_display = [
        'id',
        'user',
        'recipe'
    ]


@register(Ingredient)
class IngredientConfig(ModelAdmin):
    list_display = [
        'id',
        'name',
        'measurement_unit'
    ]
    search_fields = ['name', 'measurement_unit']
    list_filter = ['measurement_unit']


@register(IngredientInRecipe)
class IngredientInRecipeConfig(ModelAdmin):
    list_display = [
        'id',
        'recipe',
        'ingredient',
        'amount'
    ]


@register(Recipe)
class RecipeConfig(ModelAdmin):
    list_display = [
        'id',
        'author',
        'ingredients',
        'name',
        'image',
        'text',
        'cooking_time',
        'favorites',
        'created'
    ]
    list_filter = ['name', 'author']
    search_fields = ['name', 'author__username']

    @admin.display(description='Количество ингредиентов')
    def ingredients(self, obj):
        return obj.ingredients.count()

    @admin.display(description='Добвлено в Избранное')
    def favorites(self, obj):
        return obj.users_in_favorite.count()


@register(ShoppingCart)
class ShoppingCartConfig(ModelAdmin):
    list_display = [
        'id',
        'user',
        'recipe'
    ]


@register(Subscription)
class SubscriptionConfig(ModelAdmin):
    list_display = [
        'id',
        'user',
        'subscribed_to'
    ]
    search_fields = ['user__username', 'subscribed_to__username']
    list_filter = ['user', 'subscribed_to']


@register(User)
class UserConfig(UserAdmin):
    list_display = [
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'avatar'
    ]
    list_filter = ['username', 'email']
    search_fields = ['username', 'email']

from django.contrib import admin
from django.contrib.admin import register, ModelAdmin
from django.contrib.auth.admin import UserAdmin

from .models import (
    UserFavoriteRecipe,
    Ingredient,
    RecipeIngredient,
    CulinaryRecipe,
    UserShoppingCart,
    Subscription,
    User
)


@register(UserFavoriteRecipe)
class FavoriteAdmin(ModelAdmin):
    list_display = [
        'id',
        'user',
        'recipe'
    ]


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = [
        'id',
        'name',
        'measurement_unit'
    ]
    search_fields = ['name', 'measurement_unit']
    list_filter = ['measurement_unit']


@register(RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    list_display = [
        'id',
        'recipe',
        'ingredient',
        'amount'
    ]


@register(CulinaryRecipe)
class CulinaryRecipeAdmin(ModelAdmin):
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

    @admin.display(description='Число ингредиентов')
    def ingredients(self, obj):
        return obj.ingredients.count()

    @admin.display(description='В избранном')
    def favorites(self, obj):
        return obj.users_in_favorite.count()


@register(UserShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = [
        'id',
        'user',
        'recipe'
    ]


@register(Subscription)
class UserFollowAdmin(ModelAdmin):
    list_display = [
        'id',
        'user',
        'subscribed_to'
    ]
    search_fields = ['user__username', 'subscribed_to__username']
    list_filter = ['user', 'subscribed_to']


@register(User)
class CustomUserAdmin(UserAdmin):
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

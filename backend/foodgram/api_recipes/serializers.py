from drf_extra_fields import fields as drf_fields
from rest_framework import serializers

from api_user.serializers import UserAccountSerializer
from core.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    User
)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount'
        ]


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=1
    )

    class Meta:
        model = IngredientInRecipe
        fields = [
            'id',
            'amount'
        ]


class RecipeSerializer(serializers.ModelSerializer):
    author = UserAccountSerializer()
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_amounts',
        many=True
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user:
            return user.is_authenticated and Favorite.objects.filter(
                user__exact=user,
                recipe__exact=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user:
            return user.is_authenticated and ShoppingCart.objects.filter(
                user__exact=user,
                recipe__exact=obj
            ).exists()
        return False

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        ]


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientInRecipeSerializer(
        many=True
    )
    image = drf_fields.Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'name',
            'image',
            'text',
            'cooking_time',
            'ingredients'
        ]

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Картинка является обязательным полем.'
            )
        return image

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Ингредиенты являются обязательным полем.'
            )
        ids = [ingredient['ingredient'].id for ingredient in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return ingredients

    def add_ingredients(self, recipe, ingredients):
        return IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = self.validate_ingredients(
            validated_data.pop('ingredients', None)
        )
        instance.ingredient_amounts.all().delete()
        self.add_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context=self.context
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class UserWithRecipeSerializer(UserAccountSerializer):
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.ReadOnlyField(
        source='recipes.count'
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        ]

    def get_recipes(self, obj):
        request = self.context.get('request')
        query_params = request.query_params
        recipes = obj.recipes.all()
        recipes_limit = query_params.get('recipes_limit')
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(
            recipes,
            context={'request': request},
            many=True
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = [
            'user',
            'recipe'
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = [
            'user',
            'recipe'
        ]

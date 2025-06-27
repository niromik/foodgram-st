from drf_extra_fields import fields as drf_fields
from rest_framework import serializers

from api_user.serializers import CustomUserSerializer
from core.models import (
    UserFavoriteRecipe,
    Ingredient,
    RecipeIngredient,
    CulinaryRecipe,
    UserShoppingCart,
    User
)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте."""
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
        model = RecipeIngredient
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
        model = RecipeIngredient
        fields = [
            'id',
            'amount'
        ]


class RecipeDetailSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
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
            return user.is_authenticated and UserFavoriteRecipe.objects.filter(
                user__exact=user,
                recipe__exact=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user:
            return user.is_authenticated and UserShoppingCart.objects.filter(
                user__exact=user,
                recipe__exact=obj
            ).exists()
        return False

    class Meta:
        model = CulinaryRecipe
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


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientInRecipeSerializer(
        many=True
    )
    image = drf_fields.Base64ImageField()

    class Meta:
        model = CulinaryRecipe
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
                'Изображение рецепта обязательно для заполнения.'
            )
        return image

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент.'
            )
        ingredient_ids = [item['ingredient'].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return ingredients

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            )
            for item in ingredients_data
        ]
        return RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = CulinaryRecipe.objects.create(**validated_data)
        self._create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = self.validate_ingredients(
            validated_data.pop('ingredients', None)
        )
        if ingredients_data is not None:
            instance.ingredient_amounts.all().delete()
            self._create_recipe_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeDetailSerializer(
            instance,
            context=self.context
        ).data


class RecipeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CulinaryRecipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class UserSubscriptionSerializer(CustomUserSerializer):
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
        return RecipeSummarySerializer(
            recipes,
            context={'request': request},
            many=True
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavoriteRecipe
        fields = [
            'user',
            'recipe'
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserShoppingCart
        fields = [
            'user',
            'recipe'
        ]

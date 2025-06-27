from django.urls import path, include
from rest_framework.routers import SimpleRouter

from api_recipes.views import IngredientViewSet, RecipeController
from api_user.views import CustomUserViewSet

router = SimpleRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeController)
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

from django.urls import path, include
from rest_framework.routers import SimpleRouter

from api_recipes.views import IngredientViewSet, RecipeViewSet
from api_user.views import UserAccountViewSet

router = SimpleRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserAccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

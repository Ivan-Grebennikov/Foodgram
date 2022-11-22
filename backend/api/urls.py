from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionViewSet,
    TagViewSet,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()

router.register(
    'tags', TagViewSet, basename='tags'
)

router.register(
    'ingredients', IngredientViewSet, basename='ingredients'
)

router.register(
    'recipes', RecipeViewSet, basename='recipes'
)

router.register(
    'users', SubscriptionViewSet, basename='subscriptions'
)

urlpatterns = [
    path('', include(router.urls)),
]

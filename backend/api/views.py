
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from utils.serializers import ReadOnlyRecipeSerializer
from utils.services import create_shopping_cart, user_related_field_handler

from .filters import IngredientsSearchFilter, RecipesFilter
from .permissions import RecipePermissions
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientsSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (RecipePermissions,)

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()

        if user.is_authenticated:

            favorited_subquery = Favorite.objects.filter(
                user=user, recipe=OuterRef('pk')
            )

            in_shopping_cart_subquery = ShoppingCart.objects.filter(
                user=user, recipe=OuterRef('pk')
            )

            return queryset.annotate(
                is_favorited=Exists(favorited_subquery)).annotate(
                    is_in_shopping_cart=Exists(in_shopping_cart_subquery)
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('POST', 'DELETE'),
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):

        return user_related_field_handler(
            request=request,
            field_name='recipe',
            instance=self.get_object(),
            relation_model_cls=Favorite,
            relation_szr_cls=FavoriteSerializer,
            instance_szr_cls=ReadOnlyRecipeSerializer,
        )

    @action(detail=True, methods=('POST', 'DELETE'),
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):

        return user_related_field_handler(
            request=request,
            field_name='recipe',
            instance=self.get_object(),
            relation_model_cls=ShoppingCart,
            relation_szr_cls=ShoppingCartSerializer,
            instance_szr_cls=ReadOnlyRecipeSerializer,
        )

    @action(detail=False, methods=('GET',),
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=ReadOnlyRecipeSerializer)
    def download_shopping_cart(self, request):

        response = HttpResponse(
            create_shopping_cart(request.user),
            content_type='text/plain; charset=UTF-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt'
        )

        return response

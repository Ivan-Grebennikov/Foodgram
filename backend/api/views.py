from collections import defaultdict

from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from users.models import Subscription, User

from .filters import IngredientsSearchFilter, RecipesFilter
from .permissions import RecipePermissions
from .serializers import (
    FollowingUserSerializer,
    IngredientSerializer,
    ReadOnlyRecipeSerializer,
    RecipeSerializer,
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
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=ReadOnlyRecipeSerializer)
    def favorite(self, request, pk):
        user = request.user
        recipe = self.get_object()

        if request.method == 'POST':

            if Favorite.objects.filter(
                    user=user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    {'errors': 'Recipe is already in favorites.'}
                )

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)

        user.favorite.filter(recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('POST', 'DELETE'),
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=ReadOnlyRecipeSerializer)
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = self.get_object()

        if request.method == 'POST':

            if ShoppingCart.objects.filter(
                    user=user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    {'errors': 'Recipe is already in shopping cart.'}
                )

            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_200_OK)

        user.shopping_cart.filter(recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',),
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=ReadOnlyRecipeSerializer)
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = user.shopping_cart.all()

        shopping_cart_dict = defaultdict(int)

        for item in shopping_cart_items:
            recipe = item.recipe
            ingredients = recipe.ingredients.all()
            for ingredient in ingredients:
                recipe_ingredient = RecipeIngredient.objects.filter(
                    recipe=recipe,
                    ingredient=ingredient
                ).first()
                shopping_cart_dict[str(ingredient)] += recipe_ingredient.amount

        shopping_cart = '\n'.join(
            f'{ingredient} - {amount}'
            for ingredient, amount in shopping_cart_dict.items()
        )

        response = HttpResponse(
            shopping_cart, content_type='text/plain; charset=UTF-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt'
        )

        return response


class SubscriptionViewSet(viewsets.GenericViewSet):

    @action(detail=True, methods=('POST', 'DELETE'),
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=FollowingUserSerializer)
    def subscribe(self, request, pk):
        # need validation
        user = request.user
        following = get_object_or_404(User, pk=pk)

        if request.method == 'POST':

            if Subscription.objects.filter(
                    user=user, following=following).exists():
                raise serializers.ValidationError(
                    {'errors': 'User has already been subscribed.'}
                )

            if user == following:
                raise serializers.ValidationError(
                    {'errors': 'Can\'t subscribe to self.'}
                )

            Subscription.objects.create(user=user, following=following)
            serializer = self.get_serializer(instance=following)
            return Response(serializer.data, status=status.HTTP_200_OK)

        user.following.filter(following=following).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',),
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=FollowingUserSerializer)
    def subscriptions(self, request):
        user = request.user

        subscriptions = Subscription.objects.filter(user=user)

        followings = []
        for s in subscriptions:
            followings.append(s.following)

        page = self.paginate_queryset(followings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(instance=followings, many=True)
        return Response(serializer.data)

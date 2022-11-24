from django_filters import rest_framework as filters
from rest_framework import filters as rest_framework_filters

from recipes.models import Recipe, Tag


class RecipesFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()
    author = filters.NumberFilter(
        'author__id',
        lookup_expr='iexact'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited', 'is_in_shopping_cart',
            'author', 'tags',
        )


class IngredientsSearchFilter(rest_framework_filters.SearchFilter):
    search_param = 'name'

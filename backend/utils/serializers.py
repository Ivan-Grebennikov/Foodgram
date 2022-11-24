from rest_framework import serializers

from recipes.models import Recipe


class ReadOnlyRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        read_only_fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        model = Recipe

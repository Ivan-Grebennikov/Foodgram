from collections import defaultdict

from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.serializers import UserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id', 'name', 'color', 'slug',
        )
        read_only_access = (
            'id',
        )
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id', 'name', 'measurement_unit',
        )
        read_only_access = (
            'id',
        )
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True, read_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'text', 'author', 'image',
            'cooking_time', 'ingredients', 'tags',
            'is_favorited', 'is_in_shopping_cart',
        )
        model = Recipe

    def validate_ingredients(self, ingredients_data):

        errors = defaultdict(list)

        if ingredients_data is None:
            errors['ingredients'].append(
                'Missing field or empty value.'
            )

        for ingredient_data in ingredients_data:
            id = ingredient_data.get('id')
            if id is None:
                errors['ingredients'].append('Missing field \'id\'.')
                continue

            ingredient = Ingredient.objects.filter(pk=id)
            if not ingredient.exists():
                errors['ingredients'].append(
                    f'Ingredient with id = {id} not found.'
                )

            amount = ingredient_data.get('amount')
            if amount is None:
                errors['ingredients'].append('Missing field \'amount\'.')
                continue

            if type(amount) not in (int, str):
                errors['ingredients'].append(
                    'Field \'amount\' must be a number.'
                )
                continue

            if type(amount) == str and not amount.isdigit():
                errors['ingredients'].append(
                    'Field \'amount\' must be a number.'
                )
                continue

            if int(amount) <= 0:
                errors['ingredients'].append(
                    'Field \'amount\' must be greater than 0.'
                )
                continue

        if errors:
            raise serializers.ValidationError(detail=errors)

    def validate_tags(self, tags_data):

        errors = defaultdict(list)

        if tags_data is None:
            errors['tags'].append(
                'Missing field or empty value.'
            )

        for tag_id in tags_data:
            tag = Tag.objects.filter(pk=tag_id)
            if not tag.exists():
                errors['tags'].append(
                    f'Tag with id = {tag_id} not found.'
                )

        if errors:
            raise serializers.ValidationError(detail=errors)

    def create(self, validated_data):

        ingredients_data = self.initial_data.get('ingredients')
        tags_data = self.initial_data.get('tags')

        self.validate_ingredients(ingredients_data)
        self.validate_tags(tags_data)

        recipe = Recipe.objects.create(**validated_data)

        recipe_ingredients = []

        for ingredient_data in ingredients_data:
            ingredient = get_object_or_404(
                Ingredient, pk=ingredient_data['id']
            )
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
            )

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        for tag in tags_data:
            recipe.tags.add(tag)

        return recipe

    def update(self, instance, validated_data):

        ingredients_data = self.initial_data.get('ingredients')
        tags_data = self.initial_data.get('tags')

        if ingredients_data is not None:
            self.validate_ingredients(ingredients_data)

        if tags_data is not None:
            self.validate_tags(tags_data)

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        if ingredients_data is not None:

            for current_ingredient in instance.ingredients.all():
                RecipeIngredient.objects.get(
                    recipe=instance, ingredient=current_ingredient
                ).delete()

            recipe_ingredients = []

            for ingredient_data in ingredients_data:
                ingredient = get_object_or_404(
                    Ingredient, pk=ingredient_data['id']
                )
                recipe_ingredients.append(
                    RecipeIngredient(
                        recipe=instance,
                        ingredient=ingredient,
                        amount=ingredient_data['amount']
                    )
                )

            RecipeIngredient.objects.bulk_create(recipe_ingredients)

        if tags_data is not None:
            instance.tags.set(tags_data)

        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'user', 'recipe',
        )
        model = Favorite
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe',),
                message='Recipe is already in favorites.',
            ),
        )


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'user', 'recipe',
        )
        model = ShoppingCart
        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe',),
                message='Recipe is already in shopping cart.',
            ),
        )

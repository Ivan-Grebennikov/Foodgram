import base64
from collections import defaultdict

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
            if not amount.isnumeric():
                errors['ingredients'].append(
                    'Missing \'amount\' must be a positive number.'
                )
                continue

        if len(errors) > 0:
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

        if len(errors) > 0:
            raise serializers.ValidationError(detail=errors)

    def create(self, validated_data):

        ingredients_data = self.initial_data.get('ingredients')
        tags_data = self.initial_data.get('tags')

        self.validate_ingredients(ingredients_data)
        self.validate_tags(tags_data)

        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(
                pk=ingredient_data['id']
            )
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient,
                amount=ingredient_data['amount']
            )

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

            for ingredient_data in ingredients_data:
                ingredient = Ingredient.objects.get(
                    pk=ingredient_data['id']
                )
                RecipeIngredient.objects.create(
                    recipe=instance, ingredient=ingredient,
                    amount=ingredient_data['amount']
                )

        if tags_data is not None:
            instance.tags.set(tags_data)

        instance.save()
        return instance


class ReadOnlyRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        read_only_fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        model = Recipe


class FollowingUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        fields = (
            'id', 'username', 'password', 'email',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')

        recipes = obj.recipes.all()

        if recipes_limit is not None and recipes_limit.isnumeric():
            recipes = recipes[:int(recipes_limit)]

        serializer = ReadOnlyRecipeSerializer(instance=recipes, many=True)
        return serializer.data

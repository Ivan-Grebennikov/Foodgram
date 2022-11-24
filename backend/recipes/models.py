import os

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=64, verbose_name='Name',
    )
    color = models.CharField(
        max_length=8,
        validators=(
            RegexValidator(
                regex=r'^#[a-fA-F0-9]{6}$',
                message='Color value is invalid',
            ),
        ),
        verbose_name='Color',
    )
    slug = models.SlugField(
        unique=True, verbose_name='Slug',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Name',
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Measurement unit',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Name',
    )
    text = models.TextField(
        verbose_name='Text',
    )
    author = models.ForeignKey(
        User, related_name='recipes',
        on_delete=models.CASCADE, verbose_name='Author',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Image',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message='The cooking_time can\'t be less than 1 minute',
            ),
        ],
        verbose_name='Cooking Time',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ingredients',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tags',
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message='The amount can\'t be less than 1',
            ),
        ],
        verbose_name='Amount',
    )

    class Meta:
        verbose_name = 'Ingredient in recipe'
        verbose_name_plural = 'Ingredients in recipe'

    def __str__(self):
        return f'{self.recipe} -> {self.ingredient}, {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, related_name='favorite',
        on_delete=models.CASCADE, verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Recipe',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorites',
            ),
        )
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, related_name='shopping_cart',
        on_delete=models.CASCADE, verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Recipe',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_cart',
            ),
        )
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Cart'

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


@receiver(post_delete, sender=Recipe)
def post_delete_recipe(sender, instance, *args, **kwargs):
    instance.image.delete(save=False)


@receiver(pre_save, sender=Recipe)
def pre_save_recipe(sender, instance, *args, **kwargs):
    old_instance = Recipe.objects.filter(id=instance.id)
    if old_instance.exists():
        old_image_path = old_instance.first().image.path
        if os.path.exists(old_image_path):
            os.remove(old_image_path)

import os

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=256)
    color = models.CharField(
        max_length=8,
        validators=(
            RegexValidator(
                regex=r'^#[a-fA-F0-9]{6}$',
                message='Color value is invalid',
            ),
        )
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=256)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message='The cooking_time can\'t be less than 1 minute'
            ),
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message='The amount can\'t be less than 1'
            ),
        ]
    )

    def __str__(self):
        return f'{self.recipe} -> {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, related_name='favorite', on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorites'
            ),
        )

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, related_name='shopping_cart', on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_cart'
            ),
        )

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

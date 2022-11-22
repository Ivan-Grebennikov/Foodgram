from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'text',
        'author',
        'image',
        'cooking_time',
        'get_ingredients',
        'get_tags',
        'get_in_favorites',
    )
    inlines = (RecipeIngredientInline,)
    search_fields = ('name', 'author__username',)
    list_filter = ('tags',)

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return '; '.join(
            f'{item.ingredient} - {item.amount}' for item in ingredients
        )

    def get_tags(self, obj):
        return '; '.join(f'{tag}' for tag in obj.tags.all())

    def get_in_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    get_ingredients.short_description = 'ingredients'
    get_tags.short_description = 'tags'
    get_in_favorites.short_description = 'in favorites'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)

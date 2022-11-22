from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Subscription

User = get_user_model()


class FoodgramUserAdmin(UserAdmin):
    search_fields = ('username', 'email',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'following',)
    search_fields = ('user__username',)


admin.site.register(User, FoodgramUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)

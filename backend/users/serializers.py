import djoser.serializers as dj_serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from utils.serializers import ReadOnlyRecipeSerializer

from .models import Subscription

User = get_user_model()


class UserCreateSerializer(dj_serializers.UserCreateSerializer):

    class Meta(dj_serializers.UserCreateSerializer.Meta):
        fields = (
            'id', 'username', 'password',
            'email', 'first_name', 'last_name',
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'username', 'password', 'email',
            'first_name', 'last_name', 'is_subscribed'
        )
        read_only_fields = (
            'id',
        )
        extra_kwargs = {'password': {'write_only': True}}
        model = User

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.following.filter(following=obj).exists()
        )


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'user', 'following',
        )
        model = Subscription
        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'following',),
                message='User has already been subscribed.',
            ),
        )

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                ['Can\'t subscribe to self.']
            )
        return data


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

        if recipes_limit is not None and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]

        serializer = ReadOnlyRecipeSerializer(instance=recipes, many=True)
        return serializer.data

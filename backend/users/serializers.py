import djoser.serializers as dj_serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers

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

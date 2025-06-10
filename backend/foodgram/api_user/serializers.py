from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields import fields as drf_fields
from rest_framework import serializers

from core.models import Subscription, User


class UserAccountSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user:
            return user.is_authenticated and Subscription.objects.filter(
                user__exact=user,
                subscribed_to__exact=obj
            ).exists()
        return False

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        ]


class UserRegisterSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}


class AvatarUploadSerializer(serializers.ModelSerializer):
    avatar = drf_fields.Base64ImageField()

    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar')
        if avatar is None:
            raise serializers.ValidationError(
                {'avatar': 'Это поле является обязательным.'}
            )
        instance.avatar = avatar
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('avatar',)

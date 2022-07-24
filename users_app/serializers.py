# users/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        password = validated_data.get('password', None)
        instance = self.Meta.model(**validated_data)

        # call set_password() to hash the user's password
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                # call set_password() to hash the user's password
                instance.set_password(value)
            else:
                setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'first_name',
            'last_name'
        ]

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ['password', 'user_permissions', 'groups']


class UserMessageSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(label='Email address', max_length=254)
    class Meta:
        model = get_user_model()
        fields = ['id','email','username']

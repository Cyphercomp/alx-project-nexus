from rest_framework import serializers
from .models import Product, UserProfile
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

class ProductSerializer(serializers.ModelSerializer):
    is_on_sale = serializers.BooleanField(read_only = True)
    current_price = serializers.FloatField(read_only = True)
    photo = serializers.ImageField(default = None)
    class Meta:
        model = Product
        fields = ('id','name','description','price','sale_start', 'sale_end', 'is_on_sale', 'current_price', 'photo')

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['is_on_sale'] = instance.is_on_sale()
    #     data['current_price'] = instance.current_price()
    #     return data 

class UserSerializer(serializers.ModelSerializer):
        """Serializer for the user object."""

        class Meta:
            model = get_user_model()
            fields = ['email', 'password', 'first_name','last_name']
            extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

        def create(self, validated_data):
            """Create and return a user with encrypted password."""
            return UserProfile.objects.create_user(**validated_data)

        def update(self, instance, validated_data):
            """Update and return user."""
            password = validated_data.pop('password', None)
            user = super().update(instance, validated_data)

            if password:
                user.set_password(password)
                user.save()

            return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
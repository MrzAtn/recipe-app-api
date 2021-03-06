from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    
    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name")
        extra_kwargs = {"password":{"write_only":True, "min_length":5}}
        
    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)
    
    def update(self, instance, validated_data): # instance du model utilisé par la class ==> User
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop("password", None) # get the new password and del it from the validated data
        user = super().update(instance, validated_data) # update default operation
        
        if password:
            user.set_password(password)
            user.save()
        
        return user
        
    

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentification object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={"input_type":"password"},
        trim_whitespace=False
    )
    
    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")
        
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        # In case of failure
        if not user:
            msg = _("Unable to authentiate with provided credentials")
            raise serializers.ValidationError(msg, code="authentification")
        attrs["user"] = user
        return attrs

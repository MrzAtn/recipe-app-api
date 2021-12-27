from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import *

class CreateAPIView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes =  api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,) # method d'authentification via les token d'auth
    permission_classes = (permissions.IsAuthenticated,) # il doit juste etre login pour réaliser les modifs
    
    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user # request contient user grace au authentication_classes

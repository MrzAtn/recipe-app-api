from rest_framework.decorators import action
from rest_framework.response import Response # return a custom response

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers

class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Return objects for the current user authenticated only"""
        return self.queryset.filter(user=self.request.user).order_by("-name") # user est dans request grace permission_classes
    
    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage Tags in database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
        

class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage Ingredients in database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipe in the database"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    
    def get_queryset(self):
        """Retrieve recipes for the current user authenticated only"""
        return self.queryset.filter(user=self.request.user).order_by("-id")
    
    def get_serializer_class(self):
        """Return the appropriate serializer class"""
        if self.action == "retrieve": # case of detail view
            return serializers.RecipeDetailSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer
        return self.serializer_class # case of list view
    
    def perform_create(self, serializer):
        """Create a new recipe object"""
        serializer.save(user=self.request.user)
        
    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        
        # test si les données pass au serilizer sont corrects
        if serializer.is_valid():
            serializer.save() # save modification from update
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.status.HTTP_400_BAD_REQUEST
        )
        
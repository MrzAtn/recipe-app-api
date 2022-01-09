from django.db.models.query import QuerySet
from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag object"""
    class Meta: 
        model = Tag
        fields = ("id", "name",)
        read_only_fields = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the Ingredient object"""
    class Meta:
        model = Ingredient
        fields = ("id", "name",)
        read_only_fields = ("id",)
        

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the Recipe object"""
    # on doit préciser les types des fields des cles externes car elles font référence a des tables externes
    ingredients = serializers.PrimaryKeyRelatedField( # permet de récupérer seulement les pk des ingredients, ici on ne cherche pas a avoir toutes les donnees des ingredients 
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    class Meta:
        model = Recipe
        fields = ("id", "title", "price", "time_min", "link",
                  "ingredients", "tags")
        read_only_fields = ("id",)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the detail Recipe object"""
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
        
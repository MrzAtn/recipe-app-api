from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import serializers, status
from rest_framework.test import APIClient
from recipe.serializers import RecipeSerializer
from recipe.tests.test_recipe_api import RECIPES_URL, create_sample_recipe, sample_ingredient, sample_tag

from core.models import *

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")

class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""
    def setUp(self):
        self.client = APIClient()
        
    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "antonin.marzelle@outlook.fr",
            "testPassword",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")
        
        res = self.client.get(TAGS_URL) # get les tags existant dans notre db via une view
        
        tags = Tag.objects.all().order_by("-name") # get les tags existant via Django "shell???"
        serializer = TagSerializer(tags, many=True) # many=True car on lui passe une liste d'instance de la class vers laquelle il pointe
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_tags_limited_to_user(self):
        """Test that the returned tags are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            email="antonin@noirlumiere.com",
            password="testPassword2",
        )
        
        Tag.objects.create(user=user2, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Comfort Food")
        
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(len(res.data), 1) # 1 seul élément à l'utilisateur "user"
         
    def test_create_tag_succesful(self):
        """Test creating a new tag"""
        payload = {"name": "test Tag creation"}
        self.client.post(TAGS_URL, payload)
        
        exists = Tag.objects.filter(
            name=payload["name"],
            user=self.user
        ).exists()
        
        self.assertTrue(exists)
    
    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)   

    def test_retrieve_tags_assigned_to_recipe(self):
        """Test filtering tags by those assigned to recipe"""
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        tag2 = Tag.objects.create(user=self.user, name="Lunch")
        recipe = Recipe.objects.create(
            title="Coriander eggs on toast",
            time_min=10, 
            price=5.00,
            user=self.user 
        )
        recipe.tags.add(tag1)
        
        res = self.client.get(TAGS_URL, {"assigned_only":1})
        
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        
    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned return unique items"""
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        Tag.objects.create(user=self.user, name="Lunch")
        recipe1 = Recipe.objects.create(
            title="Pancakes",
            time_min=5, 
            price=3.00,
            user=self.user 
        )
        recipe1.tags.add(tag)
        
        recipe2 = Recipe.objects.create(
            title="Porrige", 
            time_min=3,
            price=3.00,
            user=self.user
        )
        recipe2.tags.add(tag)
        
        res = self.client.get(TAGS_URL, {"assigned_only":1})
        
        self.assertEqual(len(res.data), 1)
        
        
        
        
        
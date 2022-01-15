import tempfile # permet de gérer des fichiers temporairement save
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import serializers, status
from rest_framework.test import APIClient

from core.models import *

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")

def image_upload_url(recipe_id):
    """RETURN URL for recipe image upload"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])

# api/recipe/recipes for the list page
# api/recipe/recipes/1 for a specified detail recipe view 

def detail_url(recipe_id):
    """Return the recipe detail url view"""
    return reverse("recipe:recipe-detail", args=[recipe_id])

def sample_tag(user, name="Main course"):
    """Create and return a sample tag object"""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name="Paprika"):
    """Create and return a sample ingredient object"""
    return Ingredient.objects.create(user=user, name=name)

def create_sample_recipe(user, **params):
    """Create and return a sample recipe object"""
    defaults = {
        "title": "Sample test",
        "time_min":10,
        "price": 8.00
    }
    defaults.update(params) # auto update the existing param if the matched keys were is in param or create it
    return Recipe.objects.create(
        user=user,
        **defaults
    )

class PublicTestApiRecipe(TestCase):
    """Test unauthenticated recipe API access"""
    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """Test that authentification is required"""
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    

class PrivateTestApiRecipe(TestCase):
    """Test authenticated recipe API access"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="antonin.marzelle@outlook.fr",
            password="testPassword"
        )
        
        self.client.force_authenticate(self.user)
    
    def test_retrieve_recipe_list(self):
        """Test retrieving a list of recipe"""
        create_sample_recipe(self.user)
        create_sample_recipe(self.user)
        
        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipe_limited_to_user(self):
        """Test retrieving recipes corresponding to the authenticated user"""
        user2 = get_user_model().objects.create_user(
            email="antonin@noirlumiere.com",
            password="testPassword2"
        )
        
        create_sample_recipe(self.user)
        create_sample_recipe(user2)
        
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)                      
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 1)
        
    def test_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user, name="tag1"))
        recipe.ingredients.add(sample_ingredient(user=self.user, name="ingredient1"))
        
        serializer = RecipeDetailSerializer(recipe)
        
        res = self.client.get(detail_url(recipe.id))
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipe_creation(self):
        """Test creating recipe"""
        payload = {
            "title": "Chocolate cake",
            "time_min": 30,
            "price": 6.50,
        }
        
        res = self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key)) # cant do recipe.key car objet de type QuerySet
            
    def test_recipe_create_with_tags(self):
        """Test creating recipe with tags"""
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Dessert")
        
        payload = {
            "title": "Avocado Cheesecake",
            "tags": [tag1.id, tag2.id],
            "time_min": 60, 
            "price": 15,
        }
        res = self.client.post(RECIPES_URL, payload) # we create the test recipe using tags
        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()
        
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        
    def test_recipe_create_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name="Avocado")
        ingredient2 = sample_ingredient(user=self.user, name="Cheese")
        
        payload = {
            "title": "Avocado Cheesecake",
            "ingredients": [ingredient1.id, ingredient2.id],
            "time_min": 60, 
            "price": 15,
        }
        res = self.client.post(RECIPES_URL, payload) # we create the test recipe using tags
        recipe = Recipe.objects.get(id=res.data["id"])
        ingredients = recipe.ingredients.all()
        
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
        
class RecipeImageUploadTest(TestCase):
    
    def setUp(self):
        self.client = APIClient() 
        self.user = get_user_model().objects.create_user(
            email="antonin.marzelle@outlook.fr",
            password="testPassword"
        )
        
        self.client.force_authenticate(self.user)
        self.recipe = create_sample_recipe(user=self.user)

    def tearDown(self): # Fonction comme setUp, appelé auto a la fin du test
        """Assure qu'aucune image reste enregistré apres notre test"""
        self.recipe.image.delete()
        
    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10,10))
            img.save(ntf, format="JPEG")
            ntf.seek(0) # reboot file cursor to the begining of the file
            res = self.client.post(url, {"image": ntf}, format="multipart")
        
        self.recipe.refresh_from_db()
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))
        
    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {"image": "notimage"}, format="multipart")
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_filter_recipes_by_tags(self):
        """Test returning recipes with specific tags"""
        recipe1 = create_sample_recipe(user=self.user, title="Tiramisu")
        recipe2 = create_sample_recipe(user=self.user, title="Tarte aux pommes")
        recipe3 = create_sample_recipe(user=self.user, title="Steak")

        tag1 = sample_tag(user=self.user, name="Dessert")
        tag2 = sample_tag(user=self.user, name="Vegan")
        
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        
        res = self.client.get(RECIPES_URL, {"tags": f"{tag1.id}, {tag2.id}"})
        
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
        
    def test_filter_recipes_by_ingredients(self):
        """Test returning recipeds with specific ingredients"""
        recipe1 = create_sample_recipe(user=self.user, title="Tiramisu")
        recipe2 = create_sample_recipe(user=self.user, title="Tarte aux pommes")
        recipe3 = create_sample_recipe(user=self.user, title="Steak")

        ingredient1 = sample_ingredient(user=self.user, name="cafe")
        ingredient2 = sample_ingredient(user=self.user, name="apple")
        
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        
        res = self.client.get(
            RECIPES_URL, 
            {"ingredients": f"{ingredient1.id}, {ingredient2.id}"}
        )
        
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
        
           
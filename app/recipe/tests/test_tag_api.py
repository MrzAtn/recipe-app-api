from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

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

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the user api public"""
    
    def setUp(self):
        self.client = APIClient()
      
        
    def test_create_valid_user_sucess(self):
        """Test creating with valid payload is successful"""
        payload = {
            "email":"antonin.marzelle@outlook.fr",
            "password":"admin123",
            "name":"Antonin",
        }
        res = self.client.post(CREATE_USER_URL, payload) # on envoie la requete de création via notre client
        # on test si la creation est bien réalisée par rapport à la réponse HTTP
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)
       
        
    def test_user_exits(self):
        """Test creating user that already exists fails"""
        payload = {
            "email":"antonin.marzelle@outlook.fr",
            "password":"admin123",
        }
        create_user(**payload) # création d'un user via notre fonction interne
        
        res = self.client.post(CREATE_USER_URL, payload) # Création d'un user via notre client
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        
    def test_password_to_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            "email":"antonin@noirlumiere.com",
            "password":"pw",
            "name":"Antonin",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Test si le user à quand meme été créé
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)
       
        
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            "email":"antonin@noirlumiere.com",
            "password":"test_password",
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        
    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email="antonin.marzelle@outlook.fr", password="testPoney")
        payload = {
            "email":"antonin.marzelle@outlook.fr",
            "password":"wrong",
        }
        res = self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        
    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {
            "email":"antonin@noirlumiere.com",
            "password":"psdfedfsw", 
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
       
        
    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        payload = {
            "email":"one",
            "password":"",
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_retrieve_user_unauthorized(self):
        """Test that authentification is required for user"""
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateUserAPITest(TestCase):
    """Test API request that required authentification"""
    
    def setUp(self):
        self.user = create_user(
            email="antonin.marzelle@outlook.fr", 
            password="admin123",
            name="Antonin")
        self.client = APIClient()
        # permet pour chaque test de forcer l'auth de notr utilisateur exemple pour ensuite le manipuler
        self.client.force_authenticate(user=self.user)
        
        
    def test_retrieve_profile_success(self):
        """Test that retrieving profile for logged in user"""
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.data, {
            "name":self.user.name,
            "email":self.user.email,
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        
    def test_post_me_not_allowed(self):
        """Test that POST method is not allowed in me url"""
        res = self.client.post(ME_URL, {})
        
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def test_update_user_profil(self):
        """Test updating the user profile for authentification user"""
        payload = {
            "name":"Nolwenn",
            "password":"admin234",
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db() # on refresh les donnés en local suite a notre patch
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        
        

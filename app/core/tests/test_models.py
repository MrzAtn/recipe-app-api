from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import *

def create_sample_user(email="antonin.marzelle@outlook.fr", password="testpassword"):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        # Variable pour la création de notre fake user
        email = "antonin.marzelle@outlook.fr"
        password = "lamalinE13!"
        # Récupération du model User puis création d'un élément
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "antonin.marzelle@OUTLOOK.fr"
        user = get_user_model().objects.create_user(email, "test123")
        self.assertEqual(user.email, email.lower())


    def test_empty_email_raiseError(self):
        """Test that if we try to create a user without email adress, a ValueError is raised."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None, password="test123")

    def test_create_superuser(self):
        """Test that we can create a superuser"""
        email = "antonin.marzelle@outlook.fr"
        password = "lamalinE13!"
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )
        self.assertTrue(user, user.is_superuser)
        self.assertTrue(user, user.is_staff)
    
    def test_tag_str(self):
        """Test the tag string representation"""
        tag = Tag.objects.create(
            user=create_sample_user(),
            name="Vegan",
        )
        self.assertEqual(str(tag), tag.name)
        
    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        incredient = Ingredient.objects.create(
            user=create_sample_user(),
            name="tomato",
        )
        self.assertEqual(str(incredient), incredient.name)
        
    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = Recipe.objects.create(
            user=create_sample_user(),
            title="pizza",
            time_min=5,
            price=8.00
        )
        self.assertEqual(str(recipe), recipe.title)
        
    @patch("uuid.uuid4")
    def test_recipe_filename_uuis(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = "uuid-test"
        mock_uuid.return_value = uuid
        file_path = recipe_image_file_path(None, "myimage.jpg")
        
        expected_path = f"uploads/recipe/{uuid}.jpg" 
        
        self.assertEqual(file_path, expected_path)
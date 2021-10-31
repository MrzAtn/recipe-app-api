from django.test import TestCase
from django.contrib.auth import get_user_model

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


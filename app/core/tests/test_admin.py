from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTests(TestCase):

    def setUp(self):
        """Function that setUp the Client that is needed to make our amdin test"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin.antonin.marzelle@outlook.fr",
            password="admin123"
        )
        # force_login permet de loger automatiquement un user à notre client
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = "antonin.marzelle@outlook.fr",
            password = "antonin123",
            name = "Test user full name"
        )
    
    def tests_user_listed(self):
        """Test that users ares listed on user page"""
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        # Validation of our test
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
        
    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse("admin:core_user_change", args=[self.user.id]) #/amdin/core/user/<id_user>
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200) # 200 is the status_code that is returned when the page is OK
        
    def test_create_user_page(self):
        """Test that the create user page work"""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)
from bs4 import BeautifulSoup
from django.test import TestCase, Client
from django.contrib.auth.models import User
from mall.models import Product

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password="somepassword")

    def test_landing(self):
        product_001 = Product.objects.create(
            name="abc",
            content='Hello World.',
            price=1234,
            author=self.user_trump
        )

        product_002 = Product.objects.create(
            name="defg",
            content='We are the World',
            price=1234,
            author=self.user_trump
        )

        product_003 = Product.objects.create(
            name="twer",
            content='Hello World.',
            price=1234,
            author=self.user_trump
        )

        product_004 = Product.objects.create(
            name="364352",
            content='Hello World.',
            price=1234,
            author=self.user_trump
        )
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn(product_001.name, body.text)
        self.assertIn(product_002.name, body.text)
        self.assertIn(product_003.name, body.text)
        self.assertIn(product_004.name, body.text)

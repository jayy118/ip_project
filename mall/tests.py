from bs4 import BeautifulSoup
from django.test import TestCase, Client
from .models import Product

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Mall', navbar.text)
        self.assertIn('About Us', navbar.text)

        logo_btn = navbar.find('a', text='DS Games')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        mall_btn = navbar.find('a', text='Mall')
        self.assertEqual(mall_btn.attrs['href'], '/mall/')

        about_us_btn = navbar.find('a', text='About Us')
        self.assertEqual(about_us_btn.attrs['href'], '/about_us/')

    def test_post_list(self):
        # 상품 목록 페이지를 가져온다
        response = self.client.get('/mall/')
        # 정상적으로 페이지가 로드
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀 'Mall'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Mall')
        # 네비게이션바가 있다
        self.navbar_test(soup)

        # 포스트(게시물)이 하나도 없는 경우
        self.assertEqual(Product.objects.count(), 0)
        # 적절한 안내 문구가 포함되어 있는지
        main_area = soup.find('div', id="main-area")
        self.assertIn('아직 상품이 없습니다.', main_area.text)

        # 포스트(게시물)이 2개 존재하는 경우
        product_001 = Product.objects.create(
            name = '첫 번째 상품입니다.',
            content = "Hello World!!! We are the world...",
            price = 1234,
            publisher = "abc"
        )
        product_002 = Product.objects.create(
            name='두 번째 상품입니다.',
            content="1등이 전부가 아니잖아요",
            price = 1234,
            publisher = "abc",
        )
        self.assertEqual(Product.objects.count(), 2)
        # 목록페이지를 새롭게 불러와서
        response = self.client.get('/mall/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 상품(게시물)의 타이틀이 2개 존재하는가
        main_area = soup.find('div', id="main-area")
        self.assertIn(product_001.name, main_area.text)
        self.assertIn(product_002.name, main_area.text)
        self.assertNotIn('아직 상품이 없습니다.', main_area.text)

    def test_post_detail(self):
        # 상품 하나
        product_001 = Product.objects.create(
            name='첫 번째 상품입니다.',
            content="Hello World!!! We are the world...",
            price=1234,
            publisher="abc"
        )
        # 이 상품의 url이 /blog/1
        self.assertEqual(product_001.get_absolute_url(), '/mall/1/')
        # url에 의해 정상적으로 상세페이지를 불러오는가
        response = self.client.get('/mall/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 상품목록과 같은 네비게이션바가 있는가
        self.navbar_test(soup)
        # 상품 name은 웹브라우저의 name에 있는가
        self.assertIn(product_001.name, soup.title.text)
        # 상품의 name은 포스트영역에도 있는가
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(product_001.name, post_area.text)
        # 포스트 작성자가 있는가
        # 아직 작성중
        # 포스트 내용이 있는가
        self.assertIn(product_001.content, post_area.text)
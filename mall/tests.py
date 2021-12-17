from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import TestCase, Client
from .models import Product, Category, Tag, Comment


# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_james = User.objects.create_user(username='james', password='somepassword')
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_james.is_staff = True
        self.user_james.save()

        self.category_rpg = Category.objects.create(name='rpg', slug='rpg')
        self.category_simulation = Category.objects.create(name='simulation', slug='simulation')

        self.tag_single = Tag.objects.create(name='싱글 플레이어', slug='싱글-플레이어')
        self.tag_coop = Tag.objects.create(name='협동', slug='협동')
        self.tag_multi = Tag.objects.create(name='멀티 플레이어', slug='멀티-플레이어')


        self.product_001 = Product.objects.create(
            name="abc",
            content='Hello World.',
            price=1234,
            category=self.category_simulation,
            author=self.user_james
        )
        self.product_001.tags.add(self.tag_single)

        self.product_002 = Product.objects.create(
            name="defg",
            content='We are the World',
            price=1234,
            category=self.category_rpg,
            author=self.user_trump
        )

        self.product_003 = Product.objects.create(
            name="twer",
            content='Hello World.',
            price=1234,
            author=self.user_james
        )
        self.product_003.tags.add(self.tag_coop)
        self.product_003.tags.add(self.tag_multi)

        self.comment_001 = Comment.objects.create(
            product = self.product_001,
            author = self.user_trump,
            content='첫 번째 댓글입니다. '
        )

    def test_create_post(self):
        # 로그인하지 않으면 status code != 200
        response = self.client.get('/mall/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff 아닌 trump 로그인
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/mall/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 james 로그인
        self.client.login(username='james', password='somepassword')

        response = self.client.get('/mall/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Add Product - Mall', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Add New Product', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/mall/create_post/',
            {
                'name': 'Post Form 만들기',
                'content': "Post Form 페이지를 만듭시다.",
                'price': 1234,
                'released_at': '2021-12-12',
                'publisher': 'aer',
                'tags_str': 'new tag; 한글 태그, 협동'
            }
        )
        last_post = Product.objects.last()
        self.assertEqual(last_post.name, "Post Form 만들기")
        self.assertEqual(last_post.author.username, 'james')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)


    def test_update_post(self):
        update_post_url = f'/mall/update_post/{self.product_003.pk}/'

        # 로그인하지 않은 경우
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.product_003.author, self.user_trump)
        self.client.login(
            username=self.user_trump.username,
            password='somepassword'
        )

        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # 작성자가 접근하는 경우
        self.client.login(
            username=self.product_003.author.username,
            password='somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Product - Mall', soup.title.text)
        main_area = soup.find('div', id="main-area")
        self.assertIn('Edit Product', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('협동; 멀티 플레이어', tag_str_input.attrs['value'])
        response = self.client.post(
            update_post_url,
            {
                'name': 'Post Form 수정하기',
                'content': "Post Form 페이지를 수저합시다.",
                'price': 1234,
                'released_at': '2021-12-12',
                'publisher': 'aer',
                'category': self.category_rpg.pk,
                'tags_str': '멀티 플레이어; 한글 태그, some tag'
            },
            follow = True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id="main-area")
        self.assertIn('Post Form 수정하기', main_area.text)
        self.assertIn("Post Form 페이지를 수저합시다.", main_area.text)
        self.assertIn(self.category_rpg.name, main_area.text)
        self.assertTrue(Tag.objects.get(name='멀티 플레이어'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertTrue(Tag.objects.get(name='some tag'))
        self.assertTrue(Tag.objects.get(name='협동'))



    def test_tag_page(self):
        response = self.client.get(self.tag_single.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_single.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_single.name, main_area.text)
        self.assertIn(self.product_001.name, main_area.text)
        self.assertNotIn(self.product_002.name, main_area.text)
        self.assertNotIn(self.product_003.name, main_area.text)

    def category_card_test(self, soup):
        category = soup.find('div', id='categories-card')
        self.assertIn('Categories', category.text)
        self.assertIn(f'{self.category_rpg.name} ({self.category_rpg.product_set.count()})', category.text)
        self.assertIn(f'{self.category_simulation.name} ({self.category_simulation.product_set.count()})', category.text)
        self.assertIn(f'미분류 (1)', category.text)

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

    def test_product_list(self):
        # 포스트가 있는 경우
        self.assertEqual(Product.objects.count(), 3)

        # 포스트 목록 페이지를 가져온다
        response = self.client.get('/mall/')
        # 정상적으로 페이지가 로드
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')  # soup에 페이지 내용을 담기
        self.assertEqual(soup.title.text, 'Mall')  # 타이틀에서 텍스트만 가져와 몰인지 확인

        self.navbar_test(soup)
        self.category_card_test(soup)

        # 포스트(게시물)의 타이틀이 3개 존재하는가
        main_area = soup.find('div', id="main-area")
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        product_001_card = main_area.find('div', id='product-1')
        self.assertIn(self.product_001.name, product_001_card.text)
        self.assertIn(self.product_001.category.name, product_001_card.text)
        self.assertIn(self.tag_single.name, product_001_card.text)
        self.assertNotIn(self.tag_coop.name, product_001_card.text)
        self.assertNotIn(self.tag_multi.name, product_001_card.text)

        product_002_card = main_area.find('div', id='product-2')
        self.assertIn(self.product_002.name, product_002_card.text)
        self.assertIn(self.product_002.category.name, product_002_card.text)
        self.assertNotIn(self.tag_single.name, product_002_card.text)
        self.assertNotIn(self.tag_coop.name, product_002_card.text)
        self.assertNotIn(self.tag_multi.name, product_002_card.text)

        product_003_card = main_area.find('div', id='product-3')
        self.assertIn(self.product_003.name, product_003_card.text)
        self.assertIn('미분류', product_003_card.text)
        self.assertNotIn(self.tag_single.name, product_003_card.text)
        self.assertIn(self.tag_coop.name, product_003_card.text)
        self.assertIn(self.tag_multi.name, product_003_card.text)

        #self.assertIn(self.user_james.username.upper(), main_area.text)
        #self.assertIn(self.user_trump.username.upper(), main_area.text)

        # 포스트(게시물)이 하나도 없는 경우
        Product.objects.all().delete()
        self.assertEqual(Product.objects.count(), 0)
        # 포스트 목록 페이지를 가져온다
        response = self.client.get('/mall/')
        # 정상적으로 페이지가 로드
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        # 적절한 안내 문구가 포함되어 있는지
        main_area = soup.find('div', id="main-area")
        self.assertIn('아직 상품이 없습니다.', main_area.text)


    def test_post_detail(self):
        # 상품 하나
        # 이 상품의 url이 /blog/1
        self.assertEqual(self.product_001.get_absolute_url(), '/mall/1/')
        # url에 의해 정상적으로 상세페이지를 불러오는가
        response = self.client.get('/mall/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 상품목록과 같은 네비게이션바가 있는가
        self.navbar_test(soup)
        self.category_card_test(soup)
        # 상품 name은 웹브라우저의 name에 있는가
        self.assertIn(self.product_001.name, soup.title.text)
        # 상품의 name은 포스트영역에도 있는가
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.product_001.name, post_area.text)
        self.assertIn(self.category_simulation.name, post_area.text)
        # 포스트 작성자가 있는가
        # 아직 작성중
        # 포스트 내용이 있는가
        self.assertIn(self.product_001.content, post_area.text)

        self.assertIn(self.tag_single.name, post_area.text)
        self.assertNotIn(self.tag_multi.name, post_area.text)
        self.assertNotIn(self.tag_coop.name, post_area.text)

        # comment area
        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_simulation.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_simulation.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_simulation.name, main_area.text)
        self.assertIn(self.product_001.name, main_area.text)
        self.assertNotIn(self.product_002.name, main_area.text)
        self.assertNotIn(self.product_003.name, main_area.text)

    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.product_001.comment_set.count(), 1)

        # 로그인 하지 않은 상태
        response = self.client.get(self.product_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertIn('Log in and leave a comment', comment_area.text)
        self.assertFalse(comment_area.find('form', id='comment-form'))

        # 로그인 한 상태
        self.client.login(username='trump', password='somepassword')
        response = self.client.get(self.product_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Log in and leave a comment', comment_area.text)

        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea', id='id_content'))
        response = self.client.post(
            self.product_001.get_absolute_url() + 'new_comment/',
            {
                'content': "두번째 댓글입니다.",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.product_001.comment_set.count(), 2)

        new_comment = Comment.objects.last()
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.product.name, soup.title.text)
        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn('trump', new_comment_div.text)
        self.assertIn("두번째 댓글입니다.", new_comment_div.text)

    def test_search(self):
        product_004 = Product.objects.create(
            name="게임에 대한 포스트입니다.",
            content='Hello World.',
            price=1234,
            author=self.user_james
        )

        response = self.client.get('/mall/search/게임/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('Search : 게임(1)', main_area.text)
        self.assertNotIn(self.product_001.name, main_area.text)
        self.assertNotIn(self.product_002.name, main_area.text)
        self.assertNotIn(self.product_003.name, main_area.text)
        self.assertIn(product_004.name, main_area.text)
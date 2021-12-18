from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils.datetime_safe import datetime
from markdownx.utils import markdown
from markdownx.models import MarkdownxField


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/mall/tag/{self.slug}/'


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, allow_unicode=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

    def get_absolute_url(self):
        return f'/mall/category/{self.slug}/'


class Publisher(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/mall/publisher/{self.slug}/'


class Product(models.Model):
    name = models.CharField(max_length=30)
    content = MarkdownxField()
    price = models.IntegerField()

    released_at = models.DateField(null=True)
    head_image = models.ImageField(upload_to='mall/images/%Y/%m/%d/',
                                   blank=True)  # -> 프로젝트 파일 > urls setting, static import urlpatterns 작성

    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    publisher = models.ForeignKey(Publisher, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.name} :: {self.publisher}'

    def get_absolute_url(self):
        return f'/mall/{self.pk}/'

    def get_content_markdown(self):
        return markdown(self.content)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/423/4a7c4bafe4a4afbe/svg/{self.author.email}'

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.product.get_absolute_url()}#comment-{self.pk}'

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/423/4a7c4bafe4a4afbe/svg/{self.author.email}'
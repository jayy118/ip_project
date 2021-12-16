from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils.datetime_safe import datetime

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

class Product(models.Model):
    name = models.CharField(max_length=30)
    content = models.TextField()
    price = models.IntegerField()
    publisher = models.CharField(max_length=50)

    released_at = models.DateField(null=True)
    head_image = models.ImageField(upload_to='mall/images/%Y/%m/%d/',
                                   blank=True)  # -> 프로젝트 파일 > urls setting, static import urlpatterns 작성

    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.name} :: {self.publisher}'

    def get_absolute_url(self):
        return f'/mall/{self.pk}/'

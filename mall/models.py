
from django.db import models

# Create your models here.
from django.utils.datetime_safe import datetime


class Product(models.Model):
    name = models.CharField(max_length=30)
    content = models.TextField()
    price = models.IntegerField()
    publisher = models.CharField(max_length=50)

    released_at = models.DateField(null=True)
    #head_image = models.ImageField(upload_to='mall/images/%Y/%m/%d/', blank=True) #-> 프로젝트 파일 > urls setting, static import urlpatterns 작성

    #author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    #category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    #tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.name} :: {self.publisher}'

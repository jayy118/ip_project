from django.shortcuts import render
from django.views.generic import ListView, DetailView

from mall.models import Product


class ProductList(ListView):
    model = Product
    ordering = '-pk'


class ProductDetail(DetailView):
    model = Product

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView

from mall.models import Product, Category, Tag


class ProductList(ListView):
    model = Product
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_product_count'] = Product.objects.filter(category=None).count()

        return context


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    product_list = tag.product_set.all()

    return render(
        request,
        'mall/product_list.html',
        {
            'product_list': product_list,
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_product_count': Product.objects.filter(category=None).count(),
        }
    )


class PostCreate(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'content', 'price', 'publisher', 'released_at', 'head_image', 'category']

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            return super(PostCreate, self).form_valid(form)
        else:
            return redirect('/mall/')


def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        product_list = Product.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        product_list = Product.objects.filter(category=category)

    return render(
        request,
        'mall/product_list.html',
        {
            'product_list': product_list,
            'categories': Category.objects.all(),
            'no_category_product_count': Product.objects.filter(category=None).count(),
            'category': category,
        }
    )


class ProductDetail(DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_product_count'] = Product.objects.filter(category=None).count()

        return context

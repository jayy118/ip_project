from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .forms import CommentForm
from .models import Product, Category, Tag, Publisher


class ProductList(ListView):
    model = Product
    ordering = '-pk'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_product_count'] = Product.objects.filter(category=None).count()
        context['publishers'] = Publisher.objects.all()
        context['no_publisher_product_count'] = Product.objects.filter(publisher=None).count()

        return context

class ProductSearch(ProductList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']
        product_list = Product.objects.filter(
            Q(name__contains=q) | Q(tags__name__contains=q)
        ).distinct()
        return product_list

    def get_context_data(self, **kwargs):
        context = super(ProductSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search : {q}({self.get_queryset().count()})'

        return context

def new_comment(request, pk):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.product = product
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())

        else:
            return redirect(product.get_absolute_url())
    else:
        raise PermissionDenied

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


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'content', 'price', 'publisher', 'released_at', 'head_image', 'category']

    template_name = 'mall/product_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    fields = ['name', 'content', 'price', 'publisher', 'released_at', 'head_image', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            return response
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


def publisher_page(request, slug):
    if slug == 'no_publisher':
        publisher = '미분류'
        product_list = Product.objects.filter(publisher=None)
    else:
        publisher = Publisher.objects.get(slug=slug)
        product_list = Product.objects.filter(publisher=publisher)

    return render(
        request,
        'mall/product_list.html',
        {
            'product_list': product_list,
            'publishers': Publisher.objects.all(),
            'no_publisher_product_count': Product.objects.filter(publisher=None).count(),
            'publisher': publisher,
        }
    )


class ProductDetail(DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_product_count'] = Product.objects.filter(category=None).count()
        context['publishers'] = Publisher.objects.all()
        context['no_publisher_product_count'] = Product.objects.filter(publisher=None).count()
        context['comment_form'] = CommentForm

        return context

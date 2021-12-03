from django.shortcuts import render

# Create your views here.
from mall.models import Product


def index(request):
    products = Product.objects.all().order_by('-pk')

    return render(
        request,
        'mall/index.html',
        {
            'products': products,
        }
    )
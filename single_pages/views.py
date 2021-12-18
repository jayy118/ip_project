from django.shortcuts import render
from mall.models import Product

# Create your views here.
def landing(request):
    recent_products = Product.objects.order_by('-pk')[:3]
    return render(
        request,
        'single_pages/landing.html',
        {
            'recent_products':recent_products
        }
    )

def about_us(request):
    return render(
        request,
        'single_pages/about_us.html'
    )
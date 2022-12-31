from django.shortcuts import render, get_object_or_404
from store.models import Product
from category.models import Category

# Create your views here.

def store(request, category_slug = None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories,is_avalible=True)
        products_count = products.count()

    else:
        products = Product.objects.all().filter(is_avalible=True)
        products_count = products.count()

    constext = {
        'products' : products,
        'products_count': products_count
    }

    return render(request, 'store/store.html', constext)

def product_detail(request,category_slug,product_slug):
    try:
        #para acessar o model da Category e pegar pelo slug do request e o slug do produto
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    
    except Exception as e:
        raise e
    
    context = {
        'product':product
    }

    return render(request, 'store/product_detail.html', context)
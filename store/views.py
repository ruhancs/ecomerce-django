from django.shortcuts import render, get_object_or_404
from store.models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator # para inserir paginaçao na pagina
from django.db.models import Q

def store(request, category_slug = None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories,is_avalible=True)
        paginator = Paginator(products, 3)# 6 produtos por pagina
        page = request.GET.get('page')# pegar a url da pagina
        paged_product = paginator.get_page(page)# armazena os 6 produtos
        products_count = products.count()

    else:
        products = Product.objects.all().filter(is_avalible=True).order_by('id')
        paginator = Paginator(products, 3)# 6 produtos por pagina
        page = request.GET.get('page')# pegar a url da pagina
        paged_product = paginator.get_page(page)# armazena os 6 produtos
        products_count = products.count()

    constext = {
        'products' : paged_product,
        'products_count': products_count
    }

    return render(request, 'store/store.html', constext)

def product_detail(request,category_slug,product_slug):
    try:
        #para acessar o model da Category e pegar pelo slug do request e o slug do produto
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # verificar se o produto ja esta no carrinho
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=product).exists
    
    except Exception as e:
        raise e
    
    context = {
        'product': product,
        'in_cart': in_cart
    }

    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains = keyword) | Q(product_name__icontains = keyword))
            product_count = products.count()
    context = {
        'products': products,
        'products_count': product_count
    }
    return render(request, 'store/store.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product,ReviewRating,ProductGallery
from .forms import ReviewForms
from category.models import Category
from carts.models import CartItem
from orders.models import OrderProduct
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator # para inserir paginaçao na pagina
from django.db.models import Q
from django.contrib import messages

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

    if request.user.is_authenticated:
        # verificar se o usuario ja comprou o produto
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user,product_id=product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
    
    # adicionar as avaliaçoes do produto a product_details.html
    reviews = ReviewRating.objects.filter(product_id = product.id, status=True)

    # pegar a galeria de imagens do produto
    product_gallery = ProductGallery.objects.filter(product_id = product.id)

    context = {
        'product': product,
        'in_cart': in_cart,
        'order_product':orderproduct,
        'reviews':reviews,
        'product_gallery':product_gallery
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


def submit_review(request,product_id):
    # pegar a url que esta
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            # caso o usuario ja tenha feito review do produto
            reviews = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form = ReviewForms(request.POST, instance=reviews)#para substituir o review anterior do usuario
            form.save()
            messages.success(request, 'Thank you! Your review has been updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForms(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')#pegar o ip do usuario
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted')
                return redirect(url)
from django.shortcuts import render, redirect,get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


from django.http import HttpResponse

# funçao privada com _ na frente do nome
def _cart_id(request):
    cart = request.session.session_key #pegar o id da sessao

    if not cart:
        cart = request.session.create()# se nao existe a sessao ela e criada
    
    return cart

def add_cart(request,product_id):
    current_user = request.user
    product =Product.objects.get(id=product_id)

    # se o usuario esta logado
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item # pegar o nome do input em product_detail.html
                value = request.POST[key]#pegar o valor do input em product_detail.html
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)               
                except:
                    pass        
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)       
            # verificar se a variaçao ja existe no carrinho
            ex_var_list = []
            cart_item_id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                cart_item_id.append(item.id)
            # se o product_variation ja existe dentro de ex_var_list
            # se o produto ja existe aumenta quantity se nao existe cria
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = cart_item_id[index]
                item = CartItem.objects.get(product=product, id= item_id)
                item.quantity += 1
                item.save() 
            else:#se o item com variaçoes diferentes for criado
                item = CartItem.objects.create(product=product,quantity=1,user=current_user)
            # adicionar a variaçao de tamanho e cor ao produto
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)       
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity = 1,
                user=current_user
            )
            # adicionar a variaçao de tamanho e cor ao produto
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    # se o usuario nao esta logado
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item # pegar o nome do input em product_detail.html
                value = request.POST[key]#pegar o valor do input em product_detail.html
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)               
                except:
                    pass      
        try:
    # cart_id é o cookie de nome sessionid
            cart = Cart.objects.get(cart_id = _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()   
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)       
            # verificar se a variaçao ja existe no carrinho
            ex_var_list = []
            cart_item_id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                cart_item_id.append(item.id)
            # se o product_variation ja existe dentro de ex_var_list
            # se o produto ja existe aumenta quantity se nao existe cria
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = cart_item_id[index]
                item = CartItem.objects.get(product=product, id= item_id)
                item.quantity += 1
                item.save() 
            else:#se o item com variaçoes diferentes for criado
                item = CartItem.objects.create(product=product,quantity=1,cart=cart)
            # adicionar a variaçao de tamanho e cor ao produto
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)       
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity = 1,
                cart = cart
            )
            # adicionar a variaçao de tamanho e cor ao produto
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
        return redirect('cart')


def remove_cart(request,product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_all_cart_item(request,product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id) 

    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id) 
    cart_item.delete()
    return redirect('cart')
    


def cart(request, total=0, cart_items=None,quantity=0):
    try:
        tax = 0
        final_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id =_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        final_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total':final_total
        
    }
    return render(request,'store/cart.html', context)

@login_required(login_url='login')
def checkout(request,total=0, cart_items=None,quantity=0):
    try:
        tax = 0
        final_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id =_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        final_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total':final_total
        
    }
    return render(request,'store/checkout.html', context)
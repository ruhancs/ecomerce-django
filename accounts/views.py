from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# para enviar o email de verificaçao
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id

import requests

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)#formaulario com todos os valores inseridos
        if form.is_valid():#se o formulario for valido pega os dados do formulario
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number = phone_number
            user.save()

            # user activation
            current_site = get_current_site(request)
            print(current_site)
            print('_______________')
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),#encodificar o id do usuario
                'token': default_token_generator.make_token(user),#criar token para o usuario
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            # send_email.send()
            
            # messages.success(request, 'Check your email for validate your account')
            return redirect('/accounts/login/?command=verification&email='+email)
            # return.redirect('register')
    else:
        form = RegistrationForm()
    context = {
        'form':form
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)

        if user:
            try:
                # verificar se ja exite um carrinho com compras
                # _cart_id e a funçao dentro de views de carts para pegar o id de cart da pagina
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)#todos os itens dentro do cart

                    product_variation = []
                    for item in cart_item:
                        variation = item.variation.all()#todas as variaçoes do produto
                        product_variation.append(list(variation))
                    
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter( user=user)       
                        # verificar se a variaçao ja existe no carrinho
                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variation.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)
                        
                    # verificar se as variaçoes do product_variation existe em ex_var_list
                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)#posiçao que foi encontrado o item
                                item_id = id[index]
                                item =  CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user
                                item.save()
                            else:#se a variaçao nao existe em ex_var_list
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()
            except:
                pass
            auth.login(request,user)
            messages.success(request,'You are now logged in')
            url = request.META.get('HTTP_REFERER')#para pegar a url anterior
            try:
                query = requests.utils.urlparse(url).query#para pegar a url cart/checkout
                print('_______________')
                print(query)
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('dashboard')
        else:
            messages.error(request,'Invalid email or password')
            return redirect('login')
        
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are Logged out')
    return redirect('login')

# validar o usuario que fez registro
def activate(request, uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()#para pegar a pk do user
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, ' Your account is valid now')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

@login_required
def dashboard(request):
    return render(request,'accounts/dashboard.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        # verificar se a conta existe
        
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # send email to change the password
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),#encodificar o id do usuario
                'token': default_token_generator.make_token(user),#criar token para o usuario
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            # send_email.send()

            messages.success(request,'Password reset email has been sent to you email address')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist')
            return redirect('forgotPassword')

    return render(request,'accounts/forgot_password.html')

def reset_password_validate(request, uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()#para pegar a pk do user
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        # inserir o uid na sessao
        request.session['uid'] = uid
        messages.success(request,'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request,'This link has be expired')
        return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)#set_password funçao interna do django para alterar a senha e encriptografar a nova senha
            user.save()
            messages.success(request,'Password save succesfuly')
            return redirect('login')
        else:
            messages.error(request,'Passwords does not match')
            return redirect('reset_password')
    else:
        return render(request,'accounts/reset_password.html')
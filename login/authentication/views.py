from django.core.mail.message import EmailMessage
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from login import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from token import generate_token

def home(request):
    return render(request, "authentication/index.html")

def signup(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        
        if User.objects.filter(username=username):
            messages.error(request, "Esse nome de usuário já existe!")
            return redirect('home')
        
        if User.objects.filter(email=email):
            messages.error(request, "Esse email já está sendo utilizado")
            return redirect('home')

        if len(username) > 10:
            messages.error(request, "Nome do usuário precisa ser menor que 10 caracteres!")

        if pass1 != pass2:
            messages.error(request, "A senhas digitadas não são iguais!")

        if not username.isalnum():
            messages.error(request, "O nome de usuário pode apenas conter caracteres Alfanuméricos!")
            return redirect('home')


        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Sua conta foi criada com sucesso. Nós te enviamos um email de confirmação de conta!")

        #Bem vindo no Email

        subject = "Bem vindo a um sistema simples de login em Django"
        message = "Hello" + myuser.first_name + "!! /n/n" + "Bem vindo a um sistema simples de login em Django, por gentileza, confirme seu endereço de email \n" + "Obrigado, atenciosamente, \n Junior."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        #Confirmacao de email

        current_site = get_current_site(request)
        email_subject = "Confirme seu email @ Login System - Django"
        message2 = render_to_string("email_confirmation.html", {dict}), {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),       
            'token': generate_token.make_token(myuser)
        }
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email], 
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')

    return render(request, "authentication/signup.html")

def signin(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name  
            return render(request, "authentication/index.html", {'fname':fname})  

        else:
            messages.error(request, "Credenciais incorretas!")
            return redirect('home')


    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request,"Você se desconectou com sucesso!")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request,'activate_failed.html')

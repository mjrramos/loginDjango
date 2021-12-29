from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from login import settings
from django.core.mail import send_mail


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

        myuser.save()

        messages.success(request, "Sua conta foi criada com sucesso. Nós te enviamos um email de confirmação de conta!")

        subject = "Bem vindo a um sistema simples de login em Django"
        message = "Hello" + myuser.first_name + "!! /n/n" + "Bem vindo a um sistema simples de login em Django, por gentileza, confirme seu endereço de email \n" + "Obrigado, atenciosamente, \n Junior."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

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


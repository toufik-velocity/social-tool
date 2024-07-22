from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import get_user_model

User = get_user_model()

def signup(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already taken")
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already registered")
                return redirect('signup')

            strength_tests = """
                . Password should be more than 8 characters long,
                Password should contain lowercase letters,
                Password should contain uppercase letters,
                Password should contain numbers,
                Password should contain symbols [ '!', '£', '$', '%', '&', '<', '*', '@', '#', '^']
            """
            score = 0
            length = len(password1) >= 8
            lower = any(char.islower() for char in password1)
            upper = any(char.isupper() for char in password1)
            number = any(char.isdigit() for char in password1)
            symbol = any(char in ['!', '£', '$', '%', '&', '<', '*', '@', '#', '^'] for char in password1)

            score = sum([length, lower, upper, number, symbol])
            context['score'] = score

            if score < 3:
                messages.info(request, f"Weak password. Your password strength score is: {score}/5" + strength_tests)
                return redirect('signup')

            elif score < 5:
                messages.info(request, "This password could be improved." + strength_tests)
                return redirect('signup')

            if score == 5:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                return redirect('signin')

        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')

    return render(request, 'create.html', context)

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(email=username).exists():
            the_user = User.objects.get(email=username)
            username = the_user.username

        user = auth.authenticate(request, username=username, password=password)

        if user:
            auth.login(request, user)
            return redirect('main')

        else:
            messages.info(request, "Invalid Credentials")
            return redirect('signin')

    return render(request, 'login.html')

def signout(request):
    auth.logout(request)
    return redirect('signin')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import auth

def signup(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email'] 
        password1 = request.POST['password1'] 
        password2 = request.POST['password1'] 

        # First check if the password are matching
        if password1 == password2:
            # Check if the username provided exists
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already taken")
                return redirect('signup')

            else:
                # Checking for password strength before saving the data
                strength_tests = """
                . Password should be more than 8 characters long,
                Password should contain lowercase letters,
                Password should contain uppercase letters,
                Password should contain numbers,
                Password should contain symbols[ '!', '£', '$', '%', '&', '<', '*', '@', '#', '^']
                """
                score = 0
                length = 0
                lower = False
                upper = False
                number = False
                symbol = False
                numbers = [ '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
                symbols = [ '!', '£', '$', '%', '&', '<', '*', '@', '#', '^']

                if len(password1) >= 8:
                    length = True

                for item in password1:
                    if item.islower():
                        lower = True

                    elif item.isupper():
                        upper = True

                    elif item in numbers:
                        number = True

                    elif item in symbols:
                        symbol = True

                if length:
                    score = score + 1

                if lower:
                    score = score + 1

                if upper:
                    score = score + 1


                if number:
                    score = score + 1

                if symbol:
                    score = score + 1

                context['score'] = score


                if score == 1 or score == 2:
                    messages.info(request, f"""Weak password, 
                        You password strength score is: {score}/5""" + strength_tests)
                    return redirect('signup')

                elif score == 3 or score == 4:
                    messages.info(request, "This password could be improved." + strength_tests)
                    return redirect('signup')

                elif score == 5:
                    # Saving the data
                    user = User.objects.create_user(username=username, email=email, password=password1)

                    user.save
                    return redirect('signin')
        else:
            messages.info(request, 'Password Not Matching')
            
            return redirect('signup')             

    return render(request, 'create.html', context)

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Checking if the email provided exists
        if User.objects.filter(email=username).exists():
            the_user = User.objects.get(email=username)
            username = the_user.username

        user = auth.authenticate(username=username, password=password)

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

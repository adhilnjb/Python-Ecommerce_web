from django.contrib.auth import authenticate, login as auth_login,get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages


def Registration(request):
    if request.method == 'POST':
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('confirm_password')

        if password != cpassword:
            messages.error(request,"Password and comfirm password are mismatch")
            return redirect ('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request,'Email ID already existed.')
            return redirect ('register')
        
        try:
            user = User.objects.create_user(
                first_name = fname,
                last_name = lname,
                email = email,
                username=username,
                password=password
            )
            messages.success(request,'Registration successfull')
            user.generate_verification_code()
            return redirect('otp')
        except Exception as e:
            print('error')
            messages.error(request,f"Error creating account: {e}")
            return redirect('register')

    return render(request,"Account/Registration.html")


def otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            if user.otp == otp:
                user.is_verified = True
                user.save()
                messages.success(request,'Your account is verified.' )
                return redirect('login')
            else:
                messages.error(request,"Invaild input.")
        except ObjectDoesNotExist:
            messages.error(request,'Email not found')

    return render(request,"Account/otp.html")
 
User = get_user_model()  # Use the custom User model

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')  # Fix case sensitivity for 'password'

        user = authenticate(request, email=email, password=password)  # Adjust if using email
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                messages.success(request, 'Your account is verified.')
                return redirect('home')  # Replace with your route for logged-in users
            else:
                messages.error(request, 'Account is inactive.')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, "Account/login.html")
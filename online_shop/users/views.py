from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.urls import reverse
from .forms import UserLogin, UserAuthentication, UserProfile, EmailVerification, EmailForPasswordReset, PasswordReset
from market.models import Cart
from orders.models import Order, OrderItem
from django.db.models import Prefetch
from django.core.cache import cache
from .tasks import send_account_confirmation_email
from .models import User
from celery.result import AsyncResult
from online_shop.celery import project
from django.views.decorators.http import require_POST
from .utils import generate_password_reset_token, verify_token
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.db import transaction


def register(request):
    if request.user.is_authenticated:
        return redirect(reverse("users:profile"))
    
    if request.method == 'POST':
        form = UserAuthentication(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            task_result = send_account_confirmation_email.delay(receiver=str(cleaned_data['email']))
            
            # incase old auth data got left behind
            request.session.pop('temp_auth_data', 0)
            # store some data in session to transfer between views, clean up later
            request.session['temp_auth_data'] = {
                "username": cleaned_data['username'],
                "password": cleaned_data['password1'],
                "email": cleaned_data['email'],
                "task_id": task_result.id
            }

            messages.success(request, f"Email verification code was sent to your email")
            return redirect(reverse("users:confirm_email"))
    else:
        form = UserAuthentication()
    request.session.pop('temp_auth_data', 0)
    context = {
        'form': form
    }
    return render(request, 'users/register.html', context)

def login(request):
    if request.user.is_authenticated:
        return redirect(reverse("users:profile"))
    
    if request.method == 'POST':
        form = UserLogin(data=request.POST)
        print(form.errors)
        if form.is_valid():
            username, password = request.POST['username'], request.POST['password']
            user = auth.authenticate(request=request, username=username, password=password)
            if user:
                session_key = request.session.session_key
                if session_key:
                    Cart.objects.filter(session_key=session_key).update(user=user)

                auth.login(request, user=user)
                messages.success(request, 'Successfully logged into an account')

                return redirect(reverse("main:catalog_default"))
    else:
        form = UserLogin()

    context = {'form': form}
    return render(request, 'users/login.html', context=context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfile(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')

            return redirect(reverse('users:profile'))

    else:
        form = UserProfile(files=request.FILES, instance=request.user)
    data = Order.objects.filter(user=request.user).prefetch_related(Prefetch('orderitem_set',
                                                                               queryset=OrderItem.objects.prefetch_related('product'),
                                                                               ))
    orders = cache.get_or_set(f'users:orders:{request.session.session_key}', list(data), 60*15)
    context = {'form': form,
               'orders': orders}
    return render(request, 'users/profile.html', context=context)


@login_required
def logout(request):
    messages.success(request, "You logged out of your account")
    auth.logout(request)

    return redirect(reverse("main:catalog_default"))


def confirm_email(request):
    if request.method == 'POST':
        form = EmailVerification(request.POST)
        if form.is_valid():
            temp_auth_data = request.session.get('temp_auth_data')

            task_id = temp_auth_data['task_id']
            task_async = AsyncResult(task_id)
            task_async.backend = project.backend

            task_async_result = (task_async.get(5)).get("key")
            if task_async_result:
                code = cache.get(task_async_result)
                if int(code) == form.cleaned_data['verification_code']:
                    with transaction.atomic:
                        session_key = request.session.session_key
                        new_user = User.objects.create_user(
                            username=temp_auth_data.get('username'),
                            password=temp_auth_data.get('password'),
                            email=temp_auth_data.get('email')
                        )
                        if session_key:
                            Cart.objects.filter(session_key=session_key).update(user=new_user)

                        auth.login(request, new_user)
                        # cleanups
                        request.session.pop('temp_auth_data')
                        cache.delete(task_async_result)
                        task_async.forget()
                        return redirect(reverse("main:catalog_default"))

        request.session.pop('temp_auth_data')
        context = {"form": form}
        return render(request, "users/confirm_email.html", context=context)
    
    else:
        form = EmailVerification()
        context = {
            "form": form
        }
        return render(request, "users/confirm_email.html", context=context)
    

#@require_POST
def rescend_code(request):
    temp_auth_data = request.session.get('temp_auth_data')
    if temp_auth_data:
        # Cleanup if old task related data still persists
        task_async = AsyncResult(temp_auth_data['task_id'])
        task_async.backend = project.backend
        task_data = (task_async.get(5)).get('key')
        if task_data:
            task_async.forget()
            cache.delete(task_data)

        email = request.session.get('temp_auth_data').get('email')
        task = send_account_confirmation_email.delay(receiver=email)
        request.session.get('temp_auth_data')['task_id'] = task.id

        messages.success(request, "A different verification code was sent to your email")
        return redirect(reverse("users:confirm_email"))
    

def reset_password(request):
    if request.method == 'POST':
        # Keep track of ip's to limit usage of this operation
        ip = request.META['REMOTE_ADDR']
        key = f"ratelimit:password_reset:{ip}"
        request_amount_from_ip = cache.get(key, 0)

        if request_amount_from_ip > 3:
            messages.success(request, "Slow down!")
            return redirect(reverse('users:reset_password'))
        cache.set(key, request_amount_from_ip+1, 300)
        # To not leak anything, always display successful message
        messages.success(request, "A password reset link has been successfully sent to your email")

        form = EmailForPasswordReset(request.POST)
        if form.is_valid():
            try:
                user_id = User.objects.get(email=form.cleaned_data['email'])
            except User.DoesNotExist:
                return redirect(reverse('users:reset_password'))
            
            token = generate_password_reset_token(user_id.id)
            change_url = reverse('users:change_password', kwargs={'token': token})
            url = request.build_absolute_uri(change_url)

            send_mail(
                'Password reset link',
                f'Your password reset link is {url}',
                settings.DEFAULT_FROM_EMAIL,
                [form.cleaned_data['email']]
            )

            return redirect(reverse('users:reset_password'))
    else:
        form = EmailForPasswordReset()
        context = {
            'form': form
        }
    return render(request, 'users/reset_password.html', context=context)




def change_password_after_reset(request, token):
    token_verified = verify_token(token)
    if not token_verified:
        return HttpResponse(status=400)

    if request.method == 'POST':
        form = PasswordReset(request.POST)
        if form.is_valid():
            user = User.objects.get(id=token_verified.get('user_id'))
            user.set_password(form.cleaned_data['password1'])
            user.save()

            auth.login(request, user)
            messages.success(request, 'Password changed successfully')
            return redirect(reverse('users:profile'))
    else:
        form = PasswordReset()
        context = {
            'form': form,
            'token': token
        }
    return render(request, 'users/change_password.html', context=context)
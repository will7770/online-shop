from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.urls import reverse
from .forms import UserLogin, UserAuthentication, UserProfile
from market.models import Cart
from orders.models import Order, OrderItem
from django.db.models import Prefetch
from django.core.cache import cache


def register(request):
    if request.method == 'POST':
        form = UserAuthentication(request.POST)
        if form.is_valid():
            form.save()

            session_key = request.session.session_key
            user = form.instance
            auth.login(request, user)

            if session_key:
                Cart.objects.filter(session_key=session_key).update(user=user)
            messages.success(request, f"{user.username}, Successfully made an account")
            return redirect(reverse("main:catalog_default"))
    else:
        form = UserAuthentication()
    
    context = {
        'form': form
    }
    return render(request, 'users/register.html', context)

def login(request):
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
    orders = cache.get_or_set(f'users:orders:{request.session.session_key}', list(data), 15)
    context = {'form': form,
               'orders': orders}
    return render(request, 'users/profile.html', context=context)


@login_required
def logout(request):
    messages.success(request, "You logged out of your account")
    auth.logout(request)

    return redirect(reverse("main:catalog_default"))
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ValidationError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from .forms import ReviewForm
from django.contrib import messages
from django.db import transaction
from .models import Review
from market.models import Item
from django.db.models import F
from django.core.cache import cache
from django.http import HttpResponseNotFound



class PublshReview(FormView, LoginRequiredMixin):
    template_name = 'product.html'
    form_class = ReviewForm
    
    def get_success_url(self):
        slug = self.kwargs.get('slug')
        return reverse_lazy('main:product', {'slug': slug})

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            messages.success(self.request, 'Register to post reviews!')
            return redirect(reverse('users:register'))
        
        user = self.request.user
        slug = self.kwargs.get('slug')
        item = Item.objects.filter(slug=slug).first()
        
        if not Item.objects.filter(slug=slug).exists():
            return HttpResponseNotFound()

        if Review.objects.filter(author=user, item=item).exists():
            messages.success(self.request, 'You have previously posted a review on this product before')
            return redirect(reverse('main:product', kwargs={'slug':slug}))
        
        Review.objects.create(
            author=user,
            item=item,
            rating=form.cleaned_data.get('rating'),
            text=form.cleaned_data.get('text'),
            title=form.cleaned_data.get('title')
        )
    
        messages.success(self.request, 'Review posted successfully')
        return redirect(reverse('main:product', kwargs={'slug':slug}))
    
    def form_invalid(self, form):
        print(form.errors)
        messages.success(self.request, f'Make sure you entered everything right!')
        return redirect(reverse('main:product', kwargs={'slug':self.kwargs.get('slug')}))
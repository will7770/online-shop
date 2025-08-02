from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create_review/<slug:slug>', views.PublshReview.as_view(), name='create_review')
]

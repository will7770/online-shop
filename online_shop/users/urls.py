from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.logout, name="logout"),
    path('verify_email/', views.confirm_email, name="confirm_email"),
    path('resend_email/', views.rescend_code, name="resend_email"),
    path('reset_password/', views.reset_password, name="reset_password"),
    path('change_password_after_reset/<str:token>/', views.change_password_after_reset, name='change_password')
]

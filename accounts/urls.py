
from django.urls import path
from .views import SignUpView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('accounts/', SignUpView.as_view(), name = 'signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
    


    
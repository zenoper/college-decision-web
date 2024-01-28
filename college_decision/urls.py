from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pricing/', views.pricing, name='pricing'),
    path('send_letter/', views.letter, name='send_letter'),
    path('send_letter/submit', views.submitted_info, name="submitted_info"),
    path('peasant/', views.peasant, name='peasant'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]

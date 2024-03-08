from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('pricing/', views.pricing, name='pricing'),
    path('send_letter/', views.letter, name='send_letter'),
    path('send_letter/submit', views.submitted_info, name="submitted_info"),
    path('invalid_email/', views.invalid_email, name='invalid_email')
]

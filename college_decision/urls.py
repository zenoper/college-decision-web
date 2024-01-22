from django.urls import path
from .views import home, pricing, letter, submitted_info

urlpatterns = [
    path('', home, name='home'),
    path('pricing/', pricing, name='pricing'),
    path('send_letter/', letter, name='send_letter'),
    path('send_letter/submit', submitted_info, name="submitted_info")
]

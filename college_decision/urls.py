from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('pricing/', views.pricing, name='pricing'),
    path('send_letter/', views.letter, name='send_letter'),
    path('send_letter/submit', views.submitted_info, name="submitted_info"),
    path('invalid_email/', views.invalid_email, name='invalid_email'),
    path('checkout/', views.checkout, name='checkout'),
    path('create-checkout-session', views.create_checkout_session, name='create_checkout_session'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('cancel/', views.cancel, name='cancel'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('pay_bruh/', views.pay_bruh, name='pay_bruh'),
    path('error_page/', views.error_page, name='error_page'),
    path('prices/', views.prices, name="prices")
]
 
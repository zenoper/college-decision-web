from django.shortcuts import render
from .send_email import send_email
import re

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Payment

stripe.api_key = 'sk_test_51OcOkAH7wZCCmn5aCIr3JMdMXXThlfWdA6rtWqp5KhrrE5771hVSnP11B0eMpBYh89ghWd6JaIMy81BONTCB69K200j9W7Y3zT'

def home(request):
    return render(request, 'index.html')


def pricing(request):
    return render(request, 'pricing.html')


def letter(request):
    return render(request, 'send_letter.html')


def submitted_info(request):
    if request.method == 'POST':
        EMAIL_REGEX = r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+'

        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        university = request.POST.get('university')
        decision = request.POST.get('decision')
        university_cap = university.capitalize() + ' ' + "Office of Undergraduate Admissions"
        email_to = request.POST.get('email_to')

        payment = Payment.objects.filter(user_identifier=email).first()

        if re.match(EMAIL_REGEX, email_to):

            if payment and payment.emails_purchased > payment.emails_sent:
                # Allow sending email
                payment.emails_sent += 1
                payment.save()

                try:
                    send_email(sender_name=university_cap, receiver_email=email_to, first_name=full_name, decision=decision, university=university)
                except Exception as e:
                    print(f"error : {e}")

                return render(request, 'confirmation.html')
            else:
                return render(request, 'pay_bro.html')
        else:
            return render(request, 'invalid_email.html')

    return render(request, 'send_letter.html')


def invalid_email(request):
    return render(request, 'invalid_email.html')


def checkout(request):
    # Here you can pass the order details to the template for review
    order_details = {
        # Example data structure - replace this with actual order data
        'items': [
            {'name': 'Product 1', 'price': 10, 'quantity': 1},
            {'name': 'Product 2', 'price': 5, 'quantity': 1},
        ],
        'total': 2000,  # Example total
    }

    return render(request, 'checkout.html', {'order_details': order_details})


@require_POST
def create_checkout_session(request):
    YOUR_DOMAIN = "https://www.college-decision.com/"  # Replace with your domain

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1OceKfH7wZCCmn5aMh7Izt0I',
                    'quantity': 3,
                },
                {
                    'price': 'price_1OcdziH7wZCCmn5axANeg9JL',
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/send_letter/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
    except Exception as e:
        return JsonResponse({'error': str(e)})

    return redirect(checkout_session.url)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = 'whsec_ee8fcf7616f27578757c8e44f4e02bf39e1ea96e0b87a3a7d92838776a326e45'

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_email = session['customer_email']  # Extract the email from the session
        emails_purchased = int(session['metadata']['emails_purchased'])  # Example metadata

        # Update or create the payment record for the user
        payment, created = Payment.objects.get_or_create(user_identifier=user_email)
        payment.emails_purchased += emails_purchased
        payment.save()

    return JsonResponse({'status': 'success'}, status=200)


def success(request):
    return render(request, 'success.html')


def cancel(request):
    return render(request, 'cancel.html')


def pay_bruh(request):
    return render(request, 'pay_bro.html')



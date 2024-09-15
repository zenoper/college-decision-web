from django.shortcuts import render
from .send_email import send_email
import re
from django.http import HttpResponse

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Payment

import logging
logger = logging.getLogger(__name__)

from environs import Env
env = Env()
env.read_env()

stripe.api_key = env.str("STRIPE_KEY")


def home(request):
    return render(request, 'index.html')


def pricing(request):
    return render(request, 'pricing.html')


def letter(request):
    credits = request.COOKIES.get('credits')

    if credits:
        try:
            credits = int(credits)  # Convert the string to an integer

            if credits > 0:
                # User has credits left, decrease by 1 and continue
                response = render(request, 'send_letter.html')
            else:
                # No credits left, redirect to the payment page
                return redirect('/checkout/')
        except ValueError:
            # If there's an issue with the cookie value, reset and redirect to payment
            return redirect('/checkout/')
    else:
        # If no credits cookie is found, redirect to the payment page
        return redirect('/checkout/')


def submitted_info(request):
    if request.method == 'POST':
        credits = request.COOKIES.get('credits')  # Get the credits from the cookie
        EMAIL_REGEX = r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+'

        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        university = request.POST.get('university')
        decision = request.POST.get('decision')
        university_cap = university.capitalize() + ' ' + "Office of Undergraduate Admissions"
        email_to = request.POST.get('alternate_email')
        payment = Payment.objects.filter(user_email=email).first()

        if re.match(EMAIL_REGEX, email_to):
            # Check if the user has enough credits
            if credits and payment and payment.emails_purchased > payment.emails_sent:
                try:
                    # Send the email
                    send_email(sender_name=university_cap, receiver_email=email_to, first_name=full_name, decision=decision, university=university)

                    # After the email is successfully sent, update emails_sent in the database
                    payment.emails_sent += 1
                    payment.save()

                    # Decrease the credits in the cookie
                    credits = int(credits)
                    if credits > 0:
                        response = render(request, 'confirmation.html')
                        response.set_cookie('credits', credits - 1, max_age=60 * 60 * 24 * 30)  # Decrease credits and update cookie
                        return response

                except Exception as e:
                    print(f"error : {e}")
                    return render(request, 'error.html')

            else:
                # Not enough credits, redirect to the payment page
                return render(request, 'pay_bro.html')
        else:
            # Invalid email format
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
    YOUR_DOMAIN = "https://www.college-decision.com"  # Replace with your domain

    try:

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1OceKfH7wZCCmn5aMh7Izt0I',
                    'quantity': 3,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/send_letter/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
            metadata={
                'emails_purchased': 3,  # Set the number of emails purchased here
            }
        )
    except Exception as e:
        return JsonResponse({'error': str(e)})

    return redirect(checkout_session.url)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = env.str("ENDPOINT_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_details', {}).get('email')
        emails_purchased = int(session['metadata']['emails_purchased'])  # Example metadat
        # Update or create the payment record for the user
        try:
            payment, created = Payment.objects.get_or_create(user_email=customer_email)
            payment.emails_purchased += emails_purchased
            payment.save()
            logger.info(f"Payment updated for {customer_email}: {emails_purchased} emails purchased")
            # Set a cookie in the response that indicates the user has paid
            response = HttpResponse("Payment successful")
            response.set_cookie('credits', emails_purchased, max_age=60 * 60 * 24 * 30)  # 30 days validity
        except Exception as e:
            logger.error(f"Error updating payment: {str(e)}")

    return JsonResponse({'status': 'success'}, status=200)


def success(request):
    return render(request, 'success.html')


def cancel(request):
    return render(request, 'cancel.html')


def pay_bruh(request):
    return render(request, 'pay_bro.html')



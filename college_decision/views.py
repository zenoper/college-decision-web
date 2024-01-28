from django.shortcuts import render
from .send_email import send_email

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
import json

stripe.api_key = "sk_test_51OcOkAH7wZCCmn5aCIr3JMdMXXThlfWdA6rtWqp5KhrrE5771hVSnP11B0eMpBYh89ghWd6JaIMy81BONTCB69K200j9W7Y3zT"

endpoint_secret = 'whsec_ee8fcf7616f27578757c8e44f4e02bf39e1ea96e0b87a3a7d92838776a326e45'


def home(request):
    return render(request, 'index.html')


def pricing(request):
    return render(request, 'pricing.html')


def letter(request):
    return render(request, 'send_letter.html')


def submitted_info(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        university = request.POST.get('university')
        decision = request.POST.get('decision')
        university_cap = university.capitalize() + ' ' + "Office of Undergraduate Admissions"

        print(full_name, email, university, decision, university_cap)

        try:
            send_email(sender_name=university_cap, receiver_email=email, first_name=full_name, decision=decision, university=university)
            print("sent!")
        except Exception as e:
            print(f"error : {e}")

        return render(request, 'confirmation.html')

    return render(request, 'send_letter.html')


def peasant(request):
    return render(request, 'payments.html')


def handle_checkout_session(session):
    # Example function to handle checkout session completion
    # Get customer id from session and update the user's subscription status
    customer_id = session.get('customer')
    user = User.objects.get(stripe_customer_id=customer_id)


@require_POST
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('HTTP_STRIPE_SIGNATURE')

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(payment_intent)
        # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event['type']))

    return JsonResponse({'success': True})

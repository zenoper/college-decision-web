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
from .models import Payment, LetterGeneration, UniversityDecision

from environs import Env
env = Env()
env.read_env()

stripe.api_key = env.str("STRIPE_KEY")


def home(request):
    return render(request, 'index.html')


# def pricing(request):
#     return render(request, 'pricing.html')


def letter(request):
    # credits = int(request.COOKIES.get('emailCredits', 0))
    # if credits > 0:
    return render(request, 'send_letter.html')
    # else:
    #     return redirect('/checkout/')


def submitted_info(request):
    if request.method == 'POST':
        # credits = int(request.COOKIES.get('emailCredits', 0))
        EMAIL_REGEX = r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+'


        email_to = request.POST.get('email', '').strip().lower()
        # 1. Basic validation checks
        if not email_to:
            print("no email")
            return render(request, 'invalid_email.html')
        

        # 2. Regex check
        if not re.match(EMAIL_REGEX, email_to):
            print("regex fail")
            return render(request, 'invalid_email.html')
        
        # 3. Block common disposable email domains
        BLOCKED_DOMAINS = [
            'temp-mail.org',
            'tempmail.com',
            # Add more as needed
        ]
        email_domain = email_to.split('@')[1]
        if any(blocked in email_domain for blocked in BLOCKED_DOMAINS):
            print("blocked domain")
            return render(request, 'invalid_email.html')
            
        # New check: Block emails containing "edu"
        if "edu" in email_to.lower():
            print("edu email blocked")
            return render(request, 'invalid_email.html')
        
         # 4. Additional validation for educational institutions
        # ALLOWED_EDU_DOMAINS = ['.edu', '.k12.', '.ac.', '.sch.']
        # if not any(edu_domain in email_domain for edu_domain in ALLOWED_EDU_DOMAINS):
        #     print("no edu domain")
        #     return render(request, 'invalid_email.html')

        # 5. Rate limiting (you'll need to implement this using Django's cache framework)
        from django.core.cache import cache
        cache_key = f'email_attempts_{request.META.get("REMOTE_ADDR")}'
        attempts = cache.get(cache_key, 0)
        if attempts > 5:  # Max 5 attempts per hour
            print("hitting rate limit")
            return render(request, 'rate_limit.html')
        cache.set(cache_key, attempts + 1, 3600)  # 1 hour expiry

        # If all checks pass, proceed with the rest of your code
        full_name = request.POST.get('full_name')
        # email = request.POST.get('email')
        university = request.POST.get('university')
        decision = request.POST.get('decision')
        university_cap = university.capitalize() + ' ' + "Office of Undergraduate Admissions"
        # payment = Payment.objects.filter(user_email=email).first()

        # if re.match(EMAIL_REGEX, email_to):
            # Check if the user has enough credits
            # print(credits, payment, payment.emails_purchased, payment.emails_sent)
            # if credits and payment and payment.emails_purchased > payment.emails_sent:
        email_sent = False
        try:
            # First try to send the email
            send_email(sender_name=university_cap, 
                      receiver_email=email_to, 
                      first_name=full_name, 
                      decision=decision, 
                      university=university)
            email_sent = True

        except Exception as e:
            print("Detailed error info:")
            print(f"Type: {type(e)}")
            print(f"Args: {e.args}")
            print(f"Error: {str(e)}")
            raise

        # Only update statistics if email was sent successfully
        if email_sent:
            # Update letter generation stats
            letter_stats, created = LetterGeneration.objects.get_or_create(
                email=email_to,
                defaults={
                    'full_name': request.POST.get('full_name'),
                }
            )
            
            if not created:
                letter_stats.full_name = request.POST.get('full_name')
                letter_stats.letters_generated += 1
                letter_stats.save()

            # Update university decision stats
            uni_decision, _ = UniversityDecision.objects.get_or_create(
                university=university,
                decision_type=decision,
                defaults={'decision_count': 1}
            )
            if not _:  # if the object already existed
                uni_decision.decision_count += 1
                uni_decision.save()

            response = render(request, 'confirmation.html')
            return response
        # else:
            # Not enough credits, redirect to the payment page
            # return render(request, 'pay_bro.html')
        # else:
        #     # Invalid email format
        #     return render(request, 'invalid_email.html')

    return render(request, 'send_letter.html')


def invalid_email(request):
    return render(request, 'invalid_email.html')


# def checkout(request):
#     # Here you can pass the order details to the template for review
#     order_details = {
#         # Example data structure - replace this with actual order data
#         'items': [
#             {'name': 'Product 1', 'price': 10, 'quantity': 1},
#             {'name': 'Product 2', 'price': 5, 'quantity': 1},
#         ],
#         'total': 2000,  # Example total
#     }
#
#     return render(request, 'checkout.html', {'order_details': order_details})


# @require_POST
# def create_checkout_session(request):
#     YOUR_DOMAIN = "https://college-decision.com"
#     try:
#         checkout_session = stripe.checkout.Session.create(
#             line_items=[
#                 {
#                     'price': 'price_1OceKfH7wZCCmn5aMh7Izt0I',
#                     'quantity': 3,
#                 },
#             ],
#             mode='payment',
#             success_url=YOUR_DOMAIN + '/payment-success/?session_id={CHECKOUT_SESSION_ID}',
#             cancel_url=YOUR_DOMAIN + '/cancel/',
#             metadata={
#                 'emails_purchased': 3,
#             }
#         )
#     except Exception as e:
#         return JsonResponse({'error': str(e)})
#
#     return redirect(checkout_session.url)
    

# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     endpoint_secret = env.str("ENDPOINT_SECRET")
#
#     try:
#         event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
#     except ValueError as e:
#         return JsonResponse({'error': str(e)}, status=400)
#     except stripe.error.SignatureVerificationError as e:
#         return JsonResponse({'error': str(e)}, status=400)
#
#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']
#         customer_email = session.get('customer_details', {}).get('email')
#         emails_purchased = int(session['metadata']['emails_purchased'])
#         print(f"customer email : {customer_email}, emails purchased : {emails_purchased}, session : {session}")
#         try:
#             payment, created = Payment.objects.get_or_create(
#                 user_email=customer_email
#             )
#             payment.emails_purchased += emails_purchased
#             payment.save()
#             
#             # Store the session ID in metadata for later use
#             session.metadata['credits_to_add'] = str(emails_purchased)
#             session.save()
#             
#             print(f"Payment updated for {customer_email}: {emails_purchased} emails purchased")
#         except Exception as e:
#             print(f"Error updating payment: {str(e)}")
#
#     return JsonResponse({'status': 'success'}, status=200)


# def payment_success(request):
#     session_id = request.GET.get('session_id')
#
#     if not session_id:
#         return redirect('error_page')
# 
#     try:
#         # Retrieve the session from Stripe
#         session = stripe.checkout.Session.retrieve(session_id)
#
#         # Get the number of credits purchased from the session metadata
#         credits_purchased = int(session.metadata.get('emails_purchased', 0))
#
#         # Get current credits from cookie
#         current_credits = int(request.COOKIES.get('emailCredits', 0))
#
#         # Calculate new total credits
#         new_credits = current_credits + credits_purchased
#
#         # Render the success page
#         response = render(request, 'success.html')
#         print(f"new credits set : {new_credits}")
#         # Set the new credit amount in the cookie
#         response.set_cookie('emailCredits', str(new_credits), max_age=60*60*24*30)  # Set cookie for 30 days
#
#         return response
#
#     except Exception as e:
#         print(f"Error in payment_success: {str(e)}")
#         return redirect('error_page')


# def cancel(request):
#     return render(request, 'cancel.html')


# def pay_bruh(request):
#     return render(request, 'pay_bro.html')


# def error_page(request):
#     return render(request, 'error.html')


# def prices(request):
#     return render(request, 'pricing.html')


from django.shortcuts import render
from .send_email import send_email, send_notification_email
import re
import logging
from django.http import HttpResponse

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Payment, LetterGeneration, UniversityDecision, DecisionToken

from environs import Env
env = Env()
env.read_env()

# Get logger for this module
logger = logging.getLogger(__name__)

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
        EMAIL_REGEX = r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+'

        email_to = request.POST.get('email', '').strip().lower()
        # 1. Basic validation checks
        if not email_to:
            logger.warning("No email provided in submitted_info")
            return render(request, 'invalid_email.html')
        
        # 2. Regex check
        if not re.match(EMAIL_REGEX, email_to):
            logger.warning(f"Invalid email format: {email_to}")
            return render(request, 'invalid_email.html')
        
        # 3. Block common disposable email domains
        BLOCKED_DOMAINS = [
            'temp-mail.org',
            'tempmail.com',
            # Add more as needed
        ]
        email_domain = email_to.split('@')[1]
        if any(blocked in email_domain for blocked in BLOCKED_DOMAINS):
            logger.warning(f"Blocked domain: {email_domain}")
            return render(request, 'invalid_email.html')
            
        # New check: Block emails containing "edu"
        if "edu" in email_to.lower():
            logger.warning(f"Edu email blocked: {email_to}")
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
            logger.warning(f"Rate limit hit for IP: {request.META.get('REMOTE_ADDR')}")
            return render(request, 'rate_limit.html')
        cache.set(cache_key, attempts + 1, 3600)  # 1 hour expiry

        # Get form data
        full_name = request.POST.get('full_name')
        university = request.POST.get('university')
        decision = request.POST.get('decision')
        
        # Generate unique token and application ID
        import uuid
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        token = uuid.uuid4().hex
        application_id = f"APP-2025-{str(uuid.uuid4().int)[:6]}"
        decision_date = datetime.now().strftime("%B %d, %Y")
        
        # Create portal URL
        from .university_config import UNIVERSITY_CONFIG
        uni_config = UNIVERSITY_CONFIG.get(university, {})
        subdomain = uni_config.get('subdomain', university.lower())
        portal_url = f"https://{subdomain}.college-decision.com/portal/{token}/"
        
        # Create DecisionToken record
        expires_at = timezone.now() + timedelta(days=7)
        DecisionToken.objects.create(
            token=token,
            full_name=full_name,
            university=university,
            decision=decision,
            email=email_to,
            application_id=application_id,
            expires_at=expires_at
        )
        
        # Send notification email instead of decision letter
        send_notification_email(
            receiver_email=email_to,
            full_name=full_name,
            university=university,
            portal_url=portal_url,
            application_id=application_id,
            decision_date=decision_date
        )

        # Update letter generation stats
        try:
            letter_stats, created = LetterGeneration.objects.get_or_create(
                email=email_to,
                defaults={
                    'full_name': full_name,
                }
            )
            
            if not created:
                letter_stats.full_name = full_name
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
        except Exception as e:
            logger.error(f"Error updating stats for email {email_to}: {e}")
            # If database operations fail, we still want to show success since email was sent
            pass

        return render(request, 'confirmation.html')

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


def portal_view(request, token):
    """
    View function for university decision portal
    Validates token and displays the appropriate decision letter
    """
    try:
        # Get decision token from database
        decision_token = DecisionToken.objects.get(token=token)
        
        # Check if token has expired
        if decision_token.is_expired():
            return render(request, 'portal_expired.html')
        
        # Get university configuration
        from .university_config import UNIVERSITY_CONFIG
        uni_config = UNIVERSITY_CONFIG.get(decision_token.university, {})
        
        # Mark token as viewed
        decision_token.mark_viewed()
        
        # Determine which template to use based on decision
        template_name = f"portal/{decision_token.university.lower()}_portal.html"
        
        # Prepare context for template
        context = {
            'full_name': decision_token.full_name,
            'university': decision_token.university,
            'decision': decision_token.decision,
            'application_id': decision_token.application_id,
            'university_config': uni_config,
        }
        
        # Render the portal page
        return render(request, template_name, context)
        
    except DecisionToken.DoesNotExist:
        return render(request, 'portal_invalid.html')


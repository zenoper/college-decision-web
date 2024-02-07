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



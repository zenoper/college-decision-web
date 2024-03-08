from django.shortcuts import render
from .send_email import send_email
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


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

        if re.match(EMAIL_REGEX, email):
            try:
                send_email(sender_name=university_cap, receiver_email=email, first_name=full_name, decision=decision, university=university)
            except Exception as e:
                print(f"error : {e}")

            return render(request, 'confirmation.html')
        else:
            return render(request, 'invalid_email.html')

    return render(request, 'send_letter.html')


def invalid_email(request):
    return render(request, 'invalid_email.html')




from django.shortcuts import render
from django.http import HttpResponse


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

        print(full_name, email, university, decision)

        return HttpResponse(f'Thank you, {full_name}! Your submission has been received.')

    return render(request, 'send_letter.html')
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from environs import Env
env = Env()
env.read_env()


university_dictionary = {
    'Acceptance': {
        'Stanford': 'college_decision/templates/decision_letters/Stanford/stanford_acceptance.html',
        'Harvard': 'college_decision/templates/decision_letters/Harvard/harvard_acceptance.html',
        'Yale': 'college_decision/templates/decision_letters/Yale/yale_acceptance.html',
        'Dartmouth': 'college_decision/templates/decision_letters/Dartmouth/dartmouth_acceptance.html',
        'Duke': 'college_decision/templates/decision_letters/Duke/duke_acceptance.html',
        'Nyuad': 'college_decision/templates/decision_letters/NYUAD/nyuad_acceptance.html',
        'Princeton': 'college_decision/templates/decision_letters/Princeton/princeton_acceptance.html',
        'Uchicago': 'college_decision/templates/decision_letters/Uchicago/uchicago_acceptance.html'
    },
    'Rejection': {
        'Harvard': 'college_decision/templates/decision_letters/Harvard/harvard_rejection.html',
        'Yale': 'college_decision/templates/decision_letters/Yale/yale_rejection.html',
        'Dartmouth': 'college_decision/templates/decision_letters/Dartmouth/dartmouth_rejection.html',
        'Duke': 'college_decision/templates/decision_letters/Duke/duke_rejection.html',
        'Nyuad': 'college_decision/templates/decision_letters/NYUAD/nyuad_rejection.html',
        'Princeton': 'college_decision/templates/decision_letters/Princeton/princeton_rejection.html',
        'Uchicago': 'college_decision/templates/decision_letters/Uchicago/uchicago_rejection.html',
        'Stanford': 'college_decision/templates/decision_letters/Stanford/stanford_rejection.html'
    }
}


def send_email(sender_name, receiver_email, first_name, decision, university):
    # Replace with your SMTP credentials and SES region
    smtp_username = env.str("SMTP_USERNAME")
    smtp_password = env.str("SMTP_PASSWORD")
    aws_region = env.str("AWS_REGION")

    # Replace with the verified email address associated with your SES account
    sender_email = 'simulator@college-decision.com'

    with open(university_dictionary[decision][university], 'r') as f:
        html_body = f.read()

    # Add dynamic content to HTML body
    html_body = html_body.replace('Dear,', f'Dear {first_name},')

    if university == 'uchicago':
        sender_name = "UChicago Office of Undergraduate Admissions"

    # Set up the email message
    message = MIMEMultipart("alternative")
    message["From"] = f"{sender_name} <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = "View Update to your Application!"
    message.attach(MIMEText(html_body, "html"))

    # Connect to the Amazon SES SMTP server
    smtp_server = smtplib.SMTP('email-smtp.' + aws_region + '.amazonaws.com', 587)
    smtp_server.starttls()

    # Log in to the SMTP server
    smtp_server.login(smtp_username, smtp_password)

    # Send the email
    smtp_server.sendmail(sender_email, receiver_email, message.as_string())

    # Disconnect from the server
    smtp_server.quit()
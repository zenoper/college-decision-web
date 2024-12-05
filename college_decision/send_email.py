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
    try:
        # SMTP Configuration - same as test.py
        smtp_username = env.str("SMTP_USERNAME")
        smtp_password = env.str("SMTP_PASSWORD")
        aws_region = env.str("AWS_REGION")
        smtp_endpoint = f'email-smtp.{aws_region}.amazonaws.com'
        # print(f"username: {type(smtp_username)}, password: {type(smtp_password)}, aws-region: {type(aws_region)}, endpoint: {type(smtp_endpoint)}")
        # print(f"username: {smtp_username}, password: {smtp_password}, aws-region: {aws_region}, endpoint: {smtp_endpoint}")

        # Get HTML content
        with open(university_dictionary[decision][university], 'r') as f:
            html_body = f.read()

        # Add dynamic content to HTML body
        html_body = html_body.replace('Dear,', f'Dear {first_name},')

        # Create message
        message = MIMEMultipart()
        message["From"] = f"{sender_name} <simulator@college-decision.com>"
        message["To"] = receiver_email
        message["Subject"] = "View Update to your Application!"
        message.attach(MIMEText(html_body, "html"))

        # Connect and send - same as test.py
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_endpoint, 587)
        server.starttls()
        print("TLS started")
        
        print("Attempting login...")
        server.login(smtp_username, smtp_password)
        print("Login successful!")
        
        print("Sending email...")
        server.sendmail("simulator@college-decision.com", receiver_email, message.as_string())
        print("Email sent successfully!")
        
        server.quit()

    except Exception as e:
        print("Error occurred:")
        print(f"Type: {type(e)}")
        print(f"Args: {e.args}")
        print(f"Error: {str(e)}")
        raise
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from environs import Env
from django.template.loader import render_to_string
from .university_config import UNIVERSITY_CONFIG

# Get logger for this module
logger = logging.getLogger(__name__)

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

# Portal templates for each university
portal_templates = {
    'Harvard': 'college_decision/templates/portal/harvard_portal.html',
    'Yale': 'college_decision/templates/portal/yale_portal.html',
    'Stanford': 'college_decision/templates/portal/stanford_portal.html',
    'Dartmouth': 'college_decision/templates/portal/dartmouth_portal.html',
    'Duke': 'college_decision/templates/portal/duke_portal.html',
    'Princeton': 'college_decision/templates/portal/princeton_portal.html',
    'Uchicago': 'college_decision/templates/portal/uchicago_portal.html',
    'Nyuad': 'college_decision/templates/portal/nyuad_portal.html'
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
        # Connect and send - same as test.py
        logger.info(f"Connecting to SMTP server at {smtp_endpoint}...")
        server = smtplib.SMTP(smtp_endpoint, 587, timeout=10)
        server.starttls()
        logger.info("TLS started")
        
        logger.info("Attempting login...")
        server.login(smtp_username, smtp_password)
        logger.info("Login successful!")
        
        logger.info("Sending email...")
        server.sendmail("simulator@college-decision.com", receiver_email, message.as_string())
        logger.info("Email sent successfully!")
        
        server.quit()

    except Exception as e:
        logger.error("Error occurred:")
        logger.error(f"Type: {type(e)}")
        logger.error(f"Args: {e.args}")
        logger.error(f"Error: {str(e)}")
        raise


def send_notification_email(receiver_email, full_name, university, portal_url, application_id, decision_date):
    """
    Send a neutral notification email with a link to the portal
    """
    try:
        # Get university configuration
        uni_config = UNIVERSITY_CONFIG.get(university, {})
        
        # Render email template with dynamic content
        html_body = render_to_string('emails/status_update_notification.html', {
            'university_name': uni_config.get('full_name', university),
            'university_logo_url': uni_config.get('logo_url', ''),
            'university_color': uni_config.get('primary_color', '#333333'),
            'full_name': full_name,
            'portal_url': portal_url,
            'application_id': application_id,
            'decision_date': decision_date,
            'contact_email': uni_config.get('contact_email', ''),
            'contact_phone': uni_config.get('contact_phone', ''),
        })
        
        # Create message
        message = MIMEMultipart()
        message["From"] = f"{uni_config.get('full_name', university)} Admissions <simulator@college-decision.com>"
        message["To"] = receiver_email
        message["Subject"] = f"Application Status Update - {uni_config.get('full_name', university)}"
        message.attach(MIMEText(html_body, "html"))

        # SMTP Configuration
        smtp_username = env.str("SMTP_USERNAME")
        smtp_password = env.str("SMTP_PASSWORD")
        aws_region = env.str("AWS_REGION")
        smtp_endpoint = f'email-smtp.{aws_region}.amazonaws.com'
        
        # Connect and send
        # Connect and send
        logger.info(f"Connecting to SMTP server at {smtp_endpoint}...")
        server = smtplib.SMTP(smtp_endpoint, 587, timeout=10)
        server.starttls()
        logger.info("TLS started")
        
        logger.info("Attempting login...")
        server.login(smtp_username, smtp_password)
        logger.info("Login successful!")
        
        logger.info("Sending notification email...")
        server.sendmail("simulator@college-decision.com", receiver_email, message.as_string())
        logger.info("Notification email sent successfully!")
        
        server.quit()
        
    except Exception as e:
        logger.error("Error occurred while sending notification email:")
        logger.error(f"Type: {type(e)}")
        logger.error(f"Args: {e.args}")
        logger.error(f"Error: {str(e)}")
        raise
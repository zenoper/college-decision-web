import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from environs import Env

env = Env()
env.read_env()

def test_email_send():
    # SMTP Configuration
    smtp_username = env.str("SMTP_USERNAME")
    smtp_password = env.str("SMTP_PASSWORD")
    aws_region = env.str("AWS_REGION")
    smtp_endpoint = f'email-smtp.{aws_region}.amazonaws.com'
    # print(f"username: {type(smtp_username)}, password: {type(smtp_password)}, aws-region: {type(aws_region)}, endpoint: {type(smtp_endpoint)}")
    # print(f"username: {smtp_username}, password: {smtp_password}, aws-region: {aws_region}, endpoint: {smtp_endpoint}")


    # Email content
    sender_email = 'simulator@college-decision.com'
    receiver_email = 'mukhammadkodirmakhmudjanov@gmail.com'  # Replace with a test email address
    subject = 'Test Email from Python Script'
    body = 'This is a test email sent from the Python test script.'

    # Create message
    message = MIMEMultipart()
    message["From"] = f"Test Sender <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to SMTP server
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_endpoint, 587)
        server.starttls()
        print("TLS started")
        
        # Login
        print("Attempting login...")
        server.login(smtp_username, smtp_password)
        print("Login successful!")
        
        # Send email
        print("Sending email...")
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
        
        server.quit()
        
    except Exception as e:
        print("Error occurred:")
        print(f"Type: {type(e)}")
        print(f"Args: {e.args}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_email_send()
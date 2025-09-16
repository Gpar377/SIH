import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Your demo email config
EMAIL_CONFIG = {
    "sender_email": "projectsih85@gmail.com",
    "sender_password": "jydfpidajkkaznoi",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}

def test_email():
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = "gopaparthiv@gmail.com"
        msg['Subject'] = "🚨 Test Email - SIH Demo"
        
        body = """
Test email from EduAlert System

This is a test to verify email functionality is working.

Time: Testing email delivery
Status: Demo mode active
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], "gopaparthiv@gmail.com", text)
        server.quit()
        
        print("EMAIL SENT SUCCESSFULLY!")
        print("Check gopaparthiv@gmail.com inbox")
        
    except Exception as e:
        print(f"EMAIL FAILED: {e}")

if __name__ == "__main__":
    test_email()
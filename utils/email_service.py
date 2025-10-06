import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for
import random
import string

def send_email(to_email, subject, html_content):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()

            if current_app.config['MAIL_USERNAME'] and current_app.config['MAIL_PASSWORD']:
                server.login(
                    current_app.config['MAIL_USERNAME'],
                    current_app.config['MAIL_PASSWORD']
                )

            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def send_password_reset_email(user_email, reset_token):
    reset_url = url_for('auth.reset_password', token=reset_token, _external=True)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #28a745;
                      color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SHCAP Password Reset</h1>
            </div>
            <div class="content">
                <h2>Reset Your Password</h2>
                <p>You requested to reset your password for your SHCAP account.</p>
                <p>Click the button below to reset your password:</p>
                <a href="{reset_url}" class="button">Reset Password</a>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all;">{reset_url}</p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <p>If you didn't request this, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 SHCAP - SmallHolder Carbon Assessment Platform</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(user_email, "SHCAP - Password Reset Request", html)

def generate_2fa_code():
    return ''.join(random.choices(string.digits, k=6))

def send_2fa_code_email(user_email, code):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .code {{ font-size: 32px; font-weight: bold; text-align: center;
                     background-color: #fff; padding: 20px; margin: 20px 0;
                     border: 2px dashed #28a745; letter-spacing: 5px; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SHCAP Two-Factor Authentication</h1>
            </div>
            <div class="content">
                <h2>Your Verification Code</h2>
                <p>Enter this code to complete your login:</p>
                <div class="code">{code}</div>
                <p><strong>This code will expire in 10 minutes.</strong></p>
                <p>If you didn't request this code, please secure your account immediately.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 SHCAP - SmallHolder Carbon Assessment Platform</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(user_email, "SHCAP - Two-Factor Authentication Code", html)

def send_welcome_email(user_email, first_name):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to SHCAP!</h1>
            </div>
            <div class="content">
                <h2>Hello {first_name},</h2>
                <p>Thank you for registering with the SmallHolder Carbon Assessment Platform (SHCAP).</p>
                <p>Your account has been successfully created. You can now access our platform to:</p>
                <ul>
                    <li>Estimate Above Ground Biomass (AGB)</li>
                    <li>Manage carbon assessment projects</li>
                    <li>Collaborate with other researchers and project developers</li>
                </ul>
                <p>If you have any questions, feel free to contact our support team.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 SHCAP - SmallHolder Carbon Assessment Platform</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(user_email, "Welcome to SHCAP", html)

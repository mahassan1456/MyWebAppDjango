import smtplib, ssl
from twilio.rest import Client
import os
from smtplib import  SMTPResponseException as SMTPExc
from twilio.base.exceptions import TwilioException, TwilioRestException 

AUTH_TOKEN = '010a7438fe4eb47acdb3cd55ec3b1116'
ACCOUNT_SID = 'AC69d437937a56eea0df43dfc62642d2ee'
MSG_SERV_SID = 'MGcaa37533bd0d8d597d654bbb3f95c24c'


def send_msg_email(message):
    sender_email = 'accounts@randomthoughtz.com'
    smtp_server = 'mail.privateemail.com'
    port = 465
    login = "accounts@randomthoughtz.com"
    password = "Iverson01"
    to_email = 'specialreminder@gmail.com'
    context = ssl.create_default_context()
  
    with smtplib.SMTP_SSL(smtp_server,port=port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, to_email, message)

def evaluate(value):
    if not value:
        return False
    return True

def send_sms(message='There has been a new facility added. Please check administrative console for more information'):
    AUTH_TOKEN = '010a7438fe4eb47acdb3cd55ec3b1116'
    auth_token = '010a7438fe4eb47acdb3cd55ec3b1116'
    account_sid = 'AC69d437937a56eea0df43dfc62642d2ee'
    
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        messaging_service_sid='MGcaa37533bd0d8d597d654bbb3f95c24c',
        body=message,
        to='+17134829222'
    )



    
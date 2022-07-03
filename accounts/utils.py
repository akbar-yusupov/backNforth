import os

from twilio.rest import Client

from chat.models import Thread

# accounts_sid = ""
# auth_token = ""
# client = Client(accounts_sid, auth_token)
#
#
# def send_sms(user_code, phone_number):
#     message = client.messages.create(
#         body=f"Hi! Your verification code is {user_code}",
#         from_=client
#         to=phone_number,
#     )


"""
    A stub for twilio, since it is impossible to send messages to other numbers 
    during the test period
"""


def send_sms(user_code, phone_number):
    return user_code


def get_support_thread(bot_id):
    support_thread = Thread.objects.filter(second_person__user=bot_id).first()
    return support_thread

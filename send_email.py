import smtplib
import os

MY_EMAIL = os.environ.get('EMAIL_SENDER')
PASSWORD = os.environ.get('PASSWORD_SENDER')
CHOOSE_EMAIL = os.environ.get('BUSINESS_EMAIL')

class Send_Email():
    def __init__(self, msg_name, msg_email, msg_message):
        self.connect = smtplib.SMTP('smtp.gmail.com', port=587)
        self.connect.starttls()
        self.connect.login(user=MY_EMAIL, password=PASSWORD)
        self.connect.sendmail(from_addr=MY_EMAIL, to_addrs=CHOOSE_EMAIL,
                              msg=f"Subject: MESSAGE from IGI-Blog website: {msg_name}\n\n "
                                    f"from: {msg_name}, {msg_email}\n "
                                    f"{msg_message}")
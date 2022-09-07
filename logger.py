from datetime import datetime
from email import message
from http import server

from django.dispatch import receiver
import directories as DIR
import smtplib

class Logger:

    def __init__(self, path, process):
        self.path = path
        self.process = process
        self.logger = None
        
        if self.process == 'conversion':
            self.email_content = ''
        

    def init_log(self):
        DIR_LOGS = self.path + DIR.LOGS
        date_time_info = datetime.now()
        self.start_time = date_time_info.strftime('%m.%d.%y.%H.%M.%S')
        log_filename = f'{self.process}.{self.start_time}.log'

        self.logger = open(DIR_LOGS + log_filename, 'w', encoding='utf-8')

    def __del__(self):
        if self.logger:
            self.logger.close()

    def log(self, msg):
        if self.logger:
            self.logger.write(msg)
        try:
            self.email_content += msg
        except:
            pass

    def email(self):

        if self.err_count != 0 or self.invalid_count != 0 or self.success_count != 0 or self.sent_count != 0:

            sender_email = 'syd.frisco@gmail.com'
            receiver_email = 'johnsydrick.frisco@straive.com'
            password = 'oljdwaraolfmzsqr'
            message = self.email_content

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


        


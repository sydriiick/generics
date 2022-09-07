from logger import Logger
import directories as DIR
import sender_data as SD
import ftplib
import os
import re


class Sender(Logger):

    def __init__(self, conv_path):
        self.conv_path = conv_path
        self.ftp = None

        Logger.__init__(self, conv_path, 'sending')

    def __del__(self):
        if self.ftp:
            self.ftp.quit()

        Logger.__del__(self)

    def init_ftp(self):

        self.init_log()

    def send(self):
        DIR_OUTPUT = self.conv_path + DIR.OUTPUT
        BLOCK_SIZE = 262144

        sent = 0

        _, _, green_zips = next(os.walk(DIR_OUTPUT))

        try:
            self.init_ftp()
            for green_zip in green_zips:
                sent += 1
                self.log(f'{green_zip} sent\n')


        except Exception as e:
            self.log(f'sent - {str(sent)}\n{str(e)}\n')

        return sent

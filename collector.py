from datetime import datetime
from logger import Logger
import directories as DIR


class Collector(Logger):

    def __init__(self, coll_path, encoding):
        self.coll_path = coll_path
        self.encoding = encoding

        Logger.__init__(self, coll_path, 'collection')

        self.load_checkfile()

    def load_checkfile(self):
        self.check_list = set()

        with open(self.coll_path + 'checkfile.txt', 'r', encoding='utf-8') as checkfile:
            for line in checkfile:
                self.check_list.add(line.strip())

    def update_checkfile(self, filekeys):
        if len(filekeys):
            with open(self.coll_path + 'checkfile.txt', 'a', encoding='utf-8') as checkfile:
                checkfile.write('\n'.join(filekeys) + '\n')

    def write_coll_log_header(self):
        self.log('########################################\n')
        self.log('# Collection log\n')
        self.log('########################################\n\n')
        self.log(f'Start time: {self.start_time}\n\n')
        self.log('########################################\n')
        self.log('# Contents\n')
        self.log('########################################\n\n')

    def write_coll_log_footer(self, input_files, doc_count=0):
        self.log('\n########################################\n')
        self.log('# Input files downloaded\n')
        self.log('########################################\n\n')
        self.log('\n'.join(input_files) + '\n\n')
        self.log(f'Total number of files: {str(len(input_files))}\n\n')
        if doc_count:
            self.log(f'Total number of articles: {str(doc_count)}\n\n')
        date_time_end = str(datetime.now())
        self.log(f'End time: {date_time_end}\n')

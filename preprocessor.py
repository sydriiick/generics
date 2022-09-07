from datetime import datetime
from logger import Logger
from hashlib import md5
from os import walk
import utilities as UTIL
import directories as DIR


class Preprocessor(Logger):

    def __init__(self, coll_path, conv_path, encoding):
        self.coll_path = coll_path
        self.conv_path = conv_path
        self.encoding = encoding

        self.total = 0
        self.reps = 0
        self.adds = 0
        self.dels = 0
        self.drop = 0
        self.drop_log = ''

        self.batch_map = {}
        self.rep_batch_map = {}
        self.rep_table = {}

        Logger.__init__(self, coll_path, 'preprocess')

    def __del__(self):
        Logger.__del__(self)

    def fix_chars(self, content, char_map):
        for k, v in char_map.items():
            content = content.replace(k, v)

        return content

    def read_content(self, input_filename, another_encoding=''):
        try:
            with open(input_filename, "r", encoding=self.encoding) as reader:
                return reader.read()
        except Exception:
            if another_encoding:
                self.log(f'{input_filename} <===> encoding is {another_encoding}\n')
                with open(input_filename, "rb") as reader:
                    return reader.read().decode(another_encoding).encode(self.encoding).decode(self.encoding)
            else:
                self.log(f'{input_filename} <===> encoding error\n')
                raise Exception('Encoding error\n')

    def load_repfile(self):
        with open(self.coll_path + 'repfile.txt', 'r', encoding='utf-8') as reader:
            for line in reader:
                line = line.replace('\n', '')
                key, value = line.split('###')
                self.rep_table[key] = value

    def update_repfile(self):
        with open(self.coll_path + 'repfile.txt', 'w', encoding='utf-8') as writer:
            for key, value in self.rep_table.items():
                writer.write(f'{key}###{value}\n')

    def add_article_with_rep(self, article_id, batch_key, content, hash_code):
        if article_id in self.rep_table and self.rep_table[article_id] != hash_code:
            if batch_key in self.rep_batch_map:
                self.rep_batch_map[batch_key] += content
            else:
                self.rep_batch_map[batch_key] = content
            self.reps += 1
        elif article_id not in self.rep_table:
            if batch_key in self.batch_map:
                self.batch_map[batch_key] += content
            else:
                self.batch_map[batch_key] = content
            self.adds += 1
        else:
            self.drop += 1

        self.total += 1
        self.rep_table[article_id] = hash_code

    def add_article(self, batch_key, content):
        if batch_key in self.batch_map:
            self.batch_map[batch_key] += content
        else:
            self.batch_map[batch_key] = content

        self.adds += 1
        self.total += 1

    def drop_article(self, drop_msg):
        self.drop += 1
        self.total += 1
        self.drop_log += drop_msg

    def log_summary(self):
        self.log('Summary:\n\n')
        self.log(f'Total articles - {self.total}\n')
        self.log(f'adds - {self.adds}\n')
        self.log(f'reps - {self.reps}\n')
        self.log(f'dels - {self.dels}\n')
        self.log(f'drop - {self.drop}\n')
        if self.drop_log:
            self.log(f'{self.drop_log}')

    def get_article_hash_code(self, content):
        return md5(content.encode()).hexdigest()

    def get_batch_hash_code(self, batch_id):
        return md5(batch_id.encode()).hexdigest()[:16]

    def create_combined_file(self, combined_filename, content):
        with open(combined_filename, "w", encoding=self.encoding) as writer:
            writer.write(content)

    def create_imagelist(self, imagelist_filename, image_dir):
        with open(imagelist_filename, "w", encoding=self.encoding) as writer:
            _, _, images = next(walk(image_dir))
            for image in images:
                writer.write(image + '\n')

    def create_imagezip(self, imagezip_filename, image_dir, clean_img_dir=False):
        if clean_img_dir:
            UTIL.compress_files(imagezip_filename, image_dir)
        else:
            UTIL.compress_files_no_removal(imagezip_filename, image_dir)

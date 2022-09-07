from bs4 import BeautifulSoup
from collector import Collector
from datetime import datetime
import directories as DIR
import requests
import os
import re


class WebCollector(Collector):

    def __init__(self, coll_path, encoding, article_tag, headers='', has_ext_body=False):
        self.article_tag = article_tag
        self.headers = headers
        self.has_ext_body = has_ext_body

        Collector.__init__(self, coll_path, encoding)

    def get_data(self, url, headers):
        if headers:
            return requests.get(url, headers=headers)
        else:
            if hasattr(self, 'auth'):
                return requests.get(url, auth=self.auth)
            else:
                return requests.get(url)

    def create_rawdata(self, raw_filename, content):
        with open(f'{self.coll_path}{DIR.INPUT}{raw_filename}', 'w', encoding=self.encoding) as writer:
            writer.write(content)

    def web_collect(self, get_doc_id, get_urls, insert_body=None):
        self.init_log()
        self.write_coll_log_header()

        raw_files = []
        doc_count = 0
        for pub, urls in get_urls().items():
            self.log(f'\n{pub}\n')

            raw_filename = f'{pub}_{self.start_time}.xml'
            content = ''
            docid_list = []
            dup_count = 0
            trans_count = 0

            try:
                for url in urls:
                    self.log(f'{url}\n')

                    data = self.get_data(url, self.headers)

                    scraper = BeautifulSoup(data.content, 'html.parser')
                    content += str(scraper)

                    articles = scraper.find_all(self.article_tag)

                    for article in articles:
                        docid = str(get_doc_id(article))

                        if docid in self.check_list:
                            dup_count += 1
                            self.log(f'Duplicate article id: {docid}\n')
                            content = content.replace(str(article), '')
                        else:
                            if self.has_ext_body:
                                new_article = insert_body(article)
                                content = content.replace(str(article), new_article)
                            trans_count += 1
                            docid_list.append(docid)
                            self.log(f'Transmitted article id: {docid}\n')

                doc_count += trans_count
                self.log(f'Total transmitted: {str(trans_count)}\n')
                self.log(f'Total duplicates:  {str(dup_count)}\n')

                if docid_list:
                    self.update_checkfile(docid_list)

                    self.create_rawdata(raw_filename, content)
                    raw_files.append(raw_filename)

            except Exception as e:
                self.log(str(e))

        self.write_coll_log_footer(raw_files, doc_count)

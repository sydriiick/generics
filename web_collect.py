import os
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re
import directories as DIR


def collect(COLL_PATH, ENCODING, HEADERS, ARTICLE_TAG, GET_URL, GET_DOC_ID, HAS_EXT_BODY=False, INSERT_BODY=None):
    # get current date and time for logging and file naming
    date_time_info = datetime.now()
    date_time = date_time_info.strftime('%m.%d.%y.%H.%M.%S')
    log_filename = 'collection.' + date_time + '.log'
    logfile = open(COLL_PATH + DIR.LOGS + log_filename, 'w', encoding=ENCODING)
    logfile.write('########################################\n')
    logfile.write('# Collection log\n')
    logfile.write('########################################\n\n')
    logfile.write('Start time: ' + str(date_time_info) + '\n\n')

    # Article ID check list
    checkfile = open(COLL_PATH + 'checkfile.txt', 'r', encoding=ENCODING)
    check_list = set()
    for line in checkfile:
        check_list.add(line.strip())
    checkfile.close()

    logfile.write('########################################\n')
    logfile.write('# Contents from each publication url\n')
    logfile.write('########################################\n')

    # Collection of data
    input_list = []
    total_files = 0
    total_docs = 0
    for pub, urls in GET_URL().items():
        logfile.write('\n' + pub + '\n')
        raw_filename = pub + '_' + date_time + '.xml'
        content = ''
        docid_list = []
        dupe = 0
        trans = 0
        try:
            for url in urls:
                logfile.write(url + '\n')
                data = ''
                if HEADERS:
                    data = requests.get(url, headers=HEADERS)
                else:
                    data = requests.get(url)

                scraper = BeautifulSoup(data.content, 'html.parser')
                content += str(scraper)

                # Filtering of Duplicates
                articles = scraper.find_all(ARTICLE_TAG)
                for article in articles:
                    docid = str(GET_DOC_ID(article))
                    if docid in check_list:
                        dupe += 1
                        logfile.write('Duplicate article id: ' + docid + '\n')
                        content = content.replace(str(article), '')
                    else:
                        if HAS_EXT_BODY:
                            body = INSERT_BODY(article)
                            content = content.replace(str(article), body)
                        trans += 1
                        docid_list.append(docid)
                        logfile.write('Transmitted article id: ' + docid + '\n')

            total_docs += trans
            logfile.write('Total transmitted: ' + str(trans) + '\n')
            logfile.write('Total duplicates:  ' + str(dupe) + '\n')

            # Updates list of docids in the checkfile
            if docid_list:
                checkfile = open(COLL_PATH + 'checkfile.txt', 'a+', encoding=ENCODING)
                checkfile.write('\n'.join(docid_list) + '\n')

                # Creation of collected rawdata
                total_files += 1
                input_list.append(raw_filename)
                writer = open(COLL_PATH + DIR.INPUT + raw_filename, 'w', encoding=ENCODING)
                writer.write(content)
                writer.close()

        except Exception as e:
            logfile.write(str(e))

    logfile.write('\n########################################\n')
    logfile.write('# Input files collected\n')
    logfile.write('########################################\n\n')
    logfile.write('\n'.join(input_list) + '\n\n')
    logfile.write('Total number of files:    ' + str(total_files) + '\n')
    logfile.write('Total number of articles: ' + str(total_docs) + '\n\n')

    date_time_end = datetime.now()
    logfile.write('End time: ' + str(date_time_end) + '\n')


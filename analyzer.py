import directories as DIR
import re
import os
from datetime import datetime
from bs4 import BeautifulSoup


def file_to_set(filename, ENCODING):
    reader = open(filename, 'r', encoding=ENCODING)
    fileset = set(reader.read().split('\n'))
    reader.close()
    return fileset


def update_analysis(filename, fileset, ENCODING):
    writer = open(filename, 'a', encoding=ENCODING)
    for elem in fileset:
        writer.write(elem + '\n')
    writer.close()


def update_logs(logfile, filetype, fileset):
    if len(fileset):
        logfile.write('new ' + filetype + ':\n')
        logfile.write('\n'.join(fileset))
        logfile.write('\n\n')
    else:
        logfile.write('no new ' + filetype + '\n\n')


def analyze(COLL_PATH, ENCODING):
    DIR_ANALYSIS = COLL_PATH + DIR.ANALYSIS
    DIR_DATA = COLL_PATH + DIR.DATA

    cur_xpaths = file_to_set(DIR_ANALYSIS + 'xpaths.txt', ENCODING)
    cur_tags = file_to_set(DIR_ANALYSIS + 'tags.txt', ENCODING)
    cur_entities = file_to_set(DIR_ANALYSIS + 'entts.txt', ENCODING)
    cur_nachars = file_to_set(DIR_ANALYSIS + 'nachars.txt', ENCODING)

    new_xpaths = set()
    new_tags = set()
    new_entts = set()
    new_nachars = set()

    _, _, afiles = next(os.walk(DIR_DATA))

    for afile in afiles:
        reader = open(DIR_DATA + afile, encoding=ENCODING)
        content = reader.read()
        content = re.sub(r'<!\[CDATA\[([^\000]*?)]]>', r'\g<1>', content)
        content = re.sub(r'&lt;', '<', content)
        content = re.sub(r'&gt;', '>', content)
        reader.close()
        parser = BeautifulSoup(content, 'html.parser')

        entities = re.findall(r'&(?:amp;)?#?[a-zA-Z0-9]*?;', content)
        for entity in entities:
            if not entity in cur_entities:
                new_entts.add(entity)

        for char in content:
            if ord(char) > 255 and not char in cur_nachars:
                new_nachars.add(char)

        def recursive_analysis(parent, current_xpath):
            nodes = parent.findChildren(recursive=False)
            for node in nodes:
                tmp_xpath = current_xpath + node.name + '/'
                if not tmp_xpath in cur_xpaths:
                    new_xpaths.add(tmp_xpath)
                if not node.name in cur_tags:
                    new_tags.add(node.name)
                recursive_analysis(node, tmp_xpath)

        recursive_analysis(parser, '/')

        os.remove(DIR_DATA + afile)

    update_analysis(DIR_ANALYSIS + 'xpaths.txt', new_xpaths, ENCODING)
    update_analysis(DIR_ANALYSIS + 'tags.txt', new_tags, ENCODING)
    update_analysis(DIR_ANALYSIS + 'entts.txt', new_entts, ENCODING)
    update_analysis(DIR_ANALYSIS + 'nachars.txt', new_nachars, ENCODING)

    logfile = open(COLL_PATH + DIR.LOGS + 'analysis_' + datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + '.log', 'w',
                   encoding=ENCODING)

    update_logs(logfile, 'xpaths', new_xpaths)
    update_logs(logfile, 'tags', new_tags)
    update_logs(logfile, 'entities', new_entts)
    update_logs(logfile, 'non-ascii characters', new_nachars)

    logfile.close()

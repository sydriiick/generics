import ftplib
import re
import directories as DIR
from datetime import datetime


def collect(COLL_PATH, ENCODING, FTP_HOST, FTP_USER, FTP_PSWD, FTP_PATH, GET_FILENAME, FILE_PATTERN='', DIR_PATTERN='', GET_DIR=False):
    DIR_LOGS = COLL_PATH + DIR.LOGS
    DIR_INPUT = COLL_PATH + DIR.INPUT
    # get current date and time for logging and file naming
    date_time_info = datetime.now()
    date_time = date_time_info.strftime('%m.%d.%y.%H.%M.%S')
    log_filename = 'collection.' + date_time + '.log'
    logfile = open(DIR_LOGS + log_filename, 'w', encoding=ENCODING)

    logfile.write('########################################\n')
    logfile.write('# Collection log\n')
    logfile.write('########################################\n\n')
    logfile.write('Start time: ' + str(date_time_info) + '\n\n')

    # get list of previously collected articles from checkfile.txt
    checkfile = open(COLL_PATH + 'checkfile.txt', 'r', encoding=ENCODING)
    check_list = set()
    for line in checkfile:
        check_list.add(line.strip())
    checkfile.close()

    # connect to ftp
    ftp = ftplib.FTP(FTP_HOST, timeout=300)
    ftp.login(FTP_USER, FTP_PSWD)

    logfile.write('########################################\n')
    logfile.write('# Contents from the publication ftp\n')
    logfile.write('########################################\n\n')

    downloaded_file = []
    for path in FTP_PATH:
        ftp.cwd(path)

        if GET_DIR:
            dir_list = []
            ftp.dir(dir_list.append)
            for dr in dir_list:
                dir_name = dr.split()[-1]
                if dir_name not in check_list:
                    if (DIR_PATTERN and re.match(rf'{DIR_PATTERN}', dir_name)) or not DIR_PATTERN:
                        try:
                            os.mkdir(DIR_INPUT + dir_name)
                            ftp.cwd(dir_name)
                            file_list = ftp.nlst()
                            for file in file_list:
                                if (FILE_PATTERN and re.match(rf'{FILE_PATTERN}', file)) or not FILE_PATTERN:
                                    with open(DIR_INPUT + dir_name + '/' + file, 'wb') as writer:
                                        ftp.retrbinary('RETR ' + file, writer.write)
                            downloaded_file.append(dir_name)
                            logfile.write('Downloading... ' + dir_name + '\n')
                            ftp.cwd('../')
                        except Exception as e:
                            logfile.write(str(e))                
        else:
            file_list = ftp.nlst()

            # Collection of data
            for file in file_list:
                file_name = GET_FILENAME(file)
                if file_name not in check_list:
                    if (FILE_PATTERN and re.match(rf'{FILE_PATTERN}', file_name)) or not FILE_PATTERN:
                        # Retrieves file from ftp to input directory
                        try:
                            ftp.retrbinary('RETR ' + file, open(DIR_INPUT + file_name, 'wb').write)
                            downloaded_file.append(file_name)
                            logfile.write('Downloading... ' + file + '\n')
                        # Error handling
                        except Exception as e:
                            logfile.write(str(e))
                

    logfile.write('\n########################################\n')
    logfile.write('# Input files downloaded\n')
    logfile.write('########################################\n\n')
    logfile.write('\n'.join(downloaded_file) + '\n\n')
    logfile.write('Total number of files: ' + str(len(downloaded_file)) + '\n\n')
    date_time_end = datetime.now()
    logfile.write('End time: ' + str(date_time_end) + '\n')
    logfile.close()

    if len(downloaded_file):
        # update checkfile
        checkfile = open(COLL_PATH + 'checkfile.txt', 'a', encoding='utf-8')
        checkfile.write('\n'.join(downloaded_file) + '\n')
        checkfile.close()
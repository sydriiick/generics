from collector import Collector
import directories as DIR
from zipfile import ZipFile
import paramiko
import re
import os


class SFTPCollector(Collector):

    def __init__(self, coll_path, encoding):
        self.sftp = None

        self.block_size = 262144
        self.time_out = 1000

        Collector.__init__(self, coll_path, encoding)

    def set_block_size(self, block_size):
        self.block_size = block_size

    def __del__(self):
        if self.sftp:
            self.sftp.close()

        Collector.__del__(self)

    def init_ftp(self, sftp_host, sftp_user, sftp_pswd):
        self.init_log()
        self.write_coll_log_header()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(sftp_host, username=sftp_user, password=sftp_pswd, timeout=self.time_out
        sftp = ssh.open_sftp()

    def end_collect(self, downloaded_files):
        self.write_coll_log_footer(downloaded_files)
        self.update_checkfile(downloaded_files)

    def download_dir(self, dir_name, file_pattern):
        DIR_INPUT = self.coll_path + DIR.INPUT

        try:
            os.mkdir(DIR_INPUT + dir_name)

            self.ftp.cwd(dir_name)

            file_list = self.ftp.nlst()
            for file in file_list:
                if file_pattern and re.match(rf'{file_pattern}', file):
                    with open(f'{DIR_INPUT}{dir_name}/{file}', 'wb') as writer:
                        self.ftp.retrbinary('RETR ' + file, writer.write, blocksize=self.block_size)

            self.log(f'Downloaded: {dir_name}\n')

            self.ftp.cwd('../')
        except Exception as e:
            self.log(str(e))

    def download_file(self, file, file_name):
        DIR_INPUT = self.coll_path + DIR.INPUT

        try:
            #with open(DIR_INPUT + file_name, 'wb') as writer:
                #self.ftp.retrbinary('RETR ' + file, writer.write, blocksize=self.block_size)
            sftp.get(file, DIR_INPUT + file_name)

            self.log(f'Downloaded: {file}\n')
        except Exception as e:
            self.log(str(e))

    def collect_files(self, sftp_paths, rename_file, file_pattern):
        downloaded_files = []

        for path in sftp_paths:
            self.sftp.chdir(path)

            file_list = self.sftp.listdir()
            for file in file_list:
                file_name = rename_file(file)
                if file_name not in self.check_list:
                    if file_pattern and re.match(rf'{file_pattern}', file_name):
                        self.download_file(file, file_name)
                        downloaded_files.append(file_name)

        self.end_collect(downloaded_files)

    def collect_dirs(self, sftp_paths, dir_pattern, file_pattern):
        downloaded_dirs = []

        for path in sftp_paths:
            self.ftp.chdir(path)

            dir_list = []
            self.ftp.dir(dir_list.append)

            for dr in dir_list:
                dir_name = dr.split()[-1]
                if dir_name not in self.check_list:
                    if dir_pattern and re.match(rf'{dir_pattern}', dir_name):
                        self.download_dir(dir_name, file_pattern)
                        downloaded_dirs.append(dir_name)

        self.end_collect(downloaded_dirs)

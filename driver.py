from logger import Logger
from zipfile import ZipFile
from datetime import datetime
import directories as DIR
import utilities as UTIL
import validator as VLD
import os


class Driver(Logger):

    def __init__(self, conv_path, coll_path):
        self.conv_path = conv_path
        self.coll_path = coll_path

        self.err_count = 0
        self.invalid_count = 0
        self.success_count = 0
        self.sent_count = 0

        self.green_count_map = {}

        self.init_mode()
        self.init_dirs()

        Logger.__init__(self, conv_path, 'conversion')

    def init_mode(self):
        self.prep_only = 0
        self.go_collect = 1
        self.go_convert = 1
        self.go_send = 1
        self.go_clean = 1

    def init_dirs(self):
        self.DIR_INPROGRESS = self.conv_path + DIR.INPROGRESS
        self.DIR_IMAGE = self.conv_path + DIR.IMAGE
        self.DIR_UNZIP = self.conv_path + DIR.UNZIP
        self.DIR_OUTPUT = self.conv_path + DIR.OUTPUT
        self.DIR_DONE = self.conv_path + DIR.DONE
        self.DIR_LOGS = self.conv_path + DIR.LOGS
        self.DIR_FAILED = self.conv_path + DIR.FAILED
        self.DIR_ERROR = self.conv_path + DIR.ERROR
        self.DIR_TEMP = self.conv_path + DIR.TEMP

    def set_mode(self, run_mode):
        if run_mode & 16:
            self.prep_only = 1
        if not run_mode & 8:
            self.go_collect = 0
        if not run_mode & 4:
            self.go_convert = 0
        if not run_mode & 2:
            self.go_send = 0
        if not run_mode & 1:
            self.go_clean = 0

    def handle_error_docs(self, combined_file, green_name, image_list, image_zip):
        self.log(f'{combined_file} <===> check error_{self.err_count}\n')

        UTIL.move_file(combined_file, self.DIR_TEMP)

        if image_list:
            UTIL.move_file(self.DIR_IMAGE + image_list, self.DIR_TEMP)

        if image_zip:
            UTIL.move_file(self.DIR_IMAGE + image_zip, self.DIR_TEMP)

        _, _, err_docs = next(os.walk(self.DIR_ERROR))

        for err_doc in err_docs:
            UTIL.move_file(self.DIR_ERROR + err_doc, self.DIR_TEMP)

        UTIL.move_file(self.DIR_OUTPUT + green_name, self.DIR_TEMP)

        UTIL.compress_files(self.DIR_FAILED + f'error_{self.err_count}.zip', self.DIR_TEMP)

        self.err_count += 1

    def handle_valid_docs(self, combined_basename, green_zip, green_name, mcode, image_zip):
        self.log(f'{combined_basename} <===> {green_zip}\n')

        with ZipFile(self.DIR_OUTPUT + green_zip, 'w') as zipper:
            zipper.write(self.DIR_OUTPUT + green_name, green_name)

        if image_zip:
            UTIL.unzip_file(self.DIR_IMAGE + image_zip, self.DIR_UNZIP)
            UTIL.rename_images(self.DIR_UNZIP, mcode)
            UTIL.append_to_zip(self.DIR_OUTPUT + green_zip, self.DIR_UNZIP)

        if self.go_clean:
            os.remove(self.DIR_OUTPUT + green_name)

        self.success_count += 1

    def handle_invalid_docs(self, combined_basename, combined_file, green_name, validation_result, image_list,
                            image_zip):
        self.log(f'{combined_basename} <===> {validation_result}, check invalid_{self.invalid_count}.zip\n')

        if image_list:
            UTIL.move_file(self.DIR_IMAGE + image_list, self.DIR_TEMP)

        if image_zip:
            UTIL.move_file(self.DIR_IMAGE + image_zip, self.DIR_TEMP)

        UTIL.move_file(self.DIR_OUTPUT + green_name, self.DIR_TEMP)
        UTIL.move_file(combined_file, self.DIR_TEMP)

        UTIL.compress_files(self.DIR_FAILED + f'invalid_{self.invalid_count}.zip', self.DIR_TEMP)

        self.invalid_count += 1

    def rename_green_zip(self, green_zip):
        if green_zip in self.green_count_map:
            gz_count = self.green_count_map[green_zip]
            gz_name, gz_ext = os.path.splitext(green_zip)
            self.green_count_map[green_zip] += 1
            return f'{gz_name}_{gz_count}{gz_ext}'
        else:
            self.green_count_map[green_zip] = 1
            return green_zip

    def init_convert(self, converter):
        self.init_log()
        _, _, combined_files = next(os.walk(self.DIR_INPROGRESS))

        combined_files.sort()

        green_name = None
        green_zip = None
        mcode = None

        try:
            for combined_file in combined_files:
                combined_basename = combined_file
                combined_file = self.DIR_INPROGRESS + combined_file

                image_list = combined_basename + '.imagelist'
                image_zip = combined_basename + '.images.zip'

                has_image_list = os.path.exists(self.DIR_IMAGE + image_list)
                has_image_zip = os.path.exists(self.DIR_IMAGE + image_zip)

                if not has_image_list or not has_image_zip:
                    image_list = ''
                    image_zip = ''

                green_name, green_zip, mcode, has_error = converter.convert(combined_file)

                green_zip = self.rename_green_zip(green_zip)

                if has_error:
                    self.handle_error_docs(combined_file, green_name, image_list, image_zip)
                else:
                    validator = VLD.Validator(self.DIR_OUTPUT + green_name)
                    validation_result = validator.validate()
                    if validation_result == '':
                        self.handle_valid_docs(combined_basename, green_zip, green_name, mcode, image_zip)
                    else:
                        self.handle_invalid_docs(combined_basename, combined_file, green_name, validation_result,
                                                 image_list, image_zip)

        except Exception as e:
            self.log(str(e) + '\n')

    def init_send(self, sender):
        try:
            self.sent_count = sender.send()
        except Exception as e:
            self.log(str(e) + '\n')

    def clean(self):
        current_time = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')

        UTIL.compress_files(f'{self.DIR_DONE}combined_files_{current_time}.zip', self.DIR_INPROGRESS)
        UTIL.compress_files(f'{self.DIR_DONE}green_zips_{current_time}.zip', self.DIR_OUTPUT)
        UTIL.compress_files(f'{self.DIR_DONE}images_{current_time}.zip', self.DIR_IMAGE)

    def log_summary(self):
        self.log('\nSummary:\n\n')
        self.log(f'Success - {str(self.success_count)}\n')
        self.log(f'Error - {str(self.err_count)}\n')
        self.log(f'Invalid - {str(self.invalid_count)}\n')
        self.log(f'Sent - {str(self.sent_count)}\n\n')

    def run(self, collector, converter, sender):
        if self.go_collect:
            collector.collect(self.conv_path, self.prep_only)

        if self.go_convert:
            self.init_convert(converter)

        if self.go_send:
            self.init_send(sender)

        if self.go_clean:
            self.clean()

        self.log_summary()
        
        # self.email()

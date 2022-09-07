import shutil
import os
import directories as DIR
from zipfile import ZipFile


def move_file(src, dest):
    shutil.copy(src, dest)
    os.remove(src)


def move_files(src, dest):
    _, _, files = next(os.walk(src))
    for file in files:
        move_file(src + file, dest)


def copy_files(src, dest):
    _, _, files = next(os.walk(src))
    for file in files:
        shutil.copy(src + file, dest)


def move_dir(dir_name, src, dest):
    if not os.path.exists(dest + dir_name):
        os.mkdir(dest + dir_name)

    move_files(f'{src}{dir_name}/', f'{dest}{dir_name}/')

    shutil.rmtree(src + dir_name)


def rename_images(src, mcode):
    _, _, images = next(os.walk(src))
    for image in images:
        image_name, image_ext = os.path.splitext(image)
        newname = mcode + '_' + image_name + '-p' + image_ext
        os.rename(src + image, src + newname)


def compress_files(zipname, src):
    if os.path.isdir(src) and os.listdir(src):
        with ZipFile(zipname, 'w') as zipper:
            _, _, tobezips = next(os.walk(src))
            for tbzip in tobezips:
                zipper.write(src + tbzip, tbzip)
                os.remove(src + tbzip)


def compress_files_no_removal(zipname, src):
    if os.path.isdir(src) and os.listdir(src):
        with ZipFile(zipname, 'w') as zipper:
            _, _, tobezips = next(os.walk(src))
            for tbzip in tobezips:
                zipper.write(src + tbzip, tbzip)


def append_to_zip(zipname, src):
    with ZipFile(zipname, 'a') as zipper:
        _, _, tobezips = next(os.walk(src))
        for tbzip in tobezips:
            zipper.write(src + tbzip, tbzip)
            os.remove(src + tbzip)


def unzip_file(filename, dest):
    with ZipFile(filename) as unzipper:
        for zip_info in unzipper.infolist():
            if zip_info.filename[-1] == '/':
                continue
            unzipper.extract(zip_info, dest)
            if not os.path.exists(dest + os.path.basename(zip_info.filename)):
                shutil.move(dest + zip_info.filename, dest)

    _, udirs, _ = next(os.walk(dest))
    for udir in udirs:
        shutil.rmtree(dest + udir)


def clear_directory(dir_name):
    if os.path.isdir(dir_name):
        _, drs, files = next(os.walk(dir_name))

        for file in files:
            os.remove(dir_name + file)

        for dr in drs:
            shutil.rmtree(dir_name + dr)


def has_cjk_chars(content):
    for char in content:
        dec_code = ord(char)
        if dec_code >= 19968 and dec_code <= 40959:
            return True

    return False

import os
import directories as DIR


def get_size(dir):
    total_size = 0
    num_files = 0
    for _, _, files in os.walk(dir):
        for file in files:
            if file:
                file_path = os.path.join(dir, file)
                if not os.path.islink(file_path):
                    num_files += 1
                    temp_total_size = os.path.getsize(file_path)
                    total_size += temp_total_size/(1024*1024)

    return total_size, num_files


def remove_old(dir):
    file_list = []
    _, _, filenames = next(os.walk(dir))
    for filename in filenames:
        cfile = dir + filename
        file_list.append(cfile)

    file_list.sort(key=os.path.getctime)
    os.remove(file_list[0])


def optimize(dir, size_limit = 100, file_limit = ''):
    dir_size, num_files = get_size(dir)
    if file_limit:
        while dir_size > size_limit or num_files > file_limit:
            remove_old(dir)
            dir_size, num_files = get_size(dir)

    else:
        while dir_size > size_limit:
            remove_old(dir)
            dir_size, num_files = get_size(dir)


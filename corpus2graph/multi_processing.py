__author__ = 'Zheng ZHANG'

from multiprocessing import Pool
import os
import time
import random


def long_time_task_for_worker_test(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)

    # Calculate Pi
    from sys import stdout
    scale = 10000
    maxarr = 2800
    arrinit = 2000
    carry = 0
    arr = [arrinit] * (maxarr + 1)
    for i in range(maxarr, 1, -14):
        total = 0
        for j in range(i, 0, -1):
            total = (total * j) + (scale * arr[j])
            arr[j] = total % ((j * 2) - 1)
            total /= ((j * 2) - 1)
        stdout.write("%04d" % (carry + (total / scale)))
        carry = total % scale

    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))


def master(files_getter, data_folder, file_extension, worker, process_num=4):
    """
    Each processor takes one file at one time.
    """
    print('Master process %s.' % os.getpid())
    files = files_getter(data_folder, file_extension)
    file_num = len(files)
    if file_num == 0:
        print('[ERROR] No valid files in the data folder.')
        exit()
    if file_num < process_num:
        print('#files less than #processors, change process_num to', str(file_num))
        process_num = file_num

    with Pool(process_num) as p:
        results = p.starmap(worker, zip(files))
        p.close()
        p.join()
        print('All sub-processes done.')
        return results


def get_files_endswith(data_folder, file_extension):
    files = [os.path.join(data_folder, name) for name in os.listdir(data_folder)
             if (os.path.isfile(os.path.join(data_folder, name))
                 and name.endswith(file_extension))]
    return files


def get_files_startswith(data_folder, starting):
    files = [os.path.join(data_folder, name) for name in os.listdir(data_folder)
             if (os.path.isfile(os.path.join(data_folder, name))
                 and name.startswith(starting))]
    return files


def get_files_paths_not_contain(data_folder, not_contain):
    files = [os.path.join(data_folder, name) for name in os.listdir(data_folder)
             if (os.path.isfile(os.path.join(data_folder, name)) and (not_contain not in name)
                 and (not name.startswith('.')))]
    return files


def get_files_endswith_in_all_subfolders(data_folder, file_extension):
    subfolders = [os.path.join(data_folder, name) for name in os.listdir(data_folder) if
                  os.path.isdir(os.path.join(data_folder, name))]
    files = []
    for subfolder in subfolders:
        files += get_files_endswith(subfolder, file_extension)
    return files


def get_pid():
    return os.getpid()


def get_file_name(path):
    from os.path import basename
    return basename(path).split(".")[0]


def get_file_folder(path):
    from os.path import dirname
    return dirname(path)


def worker_test(file):
    print('Processing file %s (%s)...' % (file, os.getpid()))

# TESTS
# master("/Users/zzcoolj/Code/bucc2017/zh-en", ".en", worker_test)
# print(get_file_name("/Users/zzcoolj/Code/GoW/data/xin_eng/xin_eng_200410.xml"))

def chunkify(lst, n):
    """
    e.g.
    lst = range(13) & n = 3
    return = [[0, 3, 6, 9, 12], [1, 4, 7, 10], [2, 5, 8, 11]]
    """
    return [lst[i::n] for i in range(n)]

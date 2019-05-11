import argparse
from glob import glob
import os


def save(storage_dir):
    storage_dir = os.path.abspath(storage_dir)

    # 获取所有 .ts 文件路径
    files = ["file '" + f + "'\n" for f in glob(storage_dir + "/*.ts", recursive=True)]
    files = sorted(files)

    list_path = storage_dir + '/list.txt'
    with open(list_path, 'w+') as file:
        file.writelines(files)


def parse_args():
    """
    :rtype: dict
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('storage_dir', help="Path to save files")
    kwargs = vars(parser.parse_args())
    return kwargs


def has_file(dir: str) -> bool:
    dir = os.path.abspath(dir)
    files = glob(dir + "/*.ts", recursive=True)
    return len(files) > 0


if __name__ == '__main__':
    save(storage_dir='./test')

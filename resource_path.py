import sys, os


def path(relative_path):
    """
    生成资源文件目录访问路径
    :param relative_path:
    :return:
    """
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

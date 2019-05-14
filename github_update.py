import multiprocessing
from sys import platform
from tkinter import messagebox, filedialog
from diskcache import Cache

import requests

github_release_url = 'https://api.github.com/repos/gzlock/mrplayer_mainland_live_server/releases/latest'

last_version_key = 'latest_version'
file_key = 'latest_version_file'
file_downloaded_key = 'latest_version_file_downloaded'


def get_github_version(cache):
    try:
        print('检测github release')
        res = requests.get(github_release_url, timeout=2)

    except Exception as e:
        print('错误', e)


_cache: Cache = None
_latest_version = 0


class UpdateSoftware:
    __state__ = ''

    def __init__(self, root, cache, current_version: float, menu):
        super().__init__()
        self.root = root
        global _cache
        _cache = cache
        self.current_version = current_version
        self.latest_version = _cache.get(last_version_key, default=0)
        if self.latest_version == 0:
            self.latest_version = current_version

        # root.after_idle(self.get_github_version)
        self.get_github_version()

    def get_github_version(self):
        try:
            print('检测github release')
            res = requests.get(github_release_url, timeout=5)
            if res.status_code == 200:
                res = res.json()
                self.compare_version(res)
        except:
            pass

    def compare_version(self, res: dict = None):
        """
        对比版本号
        :param res:
        :return:
        """
        latest_version = float(res['tag_name'])

        downloaded = _cache.get(file_downloaded_key, default=False)

        print(
            {'github version': latest_version, 'cache version': self.latest_version, 'downloaded': downloaded})
        # 比缓存里的新版本号要新
        if latest_version > self.latest_version:
            print('步骤 1')
            # 更新 缓存 版本号
            _cache.set(last_version_key, latest_version)
            # 下载到缓存
            self.download_file(res)

        # 缓存比现存的要新
        elif self.latest_version > self.current_version and _cache.get(file_downloaded_key,
                                                                       default=False) is True:
            # 已经下载，提示保存
            if downloaded:
                print('步骤 2')
                UpdateSoftware.download_success()
            else:
                print('步骤 3')
                self.download_file(res)

        # 版本号相同，清空缓存
        else:
            print('步骤 4')
            _cache.set(file_downloaded_key, 1, 0)
            _cache.set(file_key, 1, 0)
            _cache.expire()

    def download_file(self, res: dict):
        if platform == 'win32':
            find = 'win.zip'
        else:
            find = 'macOS.zip'
        url: str = None
        for item in res['assets']:
            if item['name'] == find:
                url = item['browser_download_url']
                break

        if url is None:
            return

        pool = multiprocessing.Pool(1)
        pool.apply_async(func=UpdateSoftware.download_thread, args=(url,),
                         callback=UpdateSoftware.download_success)

    @staticmethod
    def download_thread(url):
        print('下载', url)
        # return

        res = requests.get(url)
        if res.status_code == 200:
            _cache.set(file_key, res.content)
            _cache.set(file_downloaded_key, True)
            print('下载完成')

    @staticmethod
    def save_file():
        pass

    @staticmethod
    def download_success(*args):
        yes = messagebox.askyesno('下载完成', '已经下载新版本，是否保存到硬盘？')
        if not yes:
            return
        latest_version = _cache.get(last_version_key)
        file = filedialog.asksaveasfilename(title='保存到', filetypes=[("Zip", ".zip")],
                                            defaultextension='zip', initialfile='玩很大 v' + str(latest_version))
        if len(file) > 0:
            with open(file, 'wb') as file:
                file.write(_cache.get(file))

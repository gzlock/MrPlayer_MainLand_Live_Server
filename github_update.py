import multiprocessing
from sys import platform
from tkinter import messagebox, filedialog

import requests
from diskcache import Cache

import mul_process_package

mul_process_package.ok()

github_release_url = 'https://api.github.com/repos/gzlock/mrplayer_mainland_live_server/releases/latest'

latest_version_key = 'latest_version'
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

    def __init__(self, root, cache, current_version: float):
        super().__init__()
        self.root = root
        global _cache
        _cache = cache
        self.current_version = current_version
        self.asked = False
        self.latest_version = _cache.get(latest_version_key, default=0)
        if self.latest_version == 0:
            self.latest_version = current_version

        # root.after_idle(self.get_github_version)
        self.get_github_version()
        self.loop_check()

    def loop_check(self):
        try:
            # 还没有保存
            if not self.asked and _cache.get(file_downloaded_key, default=False):
                self.download_success()
        except:
            pass
        finally:
            if not self.asked:
                self.root.after(2000, self.loop_check)

    def get_github_version(self):
        try:
            print('检测github release')
            res = requests.get(github_release_url, timeout=5)
            if res.status_code == 200:
                res = res.json()
                self.compare_version(res)
        except:
            pass

    def has_new_version(self, github_version) -> bool:
        return github_version > self.latest_version or self.latest_version > self.current_version

    def compare_version(self, res: dict = None):
        """
        对比版本号
        :param res:
        :return:
        """
        latest_version = float(res['tag_name'])

        downloaded = _cache.get(file_downloaded_key, default=False)

        print(
            {'current version': self.current_version,
             'cache version': self.latest_version,
             'github version': latest_version,
             'downloaded': downloaded})

        # 比缓存里的新版本号要新
        if latest_version > self.latest_version:
            # 更新 缓存 版本号
            _cache.set(latest_version_key, latest_version)
            # 清空缓存
            _cache.set(file_downloaded_key, False, 0)
            _cache.set(file_key, 1, 0)
            downloaded = False
            _cache.expire()

        if self.has_new_version(latest_version):
            print('有新版本')
            if not downloaded:
                print('有新版本，需要下载新版')
                self.download_file(res)
        else:
            print('版本号相同，清空缓存')
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

        print('platform', platform, find, url)

        multiprocessing.Process(target=UpdateSoftware.download_thread, args=(url, _cache)).start()

    @staticmethod
    def download_thread(url, _cache):
        print('下载', url)
        if url is None:
            return
        # return

        res = requests.get(url)
        if res.status_code == 200:
            _cache.set(file_key, res.content)
            _cache.set(file_downloaded_key, True)
            print('下载完成')

    def download_success(self, *args):
        self.asked = True
        yes = messagebox.askyesno('新版本下载完成', '是否保存到硬盘？')

        if not yes:
            return
        latest_version = _cache.get(latest_version_key)
        file = filedialog.asksaveasfilename(title='保存到', filetypes=[("Zip", ".zip")],
                                            defaultextension='zip', initialfile='玩很大 v' + str(latest_version))
        if len(file) > 0:
            with open(file, 'wb') as file:
                file.write(_cache.get(file))

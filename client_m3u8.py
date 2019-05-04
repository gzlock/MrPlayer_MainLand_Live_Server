import argparse
import multiprocessing
import os
import re
import shutil
import signal
import time
from urllib import parse

import requests
from fake_useragent import UserAgent

import str_md5

regex = r"vod\/(.*)\/master\.m3u8"

storage_dir = ""
ts_list = {}
i = 0

GoOn = True

proxies = {}


def shutdown(signalnum, frame):
    print('exit')
    global GoOn
    GoOn = False


def main(dir: str, url, clear):
    # for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM, signal.SIGKILL]:
    signal.signal(signal.SIGINT, shutdown)

    global storage_dir
    storage_dir = os.path.abspath(dir)

    queue = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    print('clear', clear)
    # 开发环境删除文件夹
    if clear:
        shutil.rmtree(storage_dir)

    # 创建要保存的文件夹
    if not os.path.exists(storage_dir):
        os.mkdir(storage_dir)

    ts_url_folder = '/'.join(url.split('/')[:-1])

    # 不断循环
    while GoOn:
        m3u8_content = requests.get(url, proxies=proxies).text
        if "#EXTM3U" not in m3u8_content:
            print("内容不符合M3U8的格式")
        file_line = m3u8_content.split("\n")
        for index, line in enumerate(file_line):
            if "EXTINF" in line:  # 找ts地址并下载
                ts_url = ts_url_folder + '/' + file_line[index + 1]  # 下一行就是ts网址
                ts_file_name = get_ts_file_name(ts_url)
                md5 = str_md5.to_md5(ts_file_name)
                if md5 not in ts_list:
                    ts_list[md5] = (ts_file_name, False)
                    queue.apply_async(download_ts_file, (ts_file_name, ts_url, md5, storage_dir))

        save_hls_m3u8_list_file()
        time.sleep(5)

    queue.close()
    queue.join()


def download_ts_file(ts_name, ts_url, md5, save_dir):
    print('开始下载', ts_url)
    try:
        res = requests.get(ts_url, proxies=proxies, timeout=20)
        if res.status_code != 200:
            raise Exception('404')
        content = res.content
        save_dir = os.path.normpath(save_dir + '/' + ts_name)
        # print('保存ts路径', save_dir)
        with open(save_dir, 'wb') as file:
            file.write(content)
        print('保存成功', save_dir)
        ts_list[md5] = (ts_name, True)
    except Exception as ex:
        print('TS文件下载失败', ts_name)


def get_m3u8_url():
    try:
        url = "https://api.4gtv.tv/Channel/GetChannelUrl"
        ua = UserAgent()
        payload = "fnCHANNEL_ID=4&fsASSET_ID=4gtv-4gtv040&fsDEVICE_TYPE=pc&clsIDENTITY_VALIDATE_ARUS%5BfsVALUE%5D=123"
        headers = {
            "User-Agent": ua.random,
            'cache-control': "no-cache",
            'content-type': "application/x-www-form-urlencoded",
            "Pragma": "no-cache",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        }
        response = requests.request("POST", url, data=payload, headers=headers, proxies=proxies,
                                    timeout=5)
        if response.status_code is not 200 or 'flstURLs' not in response.text:
            print('获取Key错误，需要台湾IP')

        url = response.json()['flstURLs'][0]
        matches = re.search(regex, url)
        key = matches.group(1)
        response = requests.get(url, proxies=proxies, timeout=5)
        file_line = response.text.split('\n')
        url = 'http://p-sirona-yond-4gtv.svc.litv.tv/hi/vod/{}/{}'.format(key, file_line[7])
        print('网址', url)
        return url

    except Exception as ex:
        print('M3u8Key 错误', ex)


def save_hls_m3u8_list_file():
    keys = list(ts_list.keys())

    keys = keys[-15:-5]
    sequence = ''
    try:
        name, state = ts_list[keys[0]]
        matches = re.search(r'(\d+)\.ts', name)
        sequence = matches.group(1)
        # print('sequence', sequence)
    except Exception as ex:
        pass
    path = os.path.normpath(storage_dir + '/live.m3u8')
    # print('m3u8地址', path)
    with open(path, mode='w+') as file:
        file.writelines([
            '#EXTM3U\n',
            '#EXT-X-VERSION:3\n',
            '#EXT-X-MEDIA-SEQUENCE:{}\n'.format(sequence),
            '#EXT-X-TARGETDURATION:5\n'
        ])
        for key in keys:
            name, download_success = ts_list[key]
            file.write('#EXTINF:4.004, no desc\n' + name + '\n')


def get_ts_file_name(ts_url):
    return parse.urlparse(ts_url).path.split('/')[-1]


def parse_args():
    """
    :rtype: dict
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help="Path to save files")
    parser.add_argument('-c', '--clear', help="Is clear the save folder?", action="store_true")
    kwargs = vars(parser.parse_args())
    return kwargs


def run(dir: str, video_url: str, proxy: str):
    global proxies
    if len(proxy) == 0:
        proxies = {}
    else:
        proxies = proxies = {
            'http': proxy,
            'https': proxy,
        }

    main(dir=dir, url=video_url, clear=False)


if __name__ == '__main__':
    main(**parse_args())

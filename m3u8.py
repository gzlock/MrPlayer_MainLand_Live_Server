import multiprocessing
import os
import re
import time

import requests

import mul_process_package
import utils

mul_process_package.ok()

storage_dir = ""
ts_list = {}
i = 0

GoOn = True

# 例子
proxies = {
    'http': 'http://127.0.0.1:1087',
    'https': 'http://127.0.0.1:1087',
}


def main(dir: str, video_url: str, cache):
    global storage_dir
    storage_dir = os.path.abspath(dir)

    queue = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    # 创建要保存的文件夹
    if not os.path.exists(storage_dir):
        os.mkdir(storage_dir)

    get_m3u8_url_last_time = 0

    url = video_url
    if video_url == '1':
        print('使用四季TV源')
        url = None

    # 不断循环
    while not cache.get('m3u8_stop', default=False):
        if video_url == '1':
            if time.time() - get_m3u8_url_last_time > 60:
                temp_url = get_hinet_m3u8_url(proxies=proxies)
                if temp_url is not None:
                    url = temp_url
                    get_m3u8_url_last_time = time.time()
        if url is None:
            continue
        m3u8_content = requests.get(url, proxies=proxies).text

        if "#EXTM3U" in m3u8_content:
            file_line = m3u8_content.split("\n")
            has_new_ts_file = False
            for index, line in enumerate(file_line):
                if "EXTINF" in line:  # 找ts地址并下载
                    ts_url = file_line[index + 1]  # 下一行就是ts网址，有可能只是相对网址，所以需要处理
                    ts_file_name = get_ts_file_name(ts_url)
                    md5 = utils.to_md5(ts_file_name)
                    if md5 not in ts_list:
                        has_new_ts_file = True
                        ts_list[md5] = (ts_file_name, False)
                        queue.apply_async(download_ts_file,
                                          (storage_dir, url, ts_file_name, ts_url, md5, proxies, cache))

            if has_new_ts_file:
                save_hls_m3u8_list_file()

        time.sleep(1)
    print('已经停止m3u8爬虫')


def download_ts_file(video_dir, url: str, ts_name: str, ts_url: str, md5: str, proxies, cache):
    if '://' in ts_url:
        url = ts_url
    else:
        url = '/'.join(url.split('/')[:-1]) + '/' + ts_url
    success = False

    while success is False and not cache.get('m3u8_stop', default=False):
        print('TS开始下载', ts_name)
        video_dir = os.path.join(video_dir, ts_name)
        try:
            content = requests.get(url, proxies=proxies, timeout=20).content
            with open(video_dir, 'wb') as file:
                file.write(content)
                success = True
            print('TS保存成功', ts_name)
            ts_list[md5] = (ts_name, True)
        except Exception as ex:
            print('TS下载失败', ts_name)
            pass


# 1080P
def get_4gtv_m3u8_url(proxies: dict):
    try:
        url = "https://api2.4gtv.tv/Channel/GetChannelUrl"
        payload = "fnCHANNEL_ID=4&fsASSET_ID=4gtv-4gtv040&fsDEVICE_TYPE=pc&clsIDENTITY_VALIDATE_ARUS%5BfsVALUE%5D=123"
        headers = {
            'user-agent': '',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'Pragma': 'no-cache',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        }
        res = requests.request("POST", url, data=payload, headers=headers, proxies=proxies,
                               timeout=5)
        if res.status_code is not 200 or 'flstURLs' not in res.text:
            print('获取Key错误，需要台湾IP')

        # 带https://的完整网址
        url = res.json()['Data']['flstURLs'][1]
        return url.replace('index.m3u8', 'stream3.m3u8')

    except Exception as ex:
        print('M3u8Key 错误', ex)


# hinet的源
def get_hinet_m3u8_url(proxies: dict):
    try:
        url = "https://api2.4gtv.tv/Channel/GetChannelUrl"
        payload = "fnCHANNEL_ID=4&fsASSET_ID=4gtv-4gtv040&fsDEVICE_TYPE=pc&clsIDENTITY_VALIDATE_ARUS%5BfsVALUE%5D=123"
        headers = {
            'user-agent': '',
            'cache-control': "no-cache",
            'content-type': "application/x-www-form-urlencoded",
            "Pragma": "no-cache",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        }
        res = requests.request("POST", url, data=payload, headers=headers, proxies=proxies,
                               timeout=5)
        if res.status_code is not 200 or 'flstURLs' not in res.text:
            print('获取Key错误，需要台湾IP')

        # 带https://的完整网址
        url = res.json()['Data']['flstURLs'][0]
        res = requests.get(url, proxies=proxies, timeout=5)
        file_line = res.text.split('\n')
        url = '/'.join(url.split('/')[:-1]) + '/' + file_line[7]
        # print('网址', url)
        return url

    except Exception as ex:
        print('M3u8Key 错误', ex)


def save_hls_m3u8_list_file():
    """
    保存 数组中最后10个ts文件名 到 m3u8文件
    :return:
    """
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

    with open(storage_dir + '/live.m3u8', mode='w+') as file:
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
    return ts_url.split('/')[-1].split('?')[0].split('#')[0]


def run(dir: str, video_url: str, proxy: str, cache):
    global proxies
    if len(proxy) == 0:
        proxies = {}
    else:
        proxies = {
            'http': proxy,
            'https': proxy,
        }
    main(dir=dir, video_url=video_url, cache=cache)

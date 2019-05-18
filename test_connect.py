import requests


def test_connect(video_url: str, proxy: str) -> str:
    """
    测试连接到视频源
    :param video_url:
    :param proxy:
    :return: 'ok'||'NeedTWIP'||'NotM3u8'||'ProxyError'||'ConnectError'
    """
    proxies = {}
    if len(proxy) > 0:
        proxies = {'http': proxy, 'https': proxy}
    headers = {
        'content-type': "application/x-www-form-urlencoded",
    }
    try:
        if video_url == '1':
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
            # print('测试', res.status_code, res.text)
            if res.status_code is not 200 or 'flstURLs' not in res.text:
                return 'NeedTWIP'
            print(res.json()['Data']['flstURLs'][0])

            return 'ok'
        else:
            res = requests.get(video_url, proxies=proxies, headers=headers, timeout=5)
            if res.status_code is not 200 or '#EXTM3U' not in res.text:
                return 'NotM3u8'
            return 'ok'

    except Exception as e:
        message = e.__str__()
        print(message)
        if 'ProxyError' in message:
            return 'ProxyError'
        elif 'Read timed out' in message:
            return 'TimeOut'
        return 'ConnectError'

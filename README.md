# 新版本，使用Aria2下载视频碎片+丢弃了直播功能
[https://github.com/gzlock/py_gui_hls_aria2](https://github.com/gzlock/py_gui_hls_aria2)

## 此软件已经不再使用

## 玩很大转播计划 配套程序


![计划图片](./计划.png)

本程序为计划中的"参与者电脑"服务

玩很大首播时间：每周六晚22点

开发语言:Python 3.7+

#### 不编译直接运行：
执行 **运行.bat** 即可

#### 自行编译为Windows系统的exe程序：
需要修改main.spec中的路径目录为在您电脑里的当前目录

```
if platform == 'win32':
    path = 'E:\\'
```

执行 **编译.bat** 后在dist文件夹可以看到main.exe程序

#### 注意与说明
网络源默认选择的第二项是本人用家庭网络提供的服务，每周六夜晚21点55分左右会开启，直播视频内容是台湾电视首播的玩很大，目前用自购的科学上网才能收看台湾电视直播。

这项个人服务随时有可能会因为 **个人因素** 中断服务，敬请原谅。

如果本人停止服务后，大家可以前往[四季TV](https://4gtv.tv)寻找台湾中视的网络直播源，需要 **台湾IP** 才能收看网络直播。

#### 弹幕功能服务
同样是用家庭网络提供的服务，网页弹幕播放器使用的是开源项目：[DPlayer](https://github.com/DIYgod/DPlayer)

不集成到exe转播程序里是因为想聚合更多弹幕，让直播观看的氛围更好。

对应的代码在[server.py](./server.py)

启动命令：
```cmd
python3 server.py
```


#### 本项目为MIT协议

本项目因为个人兴趣而无偿发起，不接受任何资金捐助/赞助，有人拿了源代码去寻求任何资金支持与本人无关。

禁止用于任何商业用途。

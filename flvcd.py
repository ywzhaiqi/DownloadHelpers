# -*- coding: utf-8 -*- Python3
import sys
import re
import os
import json
from pyquery import PyQuery

from common import addToIDM

SAVE_PATH = 'e:\\Downloads\\_tmp'
TO_JOIN_PATH = 'youku_to_join.json'


def parseFlvcd(url, format='hight'):
    # 不知道是否需要 urllib.parse.quote(videourl)
    print('目标：{}，清晰度：{}'.format(url, format))
    url = "http://www.flvcd.com/parse.php?kw=" + url + '&format=' + format
    d = PyQuery(url)

    filename = d('input[name="filename"]').attr('value')
    filename = re.sub('[\\\|\:\*\"\?\<\>]', "_", filename)

    urltxt = d('input[name="inf"]').attr('value')
    url = urltxt.strip()
    addToIDM(url, SAVE_PATH, filename)
    # for url in urltxt.split('\r\n'):
    #     url = url.strip()
    #     if url:
    #         addToIDM(url)


class Flvcd():
    encoding = 'gbk'

    def __init__(self):
        self.url = ""
        # 只找链接 self.pattern = re.compile(r"<a href *= *\"(http://f\.youku\.com/player/getFlvPath/[^\"]+)")
        self.rContent = re.compile('<input\s+type="hidden"\s+name="inf"\s+value="([^"]+)')
        self.rNameAndUrl = re.compile('<[NU]>(.+)')
        #从在下载url中取得后缀名
        #e.g. http://f.youku.com/player/getFlvPath/sid/00_00/st/mp4/fileid/030008040050D9D8F35EBA0359955B550E4FE0-A3D0-5DC5-C140-BFCFE663892F?K=2d47c2f50d44936424114172
        self.rFileExt = re.compile('st/(\w+)/fileid/')
        self.headers = {"Accept": "*/*", "Accept-Language": "zh-CN",
                        "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)",
                        "Connection": "Keep-Alive"}

    def fetchHtml(self, url):
        req = urllib.request.Request(url, headers=self.headers)
        f = urllib.request.urlopen(req)
        return f.read().decode(self.encoding)

    def parse(self, url, format='high'):
        """ return [(url, name)...] """
        # 不知道是否需要 urllib.parse.quote(videourl)
        self.url = "http://www.flvcd.com/parse.php?kw=" + url + '&format=' + format
        html = self.fetchHtml(self.url)

        # 先找出一大块区域
        m = self.rContent.search(html)
        content = m.group(1)
        # 进一步找出所有的name、url
        result = self.rNameAndUrl.findall(content)

        size = len(result)
        print('视频共有 {:d}个片段, 保存的位置: {}'.format(int(size / 2), SAVE_PATH))
        outList = []
        if size > 0:
            for i in range(0, size, 2):
                name = result[i]  # 没有后缀 e.g. 「ZEALER 出品」 华为荣耀四核 测评-0001
                url = result[i + 1]
                # 取得后缀名
                fileExt = self.rFileExt.search(url).group(1)
                name += '.' + fileExt

                outList.append((url, name))
            return outList
        else:
            print("URL Not Found")


def addAllToIDM(allList):
    print('-' * 40)
    for url, name in allList:
        addToIDM(url, SAVE_PATH, name)
        print('添加到IDM成功：{}'.format(name))

    print("全部添加到IDM，请开始用IDM下载")


def saveData(allList):
    #先取出存在的列表
    try:
        with open(TO_JOIN_PATH) as f:
            videos = json.load(f)
    except:
        videos = []

    #当片段数量>=2才需要
    if len(allList) >= 2:
        #取得当前所有的片段列表
        filePaths = []
        for url, name in allList:
            path = os.path.join(SAVE_PATH, name)
            filePaths.append(path)

        #添加到videos
        videos.append(filePaths)

        #重写记录文件
        with open(TO_JOIN_PATH, "w") as f:
            json.dump(videos, f, indent=4, ensure_ascii=False)
            print('-' * 40)
            print("要合并的列表保存到 %s" % TO_JOIN_PATH)


def comman_line_runner():
    argc = len(sys.argv)
    if argc == 2:
        format = 'high'
    elif argc == 3:
        format = sys.argv[2]
    else:
        #对于优酷视频来说, super超清, high高清, normal标清
        print("Usage: %s videoUrl [videoQuality=normal|high|super|normal|...]" % sys.argv[0])
        print(" e.g.")
        print("   %s http://v.youku.com/v_show/id_XMzMzMjE0MjE2.html super" % sys.argv[0])
        return

    videoUrl = sys.argv[1]
    parseFlvcd(videoUrl, format)

if __name__ == '__main__':
    # main()
    comman_line_runner()

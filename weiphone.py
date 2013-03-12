# coding: gbk
import re
import os
import time
import argparse

from pyquery import PyQuery

from lib.common import addToIDM, PY3k

if PY3k:
    from urllib.parse import urlencode
else:
    from urllib import urlencode

SAVE_PATH = 'F:\\Downloads\\_tmp'
BASE_URL = 'http://bbs.weiphone.com/'
headers = {"Accept": "*/*", "Accept-Language": "zh-CN",
           "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)",
           "Connection": "Keep-Alive"}


def checkWefiler(d):
    """检查软件下载页面是否有威锋盘的链接
    """
    links = d('a[href*="www.wefiler.com/#download"]').items()
    urls = []
    for a in links:
        url = a.attr['href']
        url.replace('http://http//', 'http//')
        urls.append(url)
    return urls


def download(threadUrl):
    """
    """
    d = PyQuery(url=threadUrl, parser='soup')
    links = d('a[href^="job.php?action=download&aid="]')

    # 获取 verify 的值
    tmp = d('script:contains("var verifyhash =")').text()
    verify = re.search(r"var verifyhash = '(.*?)'", tmp).group(1)

    total = len(links)
    d.make_links_absolute()
    for i, e in enumerate(links.items(), start=1):
        filename = e.text()
        print('%s/%s %s' % (i, total, filename))

        if not os.path.exists(os.path.join(SAVE_PATH, filename)):
            params = urlencode(
                {'check': 1, 'verify': verify, 'nowtime': int(time.time() * 1000)})
            url = '%s?%s' % (e.attr['href'], params)

            print('  fetch: ' + url)
            downDoc = PyQuery(url, headers=headers)
            # 第0个是电信下载点，第1个是移动下载点
            downUrl = BASE_URL + downDoc('a[href^="remotedown.php"]').eq(1).attr('href')
            addToIDM(downUrl, SAVE_PATH, filename)
            time.sleep(1.5)

    wefiler_urls = checkWefiler(d)
    if wefiler_urls:
        print(wefiler_urls)


def main():
    # urlstrs = '''
    #     http://bbs.weiphone.com/read-htm-tid-1726790.html
    # '''

    parser = argparse.ArgumentParser(description='weiphone iPad 电子书资源 批量下载')
    parser.add_argument('urls', metavar='URL', nargs='+', help='该论坛的一个帖子地址')

    args = parser.parse_args()
    if args.urls:
        # urls = re.findall(r'http://[^\s]+', urlstrs)
        for url in args.urls:
            print(url)
            download(url)

if __name__ == '__main__':
    main()

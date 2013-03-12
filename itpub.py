
import re
import sys
import argparse
from urllib.parse import urlparse, parse_qs
from pyquery import PyQuery as pq

from lib.common import addToIDM

DOWN_PATH = 'e:\\Downloads\\itpub'
reFileExt = re.compile('[(pdf)|(rar)|(doc)|(excel)|(chm)|(zip)|(7z)|\
    (swf)|(torrent)|(txt)|(sql)|(docx)|(xls)|(xlsx)|(ppt)|(pptx)]')

BASE_URL = 'http://www.itpub.net/'
# db = pymongo.MongoClient().myDownload


def _addToDownload(url, fileName=None):
    """ url 是附件的下载链接
    """
    url = url.replace('attachment.php?', 'forum.php?mod=attachment&').replace('&amp;', '&')

    addToIDM(url)
    # fileName = trimFileName(fileName)
    # addToIDM(url, DOWN_PATH, fileName)
    print('  添加到IDM: %s' % fileName)


def _getThreadId(threadUrl):
    # http://www.itpub.net/forum.php?mod=viewthread&tid=1596873&extra=page%3D1%26filter%3Dtypeid%26typeid%3D385%26typeid%3D385&page=2
    # http://www.itpub.net/thread-1761255-1-1.html
    o = urlparse(threadUrl)
    if 'mod=viewthread&tid=' in o.query:
        querys = parse_qs(o.query)
        threadId = querys.get('tid')[0]
        # pageNum = querys.get('page')
        # pageNum = pageNum if pageNum else 1  #如果没有默认第一页
    elif '/thread-' in o.path:
        pathList = o.path.split('-')
        threadId = pathList[1]
        # pageNum = pathList[2]
    else:
        print('Error: getThreadId from url error, ' + threadUrl)
    return int(threadId)


def _parseForum(forumUrl, downed=False):
    """ 解析一个分页的 thread
    """
    d = pq(forumUrl)
    threads = []
    items = d('img[title="附件"]').siblings('a.xst').items()
    for item in items:
        url = BASE_URL + item.attr('href')
        name = item.text()
        threadId = _getThreadId(url)

        thread = {'_id': threadId, 'name': name, 'url': url, 'downed': downed}
        threads.append(thread)

    print('得到 %d 个thread' % len(threads))
    return threads


# def setOneBookDowned(threadUrl, threadId=None):
#     if not threadId:
#         threadId = _getThreadId(threadUrl)
#     db.itpub.update({'_id': threadId}, {'$set': {'downed': True}}, upset=True)
#     print('已设置为已下载')


# def parseAllThreads(start=1, end=7):
#     """ 精华书籍的列表
#     http://www.itpub.net/forum.php?mod=forumdisplay&fid=61&filter=typeid&typeid=385&page=1
#     """
#     print('开始解析所有精华列表')
#     for i in range(start, end + 1):
#         threadUrl = 'http://www.itpub.net/forum.php?mod=forumdisplay&fid=61&filter=typeid&typeid=385&page=%s' % i
#         print('fetch: page %s...' % i)
#         threads = _parseForum(threadUrl)
#         for t in threads:
#             db.itpub.update({'_id': t['_id']}, {'downed': True})


def _createNextPageUrl(url):
    # 如果 url = http://www.itpub.net/thread-1608864-2-1.html 这是第二页
    if '/forum.php?mod=viewthread' in url:
        if '&page=' in url:
            bUrl, pageNum = url.split('&page=')
            pageNum = int(pageNum)
        else:
            bUrl = url
            pageNum = 1
        nextUrl = '%s&page=%d' % (bUrl, (pageNum + 1))
    # 或 http://www.itpub.net/forum.php?mod=viewthread&tid=512296&page=2
    elif '/thread-' in url:
        m = re.match(r'(.*)-(\d)-(\d\.html)', url)
        nextNum = int(m.group(2)) + 1
        nextUrl = '%s-%d-%s' % (m.group(1), nextNum, m.group(3))
    else:
        print('生成下一页网址错误: ' + url)
        return

    return nextUrl


cacheNames = []


def parseAndDownOneBook(url):
    print('  开始解析: ' + url)
    d = pq(url)
    find = d('ignore_js_op a[href^="attachment.php?aid="]')

    if not find:
        return

    for e in find.items():
        downUrl = BASE_URL + e.attr('href')
        name = e.text()
        #防止不断重复
        if name in cacheNames:
            return
        _addToDownload(downUrl, name)
        cacheNames.append(name)

    if '.part' in name:
        #进入下一页
        nextUrl = _createNextPageUrl(url)
        parseAndDownOneBook(nextUrl)


def downDigestBooks(limit=10):
    """ 下载精华书籍 """
    books = db.itpub.find({'$or': [{'downed': {'$exists': False}}, {'downed': False}]}).limit(limit)
    for book in books:
        parseAndDownOneBook(book['url'])
        setOneBookDowned(book['url'])


def main_old():
    parser = argparse.ArgumentParser(description='itpub下载')
    parser.add_argument('-d', dest='threadUrl', help='论坛中一个帖子的地址')
    parser.add_argument('-txt', dest='txtPath', help='文本文件的路径')
    parser.add_argument('-all', dest='downNum', help='继续下载n个精华帖子')
    parser.add_argument('-df', dest='attachmentUrl', help='附件下载地址')

    args = parser.parse_args(sys.argv[1:])
    if args.threadUrl:
        #下载单个链接
        if args.threadUrl.startswith('http://www.itpub.net'):
            parseAndDownOneBook(args.threadUrl)
        else:
            print('您输入的url不正确')

    if args.txtPath:
        #下载批量链接
        with open('itpub.txt') as f:
            fileLines = f.readlines()

        for line in fileLines:
            url = line.strip()
            parseAndDownOneBook(url)
            print('')

    if args.attachmentUrl:
        urls = re.findall(r'http://.*', s)
        for url in urls:
            _addToDownload(url)

    if args.downNum:
        downDigestBooks(int(args.downNum))


def command_line_runner():
    inputStr = sys.argv[1]
    if inputStr.startswith('http://www.itpub.net'):
        if 'thread' in inputStr:
            dofunc = parseAndDownOneBook
        elif 'attachment.php?aid=' in inputStr:
            dofunc = _addToDownload
    elif '.txt' in inputStr:
        with open('itpub.txt') as f:
            inputStr = f.read()
        dofunc = parseAndDownOneBook
    else:
        input('不支持此url，按回车键退出')
        sys.exit(1)

    urls = re.findall(r'http://.*', inputStr)
    for i, url in enumerate(urls, start=1):
        print('%s/%s %s' % (i, len(urls), url))
        dofunc(url)

if __name__ == '__main__':
    command_line_runner()

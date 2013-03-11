
import re
import os
import fnmatch
import sqlite3

from lib.common import *

''' 从 http://blog.sina.com.cn/lmiou 获取开卷三分钟、财经郎眼、锵锵三人行视频地址'''

FILE_PATH = 'ifengVideo.lst'
DB_PATH = 'ifengVideo.db'


def getAllPages(start=1, end=38):
    """ 得到所有page的下载地址
    """
    downUrls = []
    for i in range(start, end + 1):
        url = 'http://blog.sina.com.cn/s/article_sort_1490886071_10001_%s.html' % i
        print('正在获取第%s页...' % i)
        urls = getOnePage(url)
        size = len(urls)
        if size < 10:
            print("    只得到%d条下载链接" % size)
            print("    " + url)
        downUrls.extend(urls)

    print("共获取到%d条下载链接" % len(downUrls))
    with open(FILE_PATH, 'w+') as f:
        urls_str = '\n'.join(downUrls)
        f.write(urls_str)
        print("写入 %s 成功" % FILE_PATH)


def getOnePage(url):
    """ 得到一个page页面的地址
    """
    # f = urllib.request.urlopen(url)
    # content = f.read().decode('utf-8')
    content = getHtml(url, 'utf-8')

    urls = re.findall(r'ed2k://.*?/', content, re.S)
    urls = [url.strip().replace('<wbr>', '').replace('\n', '') for url in urls]
    return urls


def getAllItems():
    """ 从下载地址中分解出
    e.g. [('开卷八分钟', '2012-12-19', '《弯曲的脊梁》（一）.mkv', downUrl)...]
    """
    rName = re.compile(r'''
        (\w+)                # e.g. 开卷八分钟,文化大观园
        -[-\s]?              # 分隔符 -后面可能有空格或-
        (\d{4}-\d{2}-\d{2})  # 日期 e.g. 2012-12-18
        -?                   # 分隔符
        (.*)                 # 文件名 e.g. 王立军的“火化论”颇具文化修养.mkv
        ''', re.VERBOSE)
    with open(FILE_PATH) as f:
        items = []
        for line in f:
            name = r1(r'ed2k://\|file\|(.*?)\|', line)
            name = re.sub(r'-?新时空家园录制|-?【华夏视讯网首发】|-?3e帝国录制', '', name)

            m = rName.match(name)
            if m:
                url = line.strip()
                t = (url, m.group(1), m.group(2), m.group(3))
                items.append(t)
            else:
                print('not match: %s' % name)
        return items


def writeAllItems(items):
    """ 写入到数据库
    """
    if len(items) == 0:
        print("items size is 0")
        return

    con = sqlite3.connect(DB_PATH)
    con.execute('DROP TABLE items')
    con.execute('CREATE TABLE IF NOT EXISTS items (url VARCHAR(255) UNIQUE, type TEXT, date TEXT, name TEXT)')

    cur = con.cursor()
    for item in items:
        # item e.g. url, type, date, name
        cur.execute('INSERT INTO items VALUES(?,?,?,?)', item)

    con.commit()
    cur.close()
    con.close()


def getDBItems():
    con = sqlite3.connect(DB_PATH)
    cur = con.execute("SELECT date, url FROM items WHERE type='开卷八分钟'")
    dbItems = [(date, url) for date, url in cur]
    cur.close()
    return dbItems


def getLocalDates():
    file_dates = []
    for file in os.listdir('e:\\Downloads\\视频\\开卷八分钟'):
        if fnmatch.fnmatch(file, '*.mkv') or fnmatch.fnmatch(file, '*.rmvb'):
            file_date = r1(r'(\d{4}-\d{2}-\d{2})', file)
            file_dates.append(file_date)
    return file_dates


def getUnDownUrls():
    dbItems = getDBItems()
    all_file_dates = [date for date, url in dbItems]

    local_file_dates = getLocalDates()

    print("数据库中没有的而本地有的:")
    # for date in local_file_dates:  #常规用法
    #     if date not in all_file_dates:
    #         print("    " + date)
    for date in filter(lambda x: x not in all_file_dates, local_file_dates):  # 另一种用法
        print("    " + date)

    #set(all_file_dates) ^ set(local_file_dates)

    # un_down_urls = []
    # for date, url in dbItems:
    #     if date not in local_file_dates:
    #         un_down_urls.append(url)
    un_down_urls = list(filter(lambda x: x[0] not in local_file_dates, dbItems))
    print("还有 %s个未下载" % len(un_down_urls))

    return un_down_urls


def updateAllSize():
    conn = sqlite3.connect(DB_PATH)

    c = conn.execute('SELECT rowid, url FROM items')
    for rowid, url in c:
        #ed2k://|file|<文件名>|<文件大小>|<文件Hash>|/
        size = url.split('|')[3]
        conn.execute('UPDATE items SET size=? WHERE rowid=?', (size, rowid))

    conn.commit()
    c.close()


def getSize():
    total_size = 0
    # 下载列表\开卷八分钟_下载列表.lst     3.7GB
    # 下载列表\锵锵三人行_文化大观园.lst  28.5GB
    with open('下载列表\锵锵三人行_文化大观园.lst') as f:
        for line in f:
            if line.startswith('ed2k'):
                size = line.split('|')[3]
                total_size += int(size)

    size_str = strSize(total_size)
    print(size_str)


def test():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT url FROM items WHERE type != "开卷八分钟"')
    with open('锵锵三人行_文化大观园.lst', 'w') as f:
        for url, in c:
            f.write(url + '\n')

    c.close()

if __name__ == '__main__':
    # un_down_urls = getUnDownUrls()

    # with open('下载列表/开卷八分钟_下载列表.lst', 'w') as f:
    #     f.write('\n'.join(un_down_urls))
    getSize()
    pass

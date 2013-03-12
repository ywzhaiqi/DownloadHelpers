# coding: gbk
# python2
# 统计未下载的Ken777制作的书籍
import re
import sys
import datetime
import sqlite3


class Book:
    def __init__(self, date, name, author):
        self.date = date
        self.name = name
        self.author = author
        self.downloaded = False


def get_all_books():

    with open('Ken777制作书籍汇总.TXT') as f:
        text = f.read()

    pattern = re.compile(r'([\d\.]+)《(.*)》(\S+)')
    books = []
    for m in pattern.finditer(text):
        sDate, name, author = m.groups()
        date = datetime.datetime.strptime(sDate, '%Y.%m.%d')
        books.append(Book(date, name, author))

    return books
    # 按日期排序
    # books = sorted(books, key=lambda book: book.date)
    # for book in result:
    #     print(book.date, book.name)


def download_from_weiphone():
    # ken777授权.版面精确还原PDF电子书系列发布帖
    startURL = 'http://bbs.weiphone.com/read-htm-tid-847578.html'

    sys.path.insert(0, "..")
    import weiphone
    weiphone.download(startURL)


def get_download_names():
    with open('downloaded.txt') as f:
        text = f.read()

    downloadeds = re.findall(r'《(.*)》', text)
    return downloadeds


def check_downed_exist(downed_names, all_names):
    """ 检验下载的book是否存在all_books中 """
    for name in downed_names:
        if name not in all_names:
            print("不存在：", name)

if __name__ == '__main__':
    # con = sqlite3.connect(':memory:')
    # cur = con.cursor()
    # cur.execute('create table books (name, author, date, downloaded)')

    # for book in get_all_books():
    #     cur.execute('insert into books({}, {}, {}, false)'.format(
    #         book.name, book.author, book.date.strftime('%Y-%m-%d')))
    #     all_book_names.append(book.name)
    # con.commit()

    all_book_names = []
    all_books = get_all_books()
    for book in all_books:
        all_book_names.append(book.name)

    # 下载过的
    downed_book_names = get_download_names()
    check_downed_exist(downed_book_names, all_book_names)
    print('共有 {} 本书籍，已下载 {} 本'.format(len(all_book_names), len(downed_book_names)))

    for book in all_books:
        if book.name in downed_book_names:
            book.downloaded = True

    print('未下载的书籍列表:')
    for i, book in enumerate(filter(lambda book: book.downloaded == False, all_books)):
        i += 1
        print('  %s %s' % (i, book.name))
    # con.close()

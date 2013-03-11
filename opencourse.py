
import os
import argparse
from pyquery import PyQuery

from common import addToIDM

BASE_PATH = 'e:\\Downloads\\_tmp'


def download(url):
    d = PyQuery(url)

    title = d('.m-cdes h2').text()
    # title = trimFileName(title)   # 整个公开课的标题
    # info = d('.m-cdes p:first').text()   # 本课程共4集 翻译完 欢迎学习

    path = os.path.join(BASE_PATH, title)
    print('保存的位置：' + path)

    # 有2个列表
    for e in d('#list2 .u-ctitle').items():
        ctitle = e.text()  # 一节课的标题
        downUrl = e.siblings('.u-cdown .downbtn').attr('href')
        #没翻译的为None
        if downUrl:
            filename = ctitle + '.mp4'
            addToIDM(downUrl, path, filename)   # retcode=0


def get_parser():
    parser = argparse.ArgumentParser(description='help download 163 OpenCourse')
    parser.add_argument('url', metavar='URL', nargs='?', help='the course url')
    return parser


def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())
    if 'url' in args:
        download(args['url'])


if __name__ == '__main__':
    command_line_runner()

# -*- coding=utf-8 -*-
import re
import argparse
from pyquery import PyQuery


def parse_other_page(url):
    """ 从其它网站获取链接 """
    print('正在从 gdajie.com 获取链接')
    url = url.replace('www.verycd.com', 'www.verycd.gdajie.com')
    d = PyQuery(url)
    emuleFile = d('#emuleFile a[href^="ed2k://"]')
    if emuleFile:
        items = [(e.attr('href'), e.text()) for e in emuleFile.items()]
        return items
    else:
        #http://verycdfetch.duapp.com/topics/132012/
        print('都没有链接')
        pass


def parse_verycd_topic(url):
    assert url.startswith('http://www.verycd.com/topics/'), url
    print('正在从 verycd 获取链接...')
    d = PyQuery(url)
    if d('#iptcomED2K div:contains("无法提供下载")'):
        print('  verycd 没有链接')
        # parse_other_page(url)
    else:
        for e in d('#iptcomED2K a[ed2k^="ed2k://"]').items():
            link = e.attr('ed2k')
            name = e.text()
            yield link, name
    # links = iptcomED2K.find('a[ed2k]').map(lambda i, e: PyQuery(e).attr('ed2k'))
    # return links

# def extend_link(url):
#     links = verycd_links(url)
#     from lixian_hash_ed2k import parse_ed2k_file
#     return [{'url':x, 'name':parse_ed2k_file(x)} for x in links]


def test():
    url_text = '''http://www.verycd.com/topics/2944233/
http://www.verycd.com/topics/2943310/
http://www.verycd.com/topics/2943294/
'''

    urls = re.findall(r'(http://.*)', url_text)
    for url in urls:
        for link, name in parse_other_page(url):
            print(link)


def command_line_runner():
    parser = argparse.ArgumentParser('批量解析verycd下载链接')
    parser.add_argument('url_text', metavar='URL_TEXT', nargs='?', help='链接或链接文本')

    args = parser.parse_args()
    if args.url_text:
        urls = re.findall(r'(http://.*)', args.url_text)
        pass


if __name__ == '__main__':
    # command_line_runner()
    test()

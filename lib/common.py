# coding: utf-8
import re
import sys
import subprocess

from config import IDM_PATH

PY3k = sys.version_info >= (3,)
SUFFIXES = ['Byte', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']

if PY3k:
    from urllib.parse import unquote
else:
    from urllib import unquote


def addToIDM(url, path=None, name=None):
    command = [IDM_PATH, '/d', url]
    if path:
        command.extend(['/p', path])
    if name:
        command.extend(['/f', name.encode('gbk')])
    command.append('/a')
    retcode = subprocess.call(command)
    if name:
        print(u'添加到IDM: ' + name)
    else:
        print(u'添加到IDM: ' + url)
    return retcode


def str_size(size, unit='Byte'):
    """將文件大小转换为合适的单位表示."""
    if size < 1024:
        return '%.2f %s' % (size, unit)

    return str_size(size / 1024.0, SUFFIXES[SUFFIXES.index(unit) + 1])


def unquote_url(x):
    if type(x) != str:
        return x
    if PY3k:
        try:
            return unquote(x, 'utf-8')
        except UnicodeDecodeError:
            return unquote(x, 'gbk')  # can't decode in utf-8 and gbk
    else:
        x = unquote(x)
        try:
            return x.decode('utf-8')
        except UnicodeDecodeError:
            return x.decode('gbk')


def parse_ed2k_link(link):
    ed2k_re = r'ed2k://\|file\|([^|]*)\|(\d+)\|([a-fA-F0-9]{32})\|'
    m = re.match(ed2k_re, link) or re.match(ed2k_re, unquote(link))
    if not m:
        raise Exception('not an acceptable ed2k link: ' + link)
    name, file_size, hash_hex = m.groups()
    return unquote_url(name), hash_hex.lower(), int(file_size)


def parse_ed2k_id(link):
    return parse_ed2k_link(link)[1:]


def parse_ed2k_file(link):
    return parse_ed2k_link(link)[0]

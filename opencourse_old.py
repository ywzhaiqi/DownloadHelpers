import sqlite3
import urllib.parse
import json
import cmd
from fnmatch import fnmatch

from pyquery import PyQuery

from common import *

import io  # 防止 print 出错
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

BASE_PATH = 'e:\\公开课'

def downCourse(url):
    d = PyQuery(url=url)

    title = d('.m-cdes h2').text()
    title = trimFileName(title)  # 整个公开课的标题
    info = d('.m-cdes p:first').text()  # 本课程共4集 翻译完 欢迎学习

    path = os.path.join(BASE_PATH, title)
    print('保存的位置：' + path)

    for e in d('.u-ctitle').items():
        ctitle = e.text()  # 一节课的标题
        downUrl = e.siblings('.u-cdown .downbtn').attr('href')
        #没翻译的为None
        if downUrl:
            filename = ctitle + '.mp4'  #
            retcode = addToIDM(downUrl, path, filename)  # retcode=0
            print('  添加到IDM：' + filename)

class WebParser:
    def _parseCategory(self):
        """  解析 http://open.163.com/ocw/ 国际公开课的分类列表
        Returns
            [{"category": "文学", "name": "牛津大学《犯罪小说》", "info": "共3集 翻译完", 'url':'..'}]
        """
        # 国际名校公开课

        startUrl = 'http://open.163.com/ocw/'
        courses = []
        html = getHtml(startUrl)
        soup = BeautifulSoup(html)
        for csoup in soup.find_all('div', 'm-conmt'):
            category = csoup.find('h3', 'f-fs1').get_text()  # e.g. 文学、艺术、哲学....

            for oItem in csoup.find_all('div', 'cnt'):
                name = oItem.h5.string  # e.g. 伟谷《亚伯拉罕·林肯两百周年纪念》
                url = oItem.h5.a['href']  # e.g. http://v.163.com/special/opencourse/abrahamlincoln.html
                info = oItem.h6.string  # e.g. 共3集 翻译完

                courses.append({
                    'category': category, 'name': name, 'url': url, 'info': info
                    })

        return courses

    def _parseCourse(self, url):
        """ 解析一个公开课

        Return
            introduction 介绍
            items 多个子条目，是个字典
        """
        html = getHtml(url, 'gbk')
        if not html:
            print('get url fail: ' + url)
            return
        soup = BeautifulSoup(html)
        # 介绍
        info_soup = soup.find('div', 'm-cdes')
        if info_soup:
            info = info_soup.get_text()
            introduction = info.replace(' \n\n\n 分享 \n\n\n\n\n\n\n /分享 \n收藏\n\n\n', '')
        else:
            introduction = ''
        # 子条目
        items = []
        for tr_soup in soup.select('#list2 tr[class*="u-"]'):
            item = {}
            #name
            n_soup = tr_soup.find('td', 'u-ctitle')
            name = n_soup.get_text().strip()
            name = re.sub(r'\s+', ' ', name)
            name = re.sub(r':|/', '.', name)
            item['name'] = name
            #原始链接
            release_url = n_soup.find('a')['href']
            item['release_url'] = release_url
            #下载链接
            u_soup = tr_soup.find('a', 'downbtn')
            if u_soup:  # 翻译过的
                down_url = u_soup['href']
                translated = True
            else:  # 没翻译过的
                down_url = r1(r'(http.*mp4)', str(tr_soup))
                translated = False
            item['down_url'] = down_url
            item['translated'] = translated
            items.append(item)

        return introduction, items


class OpenCourse:
    """ course like
    {
        name: '', url: '', category: '文学', info: '共3集 翻译完', introduction: '',
        items: [{name:'', down_url:'', translated: True, is_downed: False, release_url: ''}]
    }
    """

    def __init__(self):
        conn = pymongo.MongoClient()
        self.db = conn.opencourse
        self.courses = self.db.courses  # 目录集合

    def getAndUpdateOne(self):
        """ 获取目录列表并插入到 MongoDB
        """
        for course in self.courses.find():
            if 'items' not in course:
                print(course['name'], course['url'])
                self._parseCourse(course)
                self.courses.update({'_id': course['_id']}, course)

    def find(self, name, printItems=True):
        name = name.replace('\\', '')
        findCourses = list(self.courses.find({'name': re.compile(name)}))
        size, i = len(findCourses), 0
        print('找到%d个公开课:' % size)
        for course in findCourses:
            items = course['items']
            #输出分类、名字、子条目数目、是否全部下载
            print('%3d %s/%s, 共%d个子条目:' % (i, course['category'], course['name'],len(items)))
            #2个一行输出子条目
            if printItems:
                for j in range(0, len(items), 2):
                    #当前这个
                    curName = items[j]['name']
                    # curDowned = '[未下载]' if items[j]['is_downed'] is False  else ''
                    #下一个
                    next = j+1
                    if next == len(items):
                        nextName = ''
                        nextDowned = ''
                    else:
                        nextName = items[j+1]['name']
                        # nextDowned = ' [未下载]' if items[j+1]['is_downed'] is False  else ''
                    #输出
                    print('        %s%s' % (curName.ljust(30), nextName ))
                    # print('        %s %s %s' % (curName, curDowned.ljust(30), nextName + nextDowned))
            i += 1

        return findCourses

    def _checkLocalPath(self, course):
        print('检查本地情况: %s' % course['name'])
        dirPath = os.path.join(BASE_PATH, course['category'], course['name'])
        unDowned = 0
        for item in course['items']:
            # 临时用，删除以前的，因为改了名字
            if 'is_downed' in item:
                del item['is_downed']
            if os.path.exists(os.path.join(dirPath, item['name'] + '.mp4')):
                item['downed'] = True
            else:
                item['downed'] = False
                unDowned += 1
        course['unDowned'] = unDowned
        return course

    def _updateLocalPath(self, course):
        self._checkLocalPath(course)

        self.courses.update({'_id': course['_id']}, {
            '$set': {'unDowned': course['unDowned'], 'items': course['items']},
            '$unset': {'all_downed': ''}
            })
        total = len(course['items'])
        downed = total - course['unDowned']
        # sUnDowned = ' [还有 %s个未下载，继续努力]' % unDowned if unDowned>0 else ' [恭喜你，已全部下载]'
        print('成功更新本地路径: {}，下载进度：{:.0%} {}/{}'.format(course['name'],
            int(downed/total), downed, total))

    def listCategory(self, category):
        for c in self.courses.find({'category': category}):
            pass

    def listUndownload(self, limit=10):
        # self.courses.find({'items': {'$elemMatch': 'is_downed': False}}, project)
        courses = self.courses.find({'items.is_downed': False}, {'name': 1}).limit(limit)
        for c in courses:
            print(c['name'])

    def findAndChoose(self, name, func):
        """ 查找并选择，然后执行更新或下载的函数
        """
        courses = self.find(name, printItems=False)
        if courses:
            if len(courses) == 1:
                func(courses[0])
            else:
                choose = int(input('请选择第几个: '))
                if 0 <= choose < len(courses):
                    func(courses[choose])
                else:
                    print('不在选择列表中')

    def downOne(self, name):
        """ 添加一个公开课到IDM
        name 文件夹名字，支持模糊搜索 e.g. 密歇根网络教育《平面设计》
        """
        findCourses = self.find(name)
        if findCourses:
            if len(findCourses) == 1:
                self._addToDown(findCourses[0])
            else:
                choose = int(input('请选择第几个: '))
                if 0 <= choose < len(findCourses):
                    self._addToDown(findCourses[choose])
                else:
                    print('不在选择列表中')


    def test(self):
        # for f in os.listdir():
        #     if fnmatch(f, '*.mp4'):
        for c in self.courses.find():
            self._updateLocalPath(c)
        # for c in self.courses.find():
        #     folder = c['name']
        #     for item in c['items']:

        pass

    def downAll(self):
        """ 要判断是否下载过
        """
        for course in self.courses.find():
            pass

    def _addToDown(self, course, start=0, num=100):
        """
        @args
            course  一个公开课 dict
            start   起始位置, 默认为0
            num     添加的数量, -1代表全部
        """
        if num < 1:
            print('添加的数目不能小于1！')
            return

        downPath = 'e:\\Downloads\\1\\公开课'
        dirpath = os.path.join(BASE_PATH, course['category'], course['name'])
        end = start + num
        for item in course['items'][start:end]:
            #跳过未翻译的
            if item['translated'] is True:
                url = item['down_url']
                name = trimFileName(item['name']) + '.mp4'
                addToIDM(url, dirpath, name)
                print('已添加到IDM: ' + name)

class OpenCourseCommand(cmd.Cmd):
    intro = '我的公开课管理下载程序'
    prompt = '(OpenCourse) '

    def do_exit(self, arg):
        sys.exit()

    def do_set(self, arg):
        self.A = arg
        print('已经设置A的值')

    def do_print(self, arg):
        print(self.A)

def main():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS,
        description='公开课搜索和下载')
    parser.add_argument('-f', '--find', dest="find_name", default='',
        help="模糊查找，如输入'音乐'，名字带有'音乐'的所有公开课都将被查找出来。语法：'-f 音乐'")
    parser.add_argument('-d', '--down', dest='down_name', default='',
        help="添加到IDM，如输入'耶鲁大学《聆听音乐》'，程序将添加'耶鲁大学《聆听音乐》'的全集。")
    parser.add_argument('-u', '--uplocalpath', dest='uplocal_name', default='', help="更新本地路径到数据库")
    parser.add_argument('-l', '--list', dest='list_cmd', default='', help='test')
    parser.add_argument('test', nargs='?', help='test')

    args = parser.parse_args(sys.argv[1:])
    course = OpenCourse()

    if args.find_name:
        course.find(args.find_name)
    if args.down_name:
        course.downOne(args.down_name)
    if args.uplocal_name:
        pass
        # course.findAndChoose(args.uplocal_name, course.updateLocalPath)
    if 'test' in args:
        course.test()
        # opencourse.listUndownload()
        #
        # opencourse.updateLocalPath()

if __name__ == '__main__':
    # main()
    downCourse('http://v.163.com/special/opencourse/arabic.html')

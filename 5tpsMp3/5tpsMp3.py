
import threading
import signal
import json
import queue

from lib.common import *

progress_file = '5tps.json'  # 保存进度的文件名
o5tps = {}  # 要解析的对象
cur_pos = 0


class Parser():
    BASE_URL = 'http://www.5tps.com'

    def __init__(self):
        # 每个子页面的下载链接、fileName的正则
        self.rDownUrl = re.compile(
            '<a href=\"(.*)\"><font color=\"blue\">点此下载.*</a>')
        self.rFileName = re.compile(r'[^/]+\.mp3')  # 从上面的DownUrl得到

    #得到 out_dict{'start_url':'', 'title':'', 'urls':[], 'content':'', 'total_size':10}
    def parseStartUrl(self, start_url):
        """
        parse out download page from start url.
        eg. we can get 'http://www.5tps.com/down/8297_52_1_1.html' from 'http://www.5tps.com/html/8297.html'
        """
        out_dict = {'start_url': start_url}
        html = getHtml(start_url, 'gbk')

        #标题
        titleLine = r1(r'<TITLE>([^<>]*)</TITLE>', html)
        title = titleLine.split(" ")[1]
        out_dict['title'] = title

        #子链接
        rUrl = re.compile(r'href=[\"\'](/down/.*?html)')
        itemUrls = rUrl.findall(html)
        #/down/8297_52_1_1.html --> http://www.5tps.com/down/8297_52_1_1.html
        out_dict['urls'] = [self.BASE_URL + url for url in itemUrls]

        #内容简介
        # xpath_contetn = './/*[@id='full']/div/div/ul/p/span' #内容简介
        content = re.search(r'<h4>.+?</p>', html, re.DOTALL).group()
        #去掉html标记
        out_dict['content'] = htmlToText(content)

        out_dict['total_size'] = len(out_dict['urls'])
        return out_dict

    # 找到真实的下载地址， return (downUrl, fileName)
    def getDownUrl(self, url):
        """ find out the real download link from download page.
        eg. we can get the download link 'http://180j-d.ysts8.com:8000/人物纪实/童年/001.mp3?
        1251746750178x1356330062x1251747362932-3492f04cf54428055a110a176297d95a' from
        'http://www.5tps.com/down/8297_52_1_1.html'
        """
        content = getHtml(url, 'gbk')
        downUrl = self.rDownUrl.search(content).group(1)
        #从url中提取出fileName
        fileName = self.rFileName.search(downUrl).group()
        fileName = fileName.replace('%20', ' ')

        return (downUrl, fileName)


class CheckThread(threading.Thread):
    """ 检查任务是否完成 """
    def __init__(self, check_list):
        threading.Thread.__init__(self)
        self.check_list = check_list

    def run(self):
        while True:
            for i, filePath in enumerate(self.check_list):
                if os.path.exists(filePath):
                    print('   下载完成: %s' % filePath)
                    del self.check_list[i]
            time.sleep(0.5)


def exitApp(signum, frame):
    #强行中断前保存解析进度
    o5tps['start_pos'] = cur_pos
    o5tps['down_size'] = o5tps['total_size'] - o5tps['start_pos']
    with open(progress_file, 'w') as f:
        json.dump(o5tps, f, sort_keys=True, indent=4)
    print('保存进度成功，自动退出！')
    sys.exit()


def getProgress():
    #检查是否有进度文件
    try:
        global o5tps
        f = open(progress_file)
        o5tps = json.load(f)
        f.close()

        print('''读取进度, 目标: {title}, {start_url}
              共有{total_size:d}个,本次开始:第{start_pos:d}个,还有{down_size:d}个'''
              .format(**o5tps))
        return True
    except:
        return False


def main():
    global o5tps, cur_pos
    save_path = 'e:\\Downloads\\有声小说'
    parser = Parser()

    print('开始运行')

    #没有进度则输入start_url
    hasProgress = getProgress()
    if not hasProgress:
        start_url = sys.argv[1]
        if not start_url:
            print('没有输入url')
            return
        o5tps = parser.parseStartUrl(start_url)
        o5tps['start_pos'] = 0
        print('{title} 共有{total_size:d}个'.format(**o5tps))

    #注册停止命令
    signal.signal(signal.SIGINT, exitApp)

    #取得一些值，看起来简单点
    check_list = []
    urls = o5tps['urls']
    cur_pos = o5tps['start_pos']
    dir_path = os.path.join(save_path, o5tps['title'])

    #启动检查是否下载完成进程
    t = CheckThread(check_list)
    t.daemon = True
    t.start()

    #写入说明.txt
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    content_path = os.path.join(dir_path, '说明.txt')
    if not os.path.exists(content_path):
        with open(content_path, 'w', encoding='gbk') as f:
            f.write(o5tps['content'])

    #动态取得下载链接并添加到IDM
    while cur_pos < len(urls):
        if len(check_list) < 3:
            downUrl = urls[cur_pos]

            cur_num = cur_pos + 1
            print('正在处理第{}个, {}'.format(cur_num, downUrl))
            mp3Url, fileName = parser.getDownUrl(downUrl)

            #本地不存在则添加
            filePath = os.path.join(dir_path, fileName)
            if not os.path.exists(filePath):
                addToIDM(mp3Url, dir_path)

            #添加到 check_list
            check_list.append(filePath)
            cur_pos += 1
        else:
            time.sleep(0.5)

    #全部完成删除进度文件
    if os.path.exists(progress_file):
        os.remove(progress_file)
    print('全部下载完成！')

if __name__ == '__main__':
    main()

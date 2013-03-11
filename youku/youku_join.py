
import sys
import os
import subprocess
import json

from youku_flvcd import TO_JOIN_PATH


def joinVideo(videoPaths):
    """ 合并一个视频
    """
    if len(videoPaths) == 0:
        print("videoPaths size=0")
        return

    allName = videoPaths[0].replace("-0001", "")  # 合并后的名称
    fileExt = os.path.splitext(videoPaths[0])[1]  # 后缀名

    if fileExt == '.mp4':
        command = ["D:\网络工具\硕鼠\mp4box.exe"]
        for videoPath in videoPaths:
            command.extend(["-cat", videoPath])
        command.extend(["-new", allName])
    elif fileExt == '.flv':
        command = ["D:\网络工具\硕鼠\FlvBind.exe"]
        command.append(allName)
        command.extend(videoPaths)
    else:
        print('格式不支持')
        return False

    returnCode = subprocess.call(command)
    if returnCode == 0:
        #移除片段文件
        for path in videoPaths:
            os.remove(path)
            print("删除文件: " + path)
        return True


def main():
    #取出记录列表
    try:
        with open(TO_JOIN_PATH) as f:
            videos = json.load(f)
    except:
        print("没有记录列表")
        return

    if not videos:
        return

    #一个个地检验下载完成没
    for videoPaths in videos:
        #只要有一个没下载好就不合并
        isFinish = True
        for path in videoPaths:
            if not os.path.exists(path):
                isFinish = False
                break

        if isFinish:
            success = joinVideo(videoPaths)
            if success:
                videos.remove(videoPaths)

    #如果还有videos则存入进度文件，否则删除进度文件
    if videos:
        with open(TO_JOIN_PATH, 'w') as f:
            json.dump(videos, f, indent=4, ensure_ascii=False)
    else:
        if os.path.exists(TO_JOIN_PATH):
            os.remove(TO_JOIN_PATH)


if __name__ == '__main__':
    main()

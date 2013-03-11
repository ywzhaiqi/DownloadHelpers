# 各个不同网站辅助下载脚本合集

这些脚本都是我平时用到不断收集的，以Python为主，还包含js脚本。本人水平有限，希望共同探讨。
**AutoHotkey 辅助合集**

## 需要

- python >= 3
- pyquery

## 分类

### verycd 下载

- [verycd.user.js](verycd/verycd@ywzhaiqi@gmailcom.user.js)：直接在verycd页面显示下载链接
- [verycd.py](verycd/verycd.py)：未完成。用上面的 GM 脚本替代。
- [simplecd.py](verycd/simplecd.py): 可用

### 迅雷离线下载

- [thunderlixianexporter](http://s.binux.me/TLE/master/ThunderLixianExporter)
- [thunderassistant](http://userscripts.org/scripts/show/111748)
    - 有时候有问题，一直在加载，点击没反应。由于jQuery库
- [离线Python脚本](https://github.com/iambus/xunlei-lixian)
    - 自己修改添加了导出IDM下载文件，没有试用

### itpub 论坛下载

解析并添加到IDM下载，我的超级用法：复制多个论坛链接，然后调用AHK脚本直接从剪贴板取网址执行脚本。

### weiphone 论坛批量下载

取得帖子的所有下载链接并添加到IDM，用的次数不多

### 5tps 有声小说下载

动态解析（限制为2个）并添加到ID

### 网易公开课 批量获取地址

获取整个公开课数据库存在mongodb，检索、添加下载

### 凤凰视频下载

包括财经郎眼、锵锵三人行、开卷八分钟。

TODO

- 从verycd下载

### 优酷视频下载

- 从flvcd网站获取下载链接并添加到IDM下载。
- 用IDM速度比自带下载工具略快，但由于未完美解决合并的问题，一直没用
- you-get 获取不能改清晰度
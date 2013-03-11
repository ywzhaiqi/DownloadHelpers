##最终获取链接
http://bbs.weiphone.com/job.php?action=download&aid=1741094&check=1&nowtime=1360316928664&verify=5c41a95d

##点击事件
    <a onclick="return ajaxurl(this,'&check=1');" href="job.php?action=download&aid=1741081"> 资治通鉴全译本.epub</a>

	function ajaxurl(o, ep) {
	    read.obj = o;
	    ajax.send(o.href + ((typeof ep == 'undefined' || !ep) ? '' : ep), '', ajax.get);
	    return false;
	}

##ajax.send
    var nowtime = new Date().getTime();
    if (nowtime - this.last < 1500) {
        clearTimeout(this.t);
        this.t = setTimeout(function(){ajax.send(url,data,callback)},1500+this.last-nowtime);
        return;
    }
    this.last = nowtime;
    url += (url.indexOf("?") >= 0) ? "&nowtime=" + nowtime : "?nowtime=" + nowtime;
    if (typeof verifyhash != 'undefined') {
        url += '&verify=' + verifyhash;
    }


##verifyhash
    var verifyhash = '5c41a95d';
    在 read-htm-tid-1726790.html 的18行
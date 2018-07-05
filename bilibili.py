import requests
import json
import random
import pymysql
import sys
import datetime
import time
from imp import reload
from multiprocessing.dummy import Pool as ThreadPool



# 数据库相关的资源
host = '192.168.153.88'
user = 'xiyuduo'
passwd = 'xyd911211'
db = 'bilibili'

# 生成时间
def gentime():
    return  int(round(time.time()))

reload(sys)

# 加载请求头
def LoadUserAgents(uafile):
    uas = []
    with open(uafile,'r') as fp:
        for ua in fp.readlines():
            if ua:
                uas.append(ua.strip('\n'))
    random.shuffle(uas)
    return  uas




# 所有的请求头信息
uas = LoadUserAgents('user_agents.txt')
head = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://space.bilibili.com/45388',
    'Origin': 'http://space.bilibili.com',
    'Host': 'space.bilibili.com',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}




# 爬取每一个用户的 信息
def profile(i):
    id = str(i)
    payload = {
        'mid':id,
        'csrf': '',
    }
    ua = random.choice(uas)
    head = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'Referer':'http://space.bilibili.com/45388',
    }
    #发送请求
    ajax_url = 'http://space.bilibili.com/ajax/member/GetInfo'
    print('****'*20)
    jsoncontent = requests.session().post(ajax_url,data=payload,headers=head).text
    jsDict = json.loads(jsoncontent)
    statusjson = jsDict['status'] if 'status' in jsDict.keys() else False
    if statusjson == True:
        if 'data' in jsDict.keys():
            jsData = jsDict['data']
            mid = jsData['mid']
            name = jsData['name']
            sex = jsData['sex']
            rank = jsData['rank']
            face = jsData['face']
            regtimestamp = jsData['regtime']
            regtime_local = time.localtime(regtimestamp)
            regtime = time.strftime("%Y-%m-%d %H:%M:%S", regtime_local)
            spacesta = jsData['spacesta']
            birthday = jsData['birthday'] if 'birthday' in jsData.keys() else 'nobirthday'
            sign = jsData['sign']
            level = jsData['level_info']['current_level']
            OfficialVerifyType = jsData['official_verify']['type']
            OfficialVerifyDesc = jsData['official_verify']['desc']
            vipType = jsData['vip']['vipType']
            vipStatus = jsData['vip']['vipStatus']
            toutu = jsData['toutu']
            toutuId = jsData['toutuId']
            coins = jsData['coins']
            #获得其他的相关的信息
            try:
                res = requests.get('https://api.bilibili.com/x/relation/stat?vmid=' + id + '&jsonp=jsonp').text
                viewinfo = requests.get(
                    'https://api.bilibili.com/x/space/upstat?mid=' + id + '&jsonp=jsonp').text
                js_fans_data = json.loads(res)
                js_viewdata = json.loads(viewinfo)
                following = js_fans_data['data']['follwing']
                fans = js_fans_data['data']['follower']
                archiveview = js_viewdata['data']['archive']['view']
                article = js_viewdata['data']['article']['view']
            except:
                following = 0
                fans = 0
                archiveview = 0
                article = 0
        else:
            print('no data now')
        #将数据存储到数据库中
        try:
            conn = pymysql.connect(
                host='localhost', user='root', passwd='123456', db='bilibili', charset='utf8')
            cur = conn.cursor()
            cur.execute('INSERT INTO bilibili_user_info(mid, name, sex, rank, face, regtime, spacesta,birthday, sign, level, OfficialVerifyType, OfficialVerifyDesc, vipType, vipStatus,toutu, toutuId, coins, following, fans ,archiveview, article) \
                                VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s", "%s","%s","%s","%s","%s","%s")'
                        %(mid, name, sex, rank, face, regtime, spacesta,birthday, sign, level, OfficialVerifyType, OfficialVerifyDesc, vipType, vipStatus,toutu, toutuId, coins, following, fans, archiveview, article))
            conn.commit()
        except Exception as e:
            print(e)

    else:
        print('Error:'+ajax_url)

# 线爬取一个网页的用户的信息
def main():
    #发送ajax时所需要的表单的数据
    for i in range(5):
        profile(i)




if __name__ =="__main__":
    main()
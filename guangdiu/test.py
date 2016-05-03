import requests
from bs4 import BeautifulSoup
import op_time
import chardet
import log
import db
from push import push_notification

def init(database_name, collection_Items, collection_Errors):
    log.open_log()
    col_items = db.get_collection(database_name, collection_Items)
    col_errors = db.get_collection(database_name, collection_Errors)

    return col_items, col_errors

def init_push(database_name, collection_Push):
    col_push = db.get_collection(database_name, collection_Push)
    return col_push

#获取所有的页面内容
'''
ignore True如果一页中所有的item均在db中，则不会继续获取后面的内容;False 继续获取
'''
def get_pages(cnt = 1, ignore = True, push = False):
    global col_Errors, col_Items
    global prefix_url
    global max_try

    last_page, coding = get_last_page()
    if int(last_page) == 0: #判断获取最后一页是否出错
        log.log_prn('Get', 'get_last_page error', 'ERROR')
        return

    log.log_prn('Get', 'Get last page num : %d' % int(last_page), 'NORMAL')

    temp_last_page = last_page

    circle_count = 1

    while cnt <= int(temp_last_page):
        log.log_prn("Get", "---------------------------------------", "NORMAL")
        log.log_prn("Get", "Getting page %d data ..." % cnt, "NORMAL")

        page_infos = get_single_page(cnt, coding)
        if page_infos == None:#因为数量不匹配，错误
            db.insert_one_doc(col_Errors, cnt)

        #插入db的item数量
        insert_count = 0

        #404 requests.get返回码错误
        #400 requests.get无响应
        if 404 == page_infos['return_code'] or 400 == page_infos['return_code']:
            log.log_prn('Get', 'get_page return_code %d, times %d, page_url %s' % (page_infos['return_code'], circle_count ,prefix_url + str(cnt)), 'ERROR')
            op_time.delay(2, 1)
            if circle_count < max_try:#设定抓取出错次数，超过则跳过，并存入db
                circle_count = circle_count + 1
                continue #这里直接进入下一次循环，但是页面并没有改变，下一次还是抓取此次页面
            else:
                circle_count = 1
                cnt = cnt + 1
                log.log_prn('Get', 'Fail to get the page %s' % prefix_url + str(cnt), 'ERROR')

                #！！！待存入error db,如何来定位？
                db.insert_one_doc(col_Errors, cnt)

        elif 200 == page_infos['return_code']:
            #！！！循环得到的数据，查看数据库中是否存在，如果存在则break
            insert_data = [] #插入数据库的item
            for item in page_infos["data"]:
                if db.find_one_doc(col_Items, item['id']) != 0:#数据库中存在
                    log.log_prn("Get", "Item %d already exist." % int(item['id']), "WARN")
                else:
                    insert_count = insert_count+1
                    db.insert_one_doc(col_Items, item)
                    insert_data.append(item) #记录插入数据库的数据
                    log.log_prn("Get", "Item %d insert in Collection Items" % int(item['id']), "NROMAL")

            if insert_count == 0 and True == ignore:#如果本页面中Item插入数据库的数量=0，则认为该页面以及其后面的页面都已经在数据库存在
                log.log_prn("Get", "ignore False.Page %d items have already inserted in db, aboart this scan" % cnt, "NORMAL")
                log.flush_log()
                break #后续循环退出

            if not push_notification(insert_data):
                log.log_prn("Get", "Push items failed. Page %d" % cnt, "ERROR")

            cnt = cnt + 1
            circle_count = 1

        log.log_prn("Get", "Insert %d items to Col_items" % insert_count, "NORMAL")
        log.flush_log()
        op_time.delay(3, 1)
    return None

'''
获取最后一页
返回值：
大于0 最后一页
等于0 出错
'''
def get_last_page(cnt = 1):
    count = 0
    while True:
        count = count + 1
        coding = None
        page_infos = get_single_page(cnt, coding)
        if 200 == page_infos['return_code']:
            return page_infos['data'][0]['last_page'], page_infos['coding']
        else:
            if count <= 3:
                op_time.delay(2, 1)
            elif count > 3:
                return 0, 0

'''
get_page 返回一个字典
字典结构：{'return_code':返回码,
           'data':[{页面中的商品信息字典},……]}
返回码：
    404：连接错误
    200：OK
'''
def get_single_page(cnt, coding = None):
    global host_url
    global prefix_url
    data = []
    try:
        wb_data = requests.get(prefix_url + str(cnt))
    except requests.exceptions.ConnectionError:
        log.log_prn("Get", "Page %d requests.get lost connection" % cnt, "ERROR")
        return {'return_code' : 400, 'data' : data}
    else:
        if 200 != wb_data.status_code: #排除错误情况
            #添加打印
            return {'return_code' : 404, 'data' : data}
        else:

            if coding == None:
                #此处很耗时，考虑不必每次检查
                #用charset库确定编码，再转换编码,结果形式为{'confidence': 0.99, 'encoding': 'utf-8'}
                coding = chardet.detect(wb_data.content)['encoding']

            wb_data.encoding = coding

            #解析网页
            soup = BeautifulSoup(wb_data.text, 'lxml', from_encoding = 'utf-8')

            #这里不考虑使用item数量来确定是否最后一页，页面上的商品是动态的
            #获取最后一页的页码

            #获取title和img集合:img并没有到url那一级，
            # 原因是小时风云榜的图片url都是一样的，内部删除会删除所有的，会出错，故出来后需要再找下一级
            titles, ids, part_links, imgs = get_titlesandimgs(soup)
            #获取时间
            timeandfroms = get_timeandfroms(soup)

            #获取最后一页的内容
            last_page = soup.find(attrs = {'class' : 'nextpagestatic'}).previous_sibling.get_text()

            #数量不匹配错误
            if not len(titles) == len(ids) == len(part_links) == len(imgs) == len(timeandfroms):
                log.log_prn("Get", "Data count doesn't match.Page %d : titles: %d ids: %d links: %d timeandfroms: %d imgs: %d " % \
                            (cnt, len(titles), len(ids), len(part_links), len(timeandfroms), len(imgs)), "ERROR")
                return None

            #封装返回的数据结构
            for title, id, part_link, timeandfrom, img  in zip(titles, ids, part_links, timeandfroms, imgs):
                d = {
                    'title' : title,
                    'id' : id,
                    'link' : host_url + part_link,
                    'cur_time' : op_time.get_utc(),
                    'get_time' : timeandfrom,
                    'img_url' : img,
                    'cur_page' : cnt,
                    'last_page' : last_page
                }
                data.append(d)
            return {'return_code' : 200, 'data' : data, 'coding' : coding}

#获取title、id、link（部分链接）、img内容
def get_titlesandimgs(soup):
    titles = []
    imgs = []
    ids = []
    part_links = []
    ##div.zkcontent > div.gooditem.withborder
    items = soup.select("div.zkcontent > div.gooditem.withborder")
    count = 1
    for item in items:
        #print(item.select("div.imgandbtn > div.showpic"))
        try:
            img_info = item.select("div.imgandbtn > div.showpic > a")[0]
            if img_info['href'].split("?")[0] != "go.php":
                tag_a = item.select("div.iteminfoarea > h2.mallandname > a.goodname")[0]
                titles.append(tag_a['title'])
                ids.append(tag_a['href'].split("=")[1])
                part_links.append(tag_a['href'])#不是完整的路径
                imgs.append(item.select("div.imgandbtn > div.showpic > a > img")[0]['src'])
        except AttributeError:#对象属性获取错误，解析错误
            log.log_prn("Get", "Encounter an AttributeError", "ERROR")
            continue
    return titles, ids, part_links, imgs


def get_timeandfroms(soup):
    timeandfroms = []
    times = soup.select('div.infotime > a')
    for time in times:
        if None != time['target']:
            timeandfroms.append(time.get_text())
        else:
            timeandfroms.append(time.a.get_text())
    return timeandfroms




max_try = 3
prefix_url = 'http://guangdiu.com/index.php?p='
host_url = 'http://guangdiu.com/'
count_per_page = 30
database_name = 'Guangdiu'
collection_Items = 'Items'
collection_Errors = 'Errors'
collection_push = 'Push'

if __name__ == '__main__':
    #初始化两个数据库，log文件的文件描述符
    col_Items, col_Errors = init(database_name, collection_Items, collection_Errors)
    #初始化推送数据库
    col_push = init_push(database_name, collection_push)
    if col_Items == None or col_Errors == None:
        log.log_prn('Get', 'Get Collections Failed','ERROR')
    else:
        log.log_prn('Get', 'Init end.', 'NORMAL')
        while True:
            get_pages(1)
            log.log_prn("Get", "Waiting for next scan...", "NORMAL")
            op_time.delay(60, 10)# 每60秒左右 获取一次

        log.close_log()

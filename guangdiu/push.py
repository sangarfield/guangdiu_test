import log
import multiprocessing

'''
解析插入db的数据，获得详情页的信息，解析后放入pipe，待推送进程筛选发送XXXXX
    不考虑新加推送进程，由于抓取要延时，不考虑性能，直接写一个筛选函数
    这个解析过程已经是新建进程了，速率不会影响主进程，但是主进程3s抓取一页，理论上说每3秒会新建一个进程处理抓取的
        数据，这样积累下来会生成很多进程很影响性能。还是在主进程中初始化时启动解析进程，把抓取的数据放入pipe，只
        有一个解析进程抓取具体页面了！
insert_data是一个list
其内部元素是字典
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
    将获取的数据插入col_push表
'''
def analysis_data(insert_data, col_push):
    #用pipe，duplex参数为false！
    recv_conn, send_conn = multiprocessing.Pipe(duplex = False)
    for data in insert_data:
        link = data['link']
    #初始化时启动进程，待写




'''
由于analysis_data函数中的原因，这个函数把抓取到的数据放入pipe，而不是新建进程处理
'''
def push_notification(insert_data, send_conn):
    if not isinstance(insert_data, list):
        log.log_prn("Push", "push_notification input type error, not list", "ERROR")
        return False


    send_conn.send(data for data in insert_data)
    log.log_prn("Push", "Send page %d data into pipe" % insert_data[0]['cur_page'], "NORMAL")
    return True

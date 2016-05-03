import time, random
'''
将utc时间（秒数）转换为本地时间
'''
def transtime(sec, mymode = False):
    if mymode == False:
        return time.asctime(time.localtime(sec))
    else: #返回自定义的格式
        t = time.localtime(sec)
        mytime = str(t[0]) + "年" + str(t[1]) + "月" + str(t[2]) + "日" + \
            str(t[3]) + "时" + str(t[4]) + "分" + str(t[5]) + "秒"
        return mytime

'''
延时
'''
def delay(sec, range):
    if isinstance(sec, int) and isinstance(range, int):
        time.sleep(sec + (random.random() - 0.5) * range)
    else:
        time.sleep(30 + (random.random() - 0.5) * 10)

def get_utc():
    return time.time()

'''
打印级别：
ERROR 错误
NORMAL 一般
WARN 警告
'''
import time

path = r'D:\log.txt'
global fp
def open_log():
    global path,fp
    try:
        fp = open(path, 'a')
        return fp
    except IOError:
        print('Unable to open the log file!')
        return None


def write_log(line):
    global fp
    fp.write(line)
    return
def flush_log():
    global fp
    fp.flush()
    return

def close_log():
    global fp
    fp.close()
    return

def log_prn(module, info, type):
    global fp
    if fp != None:
        cur_time = time.asctime(time.localtime(time.time()))
        log_content = '[[%s]] %s :: [module: %s] : %s\n' % (type, cur_time, module, info)
        write_log(log_content)
        print(log_content)
    return


'''
import multiprocessing
import time, os

def func(x):
    return x * x

if __name__ == "__main__":
    with multiprocessing.Pool(processes=5) as pool:
'''
'''
import multiprocessing
import time
def func(conn1):
    time.sleep(3)
    t = conn1.recv()
    print(t)

if __name__ == "__main__":
    conn1, conn2 = multiprocessing.Pipe(duplex = False)
    p =  multiprocessing.Process(target = func, args = (conn1, ))
    conn2.send("xxxxxx")
    p.start()
    print(p.pid)
    print("main exit")
'''
'''
ddddddddddddddddddddddddddddddddddddddddd
'''

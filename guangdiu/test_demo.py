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

import multiprocessing as mp
import time

"""
1. send item via pipe
2. Receive on the other end by a generator
3. if the pipe is closed on the sending side, retrieve
all item left and then quit.
"""

def func(p):
    pass

if __name__=="__main__":
    p = mp.Pipe(duplex=False)
    #with mp.Process(target=func, args=(p,)) as p:
    #    p.start()
    if isinstance(p, mp.Pipe):
        print(1)
    print(type(p))
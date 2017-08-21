import time
from time import sleep


if __name__ == '__main__':
    p=0
    for n in range(0,100):
       start = time.perf_counter()
       n = n*n*10+3
       endt = time.perf_counter()
       while endt-start < 1:
           endt = time.perf_counter()
       delay = endt-start
       p=1-delay
       print('value:'+str(delay)+'    p:'+str(p))

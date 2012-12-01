#!/usr/bin/python

import urllib, httplib
import getopt, sys
from time import time, sleep
import random
from threading import Thread, currentThread
from math import pow, sqrt
from urlparse import urlparse
import bisect
import re
from math import sqrt

class LatencyTest:
    def ping(self, url):
        parsedUrl = urlparse(url)
        connection = httplib.HTTPConnection(parsedUrl.netloc)
        connection.connect()
        times = []
        for i in range(10):
            start_time = time()
            connection.request('GET', parsedUrl.path + '?x=' + str(random.random()), None,
                    {'Connection': 'Keep-Alive'})
            response = connection.getresponse()
            response.read()
            total_ms = (time() - start_time) * 1000
            times.append(total_ms)
        connection.close()
        times.sort()
        avg = sum(times) / len(times)
        mdev = sqrt(sum((x - avg) ** 2 for x in times) / len(times))
        return {'min': times[0], 'max': times[len(times) - 1], 'avg': avg,'mdev':mdev}
    def pingAll(self):
        f=open('china.txt','r')
        for line in f.readlines():
            data=line.split('\t')
            print data[3]+"\t"+str(self.ping(data[0]))
        return
def main():
    latency = LatencyTest()
    latency.pingAll()
    print latency.ping('http://speedtest02.cmc.co.ndcwest.comcast.net/speedtest/lanteny.txt')
    return

if __name__ == '__main__':
    main()
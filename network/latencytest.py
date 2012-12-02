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
from Queue import Queue

DOWNLOAD_FILES = [
    'random350x350.jpg',
    'random500x500.jpg',
    'random1500x1500.jpg',
    'random2000x2000.jpg',
    'random2500x2500.jpg',
    'random3000x3000.jpg',
    'random4000x4000.jpg'
]
MAX_DOWNLOAD_TIME = 60 * 1 #Limit: 1min
MIN_DOWNLOAD_TIME = 30 #Limit: 30s
MAX_UPLOAD_TIME = 60 * 1 #Limit: 1min
MIN_UPLOAD_TIME = 15 #Limit: 15s
class SpeedTest:
    pingQueue=Queue()
    def download(self, baseUrl):
        parsedUrl = urlparse(baseUrl)
        connection = httplib.HTTPConnection(parsedUrl.netloc)
        connection.connect()
        byte_count = 0
        time_count = 0
        start_time = time()
        shouldStop = False
        while True:
            for fileName in DOWNLOAD_FILES:
                try:
                    connection.request('GET', parsedUrl.path + fileName + '?x=' + str(int(time() * 1000)), None,
                            {'Connection': 'Keep-Alive'})
                    response = connection.getresponse()
                except httplib.BadStatusLine, e:
                    print('error when downloading %s: %s' % (baseUrl, e))
                except httplib.CannotSendRequest, e:
                    print('error when downloading %s: %s' % (baseUrl, e))
                else:
                    while True:
                        # download buffer size = 10KB
                        content = response.read(1024 * 10)
                        time_count=time() - start_time
                        if content:
                            byte_count += len(content)
                            if time_count > MAX_DOWNLOAD_TIME:
                                shouldStop = True
                                break
                        else:
                            break
                if shouldStop or time_count>MIN_DOWNLOAD_TIME:
                    break
        return byte_count * 8 / time_count

    def upload(self, url):
        parsedUrl = urlparse(url)
        time_count = 0
        byte_count = 0
        shouldStop = False
        while True:
            connection = httplib.HTTPConnection(parsedUrl.netloc)
            connection.connect()
            connection.request('POST', url, None,
                    {'Connection': 'Keep-Alive', 'Content-Type': 'application/x-www-form-urlencoded',
                     'Content-Length': 1024*100*1000+1})
            #send the first byte
            connection.send('0')
            block='0'*1024*100
            start = time()
            for x in range(1000):
                connection.send(block)
                time_count = time() - start
                byte_count += len(block)
                if time_count>MAX_UPLOAD_TIME:
                    shouldStop=True
                    break
            if shouldStop or time_count>MIN_UPLOAD_TIME:
                break
        return byte_count * 8 / time_count

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
        return {'min': times[0], 'max': times[len(times) - 1], 'avg': avg, 'mdev': mdev}

    def pingAll(self):
        f = open('server.txt', 'r')
        for line in f.readlines():
            data = line.split('\t')
            self.pingQueue.put(data)
#            print data[3]+", "+data[4] + "\t" + str(self.ping(data[0])['avg'])
        threads=[]
        for x in range(20):
            thread=Thread(target=self.pingWorker, args=())
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        return
    def pingWorker(self):
        while True:
            if self.pingQueue.empty():
                break
            data=self.pingQueue.get()
            print data[3]+", "+data[4] + "\t" + str(self.ping(data[0])['avg'])
            self.pingQueue.task_done()
        return

def main():
    test = SpeedTest()
    start=time()
    test.pingAll()
    print time()-start
#    print test.upload('http://speedtest.fas.ge/speedtest/upload.aspx')
    return

if __name__ == '__main__':
    main()
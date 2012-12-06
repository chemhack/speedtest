#!/usr/bin/python
import socket

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
MAX_DOWNLOAD_TIME = 30 #Limit: 30s
MIN_DOWNLOAD_TIME = 15 #Limit: 15s
MAX_UPLOAD_TIME = 30 #Limit: 30s
MIN_UPLOAD_TIME = 15 #Limit: 15s

class SpeedTest:
    def __init__(self):
        self.pingQueue = Queue()
        self.output = None

    def download(self, baseUrl):
        parsedUrl = urlparse(baseUrl)
        connection = httplib.HTTPConnection(parsedUrl.netloc)
        connection.connect()
        byte_count = 0
        time_count = 0
        start_time = time()
        shouldStop = False
        while not(shouldStop or time_count > MIN_DOWNLOAD_TIME):
            for fileName in DOWNLOAD_FILES:
                try:
                    connection.request('GET', parsedUrl.path + fileName + '?x=' + str(int(time() * 1000)), None,
                            {'Connection': 'Keep-Alive'})
                    response = connection.getresponse()
                except httplib.BadStatusLine, e:
                    print('error when downloading %s: %s' % (baseUrl, e))
                    return None
                except httplib.CannotSendRequest, e:
                    print('error when downloading %s: %s' % (baseUrl, e))
                    return None
                else:
                    while True:
                        # download buffer size = 10KB
                        content = response.read(1024 * 10)
                        time_count = time() - start_time
                        if content:
                            byte_count += len(content)
                            if time_count > MAX_DOWNLOAD_TIME:
                                response.close()
                                shouldStop = True
                                break
                        else:
                            break
                if shouldStop:
                    break
        return byte_count * 8 / time_count

    def upload(self, url):
        parsedUrl = urlparse(url)
        time_count = 0
        byte_count = 0
        shouldStop = False
        while not(shouldStop or time_count > MIN_DOWNLOAD_TIME):
            connection = httplib.HTTPConnection(parsedUrl.netloc)
            connection.connect()
            connection.request('POST', url, None,
                    {'Connection': 'Keep-Alive', 'Content-Type': 'application/x-www-form-urlencoded',
                     'Content-Length': 1024 * 100 * 1000 + 1})
            #send the first byte
            connection.send('0')
            block = '0' * 1024 * 100
            for x in range(1000):
                start = time()
                connection.send(block)
                time_count += time() - start
                byte_count += len(block)
                if time_count > MAX_UPLOAD_TIME:
                    shouldStop = True
                    break
        return byte_count * 8 / time_count

    def ping(self, url):
        parsedUrl = urlparse(url)
        try:
            connection = httplib.HTTPConnection(parsedUrl.netloc, timeout=10)
            connection.connect()
            times = []
            for i in range(5):
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
        except Exception:
            return None

    def pingAll(self):
        f = open('server-small.txt', 'r')
        for line in f.readlines():
            data = line.strip().split('\t')
            self.pingQueue.put(data)
        threads = []
        self.writeLine("****ping****")
        self.pingResults = []
        progressThread = Thread(target=self.progressWorker)
        progressThread.start()
        for x in range(50):
            thread = Thread(target=self.pingWorker, args=[self.pingResults])
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        for result in self.pingResults:
            ping = result['ping']
            self.writeLine('%s\t%.3f/%.3f/%.3f/%.3f' % (result['server'][0], ping['min'],ping['avg'],ping['avg'],ping['mdev']))
        self.writeLine("****end****")
        return self.pingResults

    def progressWorker(self):
        while True:
            finished = len(self.pingResults)
            left = self.pingQueue.unfinished_tasks
            if not left:
                break
            print("Ping: %.2f%%" % (finished * 100.0 / (finished + left)))
            sleep(5)
        return

    def writeLine(self, content):
        if self.output:
            self.output.write(content + '\n')

    def toBaseUrl(self,uploadUrl):
        m=re.search('(.*/)(upload\.\w+)',uploadUrl)
        return m.group(1)

    def smartTest(self):
        self.pingAll()
        #find best server
        bestServer=min(self.pingResults,key=lambda x:x['ping']['avg'])
        uploadUrl = bestServer['server'][0]
#        self.writeLine('best server: %0.2f ' % bestServer['ping']['avg'])
#        print
        print self.download(self.toBaseUrl(uploadUrl))
        print self.upload(uploadUrl)
        return

    def pingWorker(self, results):
        while True:
            if self.pingQueue.empty():
                return
            server = self.pingQueue.get()
            result = self.ping(server[0])
            if result:
                results.append({'server': server, 'ping': result})
            self.pingQueue.task_done()
        return


def usage():
    print '''
usage: speedtest.py [-h] [-s S] [-o S]

Test your bandwidth speed using Speedtest.net servers.

optional arguments:
 -h, --help         show this help message and exit
 -s S, --server=S   run test with specific server
 -o o, --output=O   write output in text file
    '''


def main():
    speedTest = SpeedTest()
    print speedTest.ping('http://down.yiinet.net/speedtest/speedtest/upload.aspx')
#    print speedTest.download('http://down.yiinet.net/speedtest/speedtest/')
#    print speedTest.upload('http://down.yiinet.net/speedtest/speedtest/upload.aspx')
    print speedTest.ping('http://speed.dtgt.org/speedtest/upload.php')
#    print speedTest.download('http://speed.dtgt.org/speedtest/')
#    print speedTest.upload('http://speed.dtgt.org/speedtest/upload.php')
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:o:", ["help", "server=", "output="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--output"):
            speedTest.output = open(a, 'w')
    speedTest.smartTest()
    #    results = speedTest.pingAll()
    #    cityDict = {}
    #    for result in results:
    #        server = result['server']
    #        cityCountry = server[3] + '\t' + server[4]
    #        if not cityDict.has_key(cityCountry):
    #            cityDict[cityCountry] = []
    #        cityDict[cityCountry].append(result)
    #    filteredResult = []
    #    for value in cityDict.values():
    #        value.sort(key=lambda value: value['result']['avg'])
    #        if len(value) > 3:
    #            filteredResult.extend(value[:3])
    #        else:
    #            filteredResult.extend(value)
    #    for result in filteredResult:
    #    #        print result['server']
    #        print '\t'.join(result['server'])
    #        #    print time()-start
    #    print speedTest.ping('http://down.yiinet.net/speedTest/speedTest/latency.txt')
    #    print speedTest.download('http://down.yiinet.net/speedTest/speedTest/')
    #    print speedTest.upload('http://down.yiinet.net/speedTest/speedTest/upload.aspx')
    #    print speedTest.ping('http://speed.dtgt.org/speedTest/latency.txt')
    #    print speedTest.download('http://speed.dtgt.org/speedTest/')
    #    print speedTest.upload('http://speed.dtgt.org/speedTest/upload.php')
    return

if __name__ == '__main__':
    main()
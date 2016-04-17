#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Author: (linuxfish.exe@gmail.com)
#########################################################################
# Created Time: 2016-04-12 17:43:55
# File Name: poller.py
# Description: check the availability of the links of a website recursively
#########################################################################

import re
import time
import threading
import logging
import logging.config
import ConfigParser
import Queue
from urlparse import urljoin,urlparse
import socket

import requests

class sohuPoller(object):

    def __init__(self, cfg):
        self.logger = logging.getLogger('sohuPoller')
        self.tasks = Queue.Queue()
        self.seen = set()
        self.lock = threading.Lock()
        self.thread_num = cfg.getint('default', 'thread_num')
        self.timeout = cfg.getint('default', 'timeout')
        self.url_regx = re.compile(r'href="([^"]*?)"')
        self.base_url = cfg.get('default', 'base_url')

    def start_thread_pool(self):
        for i in range(self.thread_num):
            t = threading.Thread(target=self.worker)
            t.start()
            time.sleep(1)

    def worker(self):
        while True:
            print '%d tasks to do, %d crawled, %d workers are working'  % (self.tasks.qsize(), len(self.seen), threading.active_count())
            try:
                url = self.tasks.get_nowait()   # consume task
            except Queue.Empty:
                break

            try:
                r = requests.get(url, allow_redirects=False, timeout=self.timeout)
                content = r.text
            except (requests.exceptions.RequestException,socket.timeout) as e:   # have to catch socket.timeout too, its a requests(or urllib3) bug
                self.logger.warn('%s, %s' % (e, url))                            #  see https://github.com/kennethreitz/requests/issues/1236
                continue                                                         #  if url is not reachable, then there is  no need to add task
#            self.logger.info('%d, %s' % (r.status_code, url))
            urls = self.url_regx.finditer(content)
            for match in urls:
                url = match.group(1)
                if not url.startswith('http'):
                    url = urljoin(self.base_url, url)
                if url.startswith('javascript') or (not url.startswith(self.base_url)):
                    continue
                path = urlparse(url).path
                url = urljoin(self.base_url, path)
                with self.lock:
                    if url not in self.seen:   # avoid duplicated crawling
                        self.seen.add(url)     #  add task
                        self.tasks.put(url)

    def run(self):
        self.tasks.put(self.base_url)
        self.start_thread_pool()


if __name__=='__main__':
    logging.config.fileConfig('conf/logging.conf')
    cfg = ConfigParser.RawConfigParser()
    cfg.read('conf/poller.cfg')
    poller = sohuPoller(cfg)
    poller.run()

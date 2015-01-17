#encoding: utf-8

'''
This file contains functions to:
(1) readin all keywords;
(2) readin website addresses;
(3) readin all related information
'''

import urllib2, requests
import re
import Queue
import time


sites=[u'http://www.ttmeiju.com']
page_queue = Queue.Queue()
unread_page_queue=Queue.Queue()
read_page = []

def dispatcher(unread_page_queue):
    url = unread_page_queue.get()
    crawler(url)

class crawler(object):
    def __init__(self,tgt_url):
        self.start_url = tgt_url

    def __open_url(self):
#note 15/1/17: open_url and parse_addr are defined as private functions, therefore can only be accessed
#from within the class. Also, to call private functions from within the class, one need to do self.__xxxx()
        #import urllib2
        try:
            page=urllib2.urlopen(self.start_url)
        except urllib2.HTTPError:
            raise ValueError, 'invalid address'
        return page.read()

    def __parse_addr(self, page=self.__open_url()):
        #import re
        pattern=re.compile(r'\<a href="(?P<addr>.*)"\>')
        #(?P<addr>.*) means matching any number of any char (.*), and ref them as 'addr'
        result=[]
        for i in re.finditer(pattern,page.lower()):
            result.append(i.group('addr'))

        return result




def init():
    original_addr = sites[0]
    page_queue.put(original_addr)
    unread_page_queue.put(original_addr)


def parse_addr(page_addr):
    from bs4 import BeautifulSoup as bsoup
    import urllib2
    #start=time.time()  
    #page = requests.get(page_addr)
    try:
        page = urllib2.urlopen(page_addr)
    except urllib2.HTTPError:
        raise ValueError, 'invalid address'
        #return None 
#NOTE: when raised an error, the function automatically ends and returns to caller
#and any command after raise error will not execute
    #if page.status_code != requests.codes.ok:
    ##determines whether the page can be opened
    #    raise ValueError, 'invalid address'
    ##throws an Error is better than return 'ERROR', since the latter
    ##will also affect the main_dispatch() flow-control structures

#TODO 141230: requests module provides r.text, which is a unicode variable, and cause problem for file writing

    #addr_pat = r'href=http://[\.\-/A-Za-z0-9=]*\.html'
    #re patern:
    #1. begins with href=http://
    #2. contains any number of A-Z, a-z, 0-9, ., -, and /
    #3. ends with .html
#TODO 141231: try to make it work with re and without beautifulsoup
#141231 problem: this pattern indicates all 3 kinds of characters must present at the same time
#while -,=,. may not in certain cases
    
    soup = bsoup(page.read())
    raw_links=[link.get('href') for link in soup.find_all('a')]
    raw_links=filter(lambda x: x is not None, raw_links)
    eligible_links=[n for n in raw_links if n.startswith('http')]

    #test_end = time.time()

    for i in eligible_links:
        yield i

def read_check(url):
    #check whether the link has already be read
    if url in read_page:
        return False
    else:
        return True

def main_dispatch():
    init()
    while unread_page_queue.empty() is False:
#TODO 150101: why use unreadqueue is emty as condition?
        try:
            a=parse_addr(unread_page_queue.get())
            for i in a:
                if read_check(i):
                    unread_page_queue.put(i)
                    read_page.append(i)
                else:
                    continue

        except ValueError:
            continue

    pass

def parse_addr2(page_addr):
    #this function tries to find out all urls without using beautifulsoup
    from urllib2 import urlopen, HTTPError
    import re
    try:
        page = urlopen(page_addr)
    except HTTPError:
        raise ValueError, 'invalid address'

    page_content = page.read()
    pat_addr = r'href="([http:]{5}|[https:]{6})//.*\.html"'
        #pat_addr refers to pattern of a url, which may take the form of http:// or https://

    if re.search(pat_addr,page_content) is None:
        raise ValueError, 'Keywords not Found'
    else:
        for i in re.finditer(pat_addr,page_content):
            yield i.group()





if __name__ == '__main__':
    main_dispatch()
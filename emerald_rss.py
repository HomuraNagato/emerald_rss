"""
objective: capture video and audio from various sites to watch offline

news outlets

 - BBC Westminster Hour (weekly) https://www.bbc.co.uk/programmes/p02nrs6c/episodes/downloads
 - marketplace https://www.marketplace.org/podcasts -> https://feeds.publicradio.org/public_feeds/marketplace-pm/rss/rss


Potential podcasts
 - 

in addition to any imports, also need to install:
  pip install html5lib
"""

import certifi                  # certificate to verify HTTPS requests
from bs4 import BeautifulSoup   # create soup from webpage-object
import logging
import logging.config
import os
import re
import numpy as np
import threading
import yaml
#import urllib
import urllib3                  # open webpage as an object

from emerald_thread import EmeraldThread

def choose_source():
    """
    allow user to select from which source they wish to download from

    :config:  dict of various elements required to trek and download from selected source
    :class:   globals allows us to get a class eg. Westminster which we can then instantiate
    """

    f = open('configs/config.yaml', 'r')
    config = yaml.safe_load(f)
    f.close()
    sources = list(config.keys())
    
    print("which source would you like to choose from?\n")
    [ print('\t', i, x) for i, x in enumerate(sources) ]
    selection = int(input('\n'))

    if selection not in range(0,len(sources)):
        print("try again")
        return choose_source()

    name = str(sources[selection])
    return config[name], globals()[name]

def load_prefs():
    """
    alter preferences.yaml for personal preference

    :display_limit:   limit number of episodes to display, starting with most recent
                      -1 (or any negative number) shows all
    :max_concurrent:  number of threads to use; less if not enough episodes requested
    :verbose:         whether to log additional info while downloading
    """
    f = open('configs/preferences.yaml', 'r')
    prefs = yaml.safe_load(f)
    f.close()
    return prefs

def assert_path(pdir):
    """ make a directory for source if it hasn't been made """
    if not os.path.isdir(pdir):
        print("the directory", pdir, "does not exist, creating now")
        os.mkdir(pdir)
    return None


class Episode(object):

    def __init__(self, source, prefs, name=''):
        self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        self.source = source
        self.limit = prefs['display_limit']
        self.nthreads = prefs['max_concurrent']
        self.verbose = prefs['verbose']
        self.name = name
        
        logging.config.fileConfig('configs/logging.conf')
        logging.info('youkoso')
        self.logThrd      = logging.getLogger('thread')
        
    def __str__(self):
        return "{} - {}".format(self.name, self.url)

    def soup_request(self, url, log=False):
        response = self.http.request('GET', url)
        soup = BeautifulSoup(response.data.decode('utf-8'), "html5lib")
        if log:
            f = open('configs/request.log', 'w')
            f.write(soup.prettify())
            f.close()
        return soup

    def access_data_links(self):
        s2 = []
        idx = 0

        # list of dicts of downloadable content
        for link in self.links:
            row = self.finder(link, idx)
            s2.append(row)
            idx += 1
            
        # first filter
        if self.limit < 0:
            self.limit = len(self.links)
        s2 = s2[0:self.limit]
        
        # prompt for downloads
        print("Content available to download\n")
        [ print('\t', d['idx'], d['date'], d['meta_text']) for i, d in enumerate(s2) ]
        print()

        # selection for second filter
        selections = input(":enter: = download all; # = download individual; #-# = download between range: ")

        # various ways to select content 
        start, end = 0, len(s2)
        if selections == 'enter':
            pass
        if selections == '':
            self.url_request()
        elif '-' in selections:
            start, end = list(map(int, selections.split('-')))
            end += 1
        elif selections == 'exit' or selections == 'quit':
            quit()
        else:
            start, end = int(selections), int(selections)+1
            
        assert( 0 <= start < end ), "first digit invalid range"
        assert( 0 <= end <= len(s2) ), "second digit invalid range"

        # apply second filter
        self.s2 = s2[start:end]

    
    def download_content(self):
        """
        instantiate threads with a queue among other items
        actually start the process of accessing the parsed urls
        and downloading the content
        """

        nreqs = len(self.s2)
        assert_path(self.directory)
        queue = list(range(nreqs)) # 10 for testing
        threads = []
        threadlock = threading.Lock()
        
        # Create threads, less if fewer requested content
        nthreads = 5
        for i in range(min(nthreads, nreqs)):
            # threadlock, f, queue, doc_emb should be passed by reference?
            thread = EmeraldThread(i+1, "thread-{}".format(i+1), threadlock, 
                                   self.logThrd, queue, len(queue), self.s2,
                                   self.directory, self.verbose, self.http)
            thread.start()
            threads.append(thread)

        # wait for threads to complete
        for t in threads:
            t.join()                

        return None


class Westminster(Episode):

    def __init__(self, source, prefs):
        Episode.__init__(self, source, prefs, 'Westminster')
        
        self.url = self.source['url']
        self.directory = self.source['directory']
        self.head_tag = self.source['head_tag']
        self.date_tag = self.source['date_tag']
        self.url_tag = self.source['url_tag']
        self.regexText = self.source['regexText']
        self.regexDate = self.source['regexDate']
        print("initialized {}".format(self))
        
    
    def url_request(self):
        """
        example link
        <a class="link-complex popup__list__item island--squashed br-subtle-bg-ontext br-subtle-bg-onbg--hover 
                  br-subtle-link-ontext--hover" 
         download="Westminster Hour, Westminster Hour 16 Dec 18 - p06vsn47.mp3" 
         href="https://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/
               audio-nondrm-download/proto/https/vpid/p06vsmyg.mp3"> 
         Higher quality (128kbps) 
        </a>

        Download
        mp3 for audio file. 128kpbs for high quality audio
        """
        self.links = self.soup_request(self.url, log=True).find_all(self.head_tag, text=re.compile(self.regexText), attrs={self.date_tag: True})
        #print("links: {}\n{}".format(self.links, len(self.links)))

    def finder(self, link, idx):
        #print("***************** {} *****************")
        #print(link)
        date = re.search(self.regexDate, link[self.date_tag]).group(1)
        text = link.get_text().strip()
        url_link = link[self.url_tag]
        #print("link date: {}  text: {}  url: {}".format(date, text, url_link))
        row = { 'idx': idx, 'date': date, 'link': url_link, 'meta_text': text }
        return row
        

class MarketPlace(Episode):

    def __init__(self, source, prefs):
        Episode.__init__(self, source, prefs, 'MarketPlace')
        self.url = self.source['url']
        self.directory = self.source['directory']
        self.head_tag = self.source['head_tag']
        self.date_tag = self.source['date_tag']
        self.text_tag = self.source['text_tag']
        self.url_tag = self.source['url_tag']
        print("initialized {}".format(self))
    
    def url_request(self):
        self.links = self.soup_request(self.url, log=False).find_all(self.head_tag)
    
    def finder(self, link, idx):
        date = link.find(self.date_tag).get_text()
        text = link.find(self.text_tag).get_text()
        url_link = link.find(self.url_tag)['url']
        row = { 'idx': idx, 'date': date, 'link': url_link, 'meta_text': text }
        return row


if __name__ == "__main__":

    preferences = load_prefs()
    source, Class = choose_source()
    eps = Class(source, preferences)
    eps.url_request() # determine source to download from
    eps.access_data_links() # choose content and purify
    eps.download_content() # download content

    print("downloading complete :)")



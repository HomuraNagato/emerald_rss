'''
Chosen gemstone: emerald
objective: capture video and audio from various sites to watch offline

news outlets

 - BBC Westminster Hour (weekly) https://www.bbc.co.uk/programmes/p02nrs6c/episodes/downloads
 - marketplace https://www.marketplace.org/podcasts -> https://feeds.publicradio.org/public_feeds/marketplace-pm/rss/rss
 - mangarock   https://mangarock.us/manga/mahou-tsukai-no-yome

Potential podcasts
 - Microsoft Channel 9 videos
 - the cloud cast - http://www.thecloudcast.net
'''

import urllib
import urllib3                  # open webpage as an object
import certifi                  # certificate to verify HTTPS requests
from bs4 import BeautifulSoup   # create soup from webpage-object
import os
import re
import numpy as np

#from cStringIO import StringIO
#from PIL import Image

def choose_source():

    # westminster hour
    westminster_hour = { 'url': 'https://www.bbc.co.uk/programmes/p02nrs6c/episodes/downloads',
                         'directory': 'westminster_hour',
                         'meta_type': 'a',
                         'meta_search': ('Westminster\sHour\s(.*)\s\-', 'download'),
                         'text_filter': '128kbps',
                         'data_link': 'href',
                         'request': True
                         }


    # marketplace
    marketplace = {'url': 'https://feeds.publicradio.org/public_feeds/marketplace-pm/rss/rss',
                   'directory': 'marketplace',
                   'meta_type': 'enclosure',
                   'meta_search': ('pm/(.*)/pm', 'url'),
                   'text_filter': '',
                   'data_link': 'url',
                   'request': True
                   }

    # mangareader
    mangarock = {'url': 'https://mangarock.us',
                 'directory': 'mangarock',
                 'meta_type': 'a',
                 'meta_search': '.*chapter-([\d.\-]+)',
                 'text_filter': '',
                 'data_link': '',
                 'request': True
                 }

    sources = ['westminster hour', 'marketplace', 'mangarock']


    print("which source would you like to choose from?\n")
    [ print('\t', i, x) for i, x in enumerate(sources) ]
    selection = input('\n')
    if selection == '0':
        source = westminster_hour
    elif selection == '1':
        source = marketplace
    elif selection == '2':
        source = mangarock
    else:
        print("try again")
        return choose_source()
    #print("returning", source)
    return source


def soup_request(url):
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "html5lib")
    return soup

def url_request(url, directory, meta_type, text_filter, meta_search, data_link, request, end_available=5):

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    response = http.request('GET', url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "html5lib")
    links = soup.find_all(meta_type)

    #print(soup.prettify())

    links = soup_request(url).find_all(meta_type)

    s2 = []
    counter = 0

    '''
    example link
    <a class="link-complex popup__list__item island--squashed br-subtle-bg-ontext br-subtle-bg-onbg--hover 
    br-subtle-link-ontext--hover" download="Westminster Hour, Westminster Hour 16 Dec 18 - p06vsn47.mp3" 
    href="https://open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/proto/https/vpid/p06vsmyg.mp3"> 
    Higher quality (128kbps) </a>

    Download
    mp3 for audio file. 128kpbs for high quality audio

    '''
    for link in links:

        #print(link)
        #print("searching for", meta_search[0], meta_search[1])

        try:
            date_regex = re.search( meta_search[0], link[meta_search[1]] )
            text_regex = re.search( text_filter, link.get_text() )
        
            if date_regex and text_regex:
                print("link", link[data_link])
                print("regex:", date_regex.group(0))
                date = date_regex.group(1)
                if '/' in date:
                    date = date.replace('/', '-')
                s2.append({ 'date': date, 'link': link[data_link], 'meta_text': link.get_text(), 'counter': counter })     
                counter += 1
        except:
            #print("link does not have meta_search[1]", meta_search[1])
            pass

        
    print("Content available to download\n")
    [ print('\t', d['counter'], d['date'], d['meta_text']) for i, d in enumerate(s2[0:end_available]) ]
        
    selections = input("Type enter to view all content or enter a value or range to download from the indicated content: ")

    if selections == '':
        return url_request(url, directory, meta_type, text_filter, meta_search, data_link, request, end_available=len(s2))
    elif '-' in selections:
        start, end = list(map(int, selections.split('-')))
    elif selections == 'exit' or selections == 'none':
        quit()
    else:
        start, end = int(selections), int(selections)+1
        
    s2 = s2[start:end]

    for i, d in enumerate(s2):
        
        i += 1
        print("downloading content", i, "of", len(s2))
        
        if request == True:
            http_lookahead = re.search('http(s)?:', d['link'])
            if not http_lookahead:
                d['link'] = 'http:' + d['link']
                print("add http to dlink. It is now: ", d['link'])

            save_location = directory + '/' + d['date'] + '.mp3'
            content = http.request('GET', d['link'], preload_content = False)

            verify_directory(directory)
            save_fragment(content, save_location)
    
    print("downloading complete :)")

    return None

def verify_directory(directory):
    # TODO
    # make a directory for the chapter if it hasn't been made
    if not os.path.isdir(directory):
        print("the directory", directory, "does not exist")
        os.mkdir(directory)
    return None

def choose_chapters(links, meta_type, meta_search):
    # choose chapters for manga downloading

    chapter_dict = {}
    
    for link in links:
        try:
            chapter_number = re.search( meta_search, link['href'] )
            chapter_dict[chapter_number.group(1)] = chapter_number.group(0)
        except:
            pass

    print("which chapter(s) do you wish to download? ")
    for chapter in chapter_dict:
        print("chapter", chapter)

    selection = input("type all to download all or the chapter number to download that specific chapter. ")


    if selection == 'all':
        return_list = [ chapter_dict[url] for url in chapter_dict ]
    elif selection in chapter_dict:
        return_list = [chapter_dict[selection]]
    else:
        print("selection not valid")
        return_list = []
    
    return return_list

def learn_page_total(url_page):
    
    links = soup_request(url_page).find_all('script')
    page_total = ''
    
    for link in links:
        #print("page total link:\n", str(link))
        regex_page_total = re.search('.*page_total\s=\s(.*);.*', str(link))
        try:
            print("page total", regex_page_total.group(1).strip())
            page_total = regex_page_total.group(1).strip().replace('\'','')
        except:
            pass

    print("chapter", url_page, "has", page_total, "pages")
    
    return page_total

def save_fragment(content, save_location):
    
    print("saving content", save_location)
    
    content_length = int(content.headers['Content-Length'])
    block = 0
    block_size = 1024
    percent_step = 0.1
    percent_complete = percent_step
        
    with open(save_location, 'wb') as code:

        for fragment in content.stream(block_size):
            block += 1
            if (block_size * block) / content_length > percent_complete:
                percent_complete += percent_step
                print('.', end='')
            code.write(fragment)

    content.release_conn()
    print()

def collect_chapters(chapter_requests, directory, manga_title):

    for chapter in chapter_requests:
        url_chapter = chapter + '?page='
        url_page = url_chapter + '1'
        chapter_number = re.search('.*chapter-([\d.\-]+)', chapter).group(1)

        page_total = learn_page_total(url_page)
        
        for i in range(1, int(page_total)+1):
            url_page = url_chapter + str(i)
            #print("collecting page", url_page)
            img_source = soup_request(url_page).find_all('img', {'class': 'img'} )[0]['src']
            save_path = directory +'/' + manga_title + '/chapter_' + chapter_number
            save_location =  save_path + '/page_' + str(i) + '.jpeg'

            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            img_request = http.request('GET', img_source, preload_content = False)

            verify_directory(save_path)
            save_fragment(img_request, save_location)
            
    return None

def mangarock_chapter_request(url, directory, meta_type, meta_search):

    '''
    example link
    <a href="https://mangarock.us/mahou-tsukai-no-yome-chapter-0" title="Mahou Tsukai no Yome Chapter 0">Mahou Tsukai no Yome Chapter 0</a>

    Download
    mp3 for audio file. 128kpbs for high quality audio
    '''
    manga_title = input("What is the name of the manga you wish to download?\nFor example to download The Ancient Magus Bride has url extension mahou-tsukai-no-yome ")
    #manga_title = 'mahou-tsukai-no-yome'
    print("searching mangarock for manga", manga_title)

    url_title = url + '/' + manga_title
    
    # get the objects in the url that have the indicated meta_type
    links = soup_request(url_title).find_all(meta_type)

    #print(links[0])

    meta_manga_search = '.*' + manga_title + '-' + meta_search
    chapter_requests = choose_chapters(links, meta_type, meta_manga_search)

    print("chapter requests", chapter_requests)

    collect_chapters(chapter_requests, directory, manga_title)
    
    print("downloading complete :)")

    return None

# main

meta_source = choose_source()
url = meta_source['url']
directory = meta_source['directory']
meta_type = meta_source['meta_type']
text_filter = meta_source['text_filter']
meta_search  = meta_source['meta_search']
data_link   = meta_source['data_link']
request    = meta_source['request']

if 'mangarock' in url:
    mangarock_chapter_request(url, directory, meta_type, meta_search)
else:
    url_request(url, directory, meta_type, text_filter, meta_search, data_link, request)


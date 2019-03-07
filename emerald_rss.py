'''
Chosen gemstone: emerald
objective: capture video and audio from various sites to watch offline

news outlets

 - BBC Westminster Hour (weekly) https://www.bbc.co.uk/programmes/p02nrs6c/episodes/downloads
 - marketplace https://www.marketplace.org/podcasts -> https://feeds.publicradio.org/public_feeds/marketplace-pm/rss/rss

Potential podcasts
 - Microsoft Channel 9 videos
 - the cloud cast - http://www.thecloudcast.net
'''

import urllib3                  # open webpage as an object
import certifi                  # certificate to verify HTTPS requests
from bs4 import BeautifulSoup   # create soup from webpage-object
import re

def choose_source():
    
    # westminster hour
    westminster_hour = { 'url': 'https://www.bbc.co.uk/programmes/p02nrs6c/episodes/downloads',
                         'directory': 'westminster_hour',
                         'meta_type': 'a',
                         'meta_name': ('Westminster\sHour\s(.*)\s\-', 'download'),
                         'text_filter': '128kbps',
                         'data_link': 'href',
                         'request': True
                         }

    
    # marketplace
    marketplace = {'url': 'https://feeds.publicradio.org/public_feeds/marketplace-pm/rss/rss',
                   'directory': 'marketplace',
                   'meta_type': 'enclosure',
                   'meta_name': ('pm/(.*)/pm', 'url'),
                   'text_filter': '',
                   'data_link': 'url',
                   'request': True
                   }
    
    sources = ['westminster hour', 'marketplace']


    print("which source would you like to choose from?\n")
    [ print('\t', i, x) for i, x in enumerate(sources) ]
    selection = input('\n')
    if selection == '0':
        source = westminster_hour
    elif selection == '1':
        source = marketplace
    else:
        print("try again")
        choose_source()
    #print("returning", source)
    return source

    

def url_request(url, directory, meta_type, text_filter, meta_name, data_link, request, end_available=5):

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    response = http.request('GET', url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "html5lib")

    #print(soup.prettify())

    links = soup.find_all(meta_type)

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
        #print("searching for", meta_name[0], meta_name[1])

        try:
            date_regex = re.search( meta_name[0], link[meta_name[1]] )
            text_regex = re.search( text_filter, link.get_text() )
        
            if date_regex and text_regex:
                #print("link", link[data_link])
                #print("regex:", date_regex.group(0))
                date = date_regex.group(1)
                if '/' in date:
                    date = date.replace('/', '-')
                s2.append({ 'date': date, 'link': link[data_link], 'meta_text': link.get_text(), 'counter': counter })     
                counter += 1
        except:
            #print("link does not have meta_name[1]", meta_name[1])
            pass
    # 
        
    print("Content available to download\n")
    [ print('\t', d['counter'], d['date'], d['meta_text']) for i, d in enumerate(s2[0:end_available]) ]
        
    selections = input("Type enter to view all content or enter a value or range to download from the indicated content: ")

    if selections == '':
        url_request(url, directory, meta_type, text_filter, meta_name, data_link, request, end_available=len(s2))
        return None
    elif '-' in selections:
        start, end = list(map(int, selections.split('-')))
    elif selections == 'exit' or selections == 'none':
        quit()
    else:
        start, end = int(selections), int(selections)+1
        
    s2 = s2[start:end]

    for i, d in enumerate(s2):
        
        i += 1
        block = 0
        block_size = 1024
        percent_step = 0.1
        percent_complete = percent_step
    
        print("downloading content", i, "of", len(s2))
        if request == True:
            http_lookahead = re.search('http(s)?:', d['link'])
            if not http_lookahead:
                d['link'] = 'http:' + d['link']
                print("add http to dlink. It is now: ", d['link'])

                
            content = http.request('GET', d['link'], preload_content = False)
            content_length = int(content.headers['Content-Length'])
            print("downloading: ", end='')

            with open(directory + '/' + d['date'] + '.mp3', 'wb') as code:

                for fragment in content.stream(block_size):
                    block += 1
                    if (block_size * block) / content_length > percent_complete:
                        percent_complete += percent_step
                        print('.', end='')
                    code.write(fragment)

            content.release_conn()
            print()
    print("downloading complete :)")

    return None

# main

meta_source = choose_source()
url = meta_source['url']
directory = meta_source['directory']
meta_type = meta_source['meta_type']
text_filter = meta_source['text_filter']
meta_name  = meta_source['meta_name']
data_link   = meta_source['data_link']
request    = meta_source['request']
url_request(url, directory, meta_type, text_filter, meta_name, data_link, request)

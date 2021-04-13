
import re
import threading

class EmeraldThread(threading.Thread):
    
    def __init__(self, id, name, lock, logThrd, q, n, s2, pdir, verbose, http):
        threading.Thread.__init__(self)
        self.id = id
        self.name = name
        self.lock = lock
        self.logThrd = logThrd
        self.q = q
        self.n = n
        self.s2 = s2
        self.total = len(self.s2)
        self.pdir = pdir
        self.verbose = verbose
        self.http = http
        self.count = 0

    def run(self):
        """ call this function with thr.start() """
        self.download_threaded_content()
        self.logThrd.info("{} completed {} items".format(self.name, self.count))

    def download_threaded_content(self):
        """
        the queue contains indicies into our list of dicts with meta and link to
        download content from. When a thread is read, it will take the next item
        off the queue, process it, then start downloading.
        """
        
        while len(self.q) > 0:
            i = self.q.pop(0)
            d = self.s2[i]
            #self.logThrd.info("{} processing content {}".format(self.name, i))

            http_lookahead = re.search('http(s)?:', d['link'])

            if not http_lookahead:
                d['link'] = 'http:' + d['link']
                #print("add http to dlink. It is now: ", d['link'])

            save_location = self.pdir + '/' + d['date'] + '.mp3'
            content = self.http.request('GET', d['link'], preload_content = False) # closed in save_fragment
            self.logThrd.info("downloading content {} of {}: {}".format(i+1, self.total, save_location))

            #self.lock.acquire()
            self.save_fragment(content, save_location)
            #self.lock.release()
            self.count += 1

            
    def save_fragment(self, content, save_location):
        """
        stream content in blocks for performance
        """

        content_length = int(content.headers['Content-Length'])
        block = 0
        block_size = 1024
        percent_step = 0.1
        percent_complete = percent_step

        with open(save_location, 'wb') as code:

            for fragment in content.stream(block_size):
                block += 1
                if self.verbose and (block_size * block) / content_length > percent_complete:
                    percent_complete += percent_step
                    self.logThrd.info("{} {}% complete".format(save_location, round(percent_complete, 2)))
                code.write(fragment)

        content.release_conn()
        return True

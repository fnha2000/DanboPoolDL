import os
import socket
import urllib.request
import configparser
from htmldom import htmldom
from html import unescape
import string

class PoolLoader (object):
    def __init__(self, pool, config):
        self.danboURL = 'http://danbooru.donmai.us'
        self.danboPoolURL = ''
        self.poolID = pool
        self.downloaded = 0
        self.currentPos = 1
        self.poolTitle = ''
        self.totalPages = 0
        self.inDlDir = False
        self.config = config
        socket.setdefaulttimeout(60);
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
        self.opener.addheaders = [('User-agent', 'DanboPoolDL')]
        urllib.request.install_opener(self.opener)

    def getImgs(self):
        poolURL = str.format('http://danbooru.donmai.us/pools/{0}', self.poolID)
        print('Loading page 1')

        dom = htmldom.HtmlDom(poolURL).createDom()
        paginator = dom.find('#description+section div.paginator li')
        try:
            paginator = paginator.eq(paginator.len - 2).find('a').first()
            self.totalPages = int(paginator.text())
        except AttributeError:
            self.totalPages = 1

        titleNode = dom.find('a.pool-category-series').first()
        rawTitle = titleNode.text()[titleNode.text().find(":")+1:]
        self.poolTitle = unescape(rawTitle.strip())

        postsNode = dom.find('#description + section article')
        self.loadPages(postsNode)  

        for i in range(2, self.totalPages + 1):
            pageURL = str.format(poolURL + '?page={0}', i)
            print(str.format('Loading page {0}', i))
            
            dom = htmldom.HtmlDom(pageURL).createDom()
            postsNode = dom.find('#description + section article')
            self.loadPages(postsNode)
            
        print('Complete.\nTotal images downloaded: %d' % self.downloaded)


    def loadPages(self, postsNode):
        for postLink in postsNode:
            linkNode = postLink.find('a')
            link = self.danboURL + linkNode.attr('href')
            self.downloadImg(link)



    def downloadImg(self, link):
        dom = htmldom.HtmlDom(link).createDom()
        imgElem = dom.find('#image-container').first()
        imgURL = ''
        if self.config['Settings']['DownloadOriginal'] == 'No':
            imgURL = self.danboURL + imgElem.attr('data-large-file-url')
        else:
            imgURL = self.danboURL + imgElem.attr('data-file-url')
        srcfile = imgElem.attr('data-large-file-url').split('/')
        filename = str.format('{0:03d}-' + srcfile[len(srcfile)-1], self.currentPos)
        
        if not self.inDlDir:
            destDir = ''
            if self.config['Settings']['DownloadDirectory'] == '':
                destDir = os.getcwd() + '\\' + self.poolTitle
            else:
                destDir = self.config['Settings']['DownloadDirectory'] + '\\' + self.poolTitle
            if not os.path.exists(destDir):
                print('Creating directory ' + destDir)
                os.mkdir(destDir)
            os.chdir(destDir)
            self.inDlDir = True

        imgfile = None
        if not os.path.isfile(filename):
            imgfile = open(filename, 'wb')

        if not imgfile is None:
            print(str.format('Downloading {0}', srcfile[len(srcfile)-1]))
            try:
                file = urllib.request.urlopen(imgURL)
                dlComplete = False
                data = file.read()
                imgfile.write(data)
                dlComplete = True
                self.downloaded += 1
            except KeyboardInterrupt:
                if not dlComplete:
                    imgfile.close()
                    os.remove(filename)
                print('Download interrupted')
                raise
            except urllib.error.HTTPError:
                if not dlComplete:
                    imgfile.close()
                    os.remove(filename)
                print('Download failed')
                raise
            imgfile.close()
            print('Done')
        self.currentPos += 1
        
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 czh
#
# Distributed under terms of the MIT license.
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import time
import datetime
import os


class crawler:
    def __init__(self):
        self.local_time = time.strftime("%Y-%m-%d", time.localtime())
        os.makedirs('./%s/' %self.local_time, exist_ok=True)
        self.file_name = int(0)
        self.sort_base = "http://news.pchome.com.tw/cat/"
        self.sort_list = ["politics", "society", "finance", "science", "internation", "china",
                          "healthcare", "sport", "living", "expense", "travel", "magazine", "car", "public"]

    def check_url(self, url):
        self.news_url
        i = 0
        while i < len(self.news_url):
            if url['href'] == self.news_url[i]:
                break
            i += 1
        else:
            self.news_url.append(url['href'])

    def get_url(self, sort_url):
        html = urlopen(sort_url).read().decode('utf-8')
        soup = BeautifulSoup(html, features='html.parser')
        pages = soup.find_all(name="select")                    # calculation pages
        pages = int(re.search(r'(\d+)</option></select>]$', str(pages)).group(1))
        for page in range(pages):
            if page != 0:
                next_page_url = str(sort_url) + "/" + str(page + 1)
                html = urlopen(next_page_url).read().decode('utf-8')
                soup = BeautifulSoup(html, features='html.parser')
            sub_urls = soup.find_all("a", {"href": re.compile("^/(.+).html$")})
            for sub_url in sub_urls:
                self.check_url(sub_url)
        print("pages:%s" % pages)

    def news_cntent(self, soup):
        try:
            title = soup.find(name="p", attrs={"class": "article_title"})
            title = re.search('title=(.+)><span', str(title)).group(1)
        except AttributeError:
            print('AttributeError')
        else:
            title = re.sub(r'/|\'|\"', '', title)
            time = soup.find_all(name="time")
            if len(time) != 0:
                time = re.search(r'datetime="(\d\d\d\d-\d\d-\d\d)', str(time)).group(1)
            else:
                time = 'notime'
            content = soup.find_all(name="div", attrs={"calss": "article_text"})
            content = re.sub(r'\[<di(.+)xt">|<span(.+)/span>|</br>|<br>|<br/>|</div>]|<im(.+)pg"/|<!-(.+)->|\n|\t',
                             '', str(content))
        return time, title, content

    def main(self):
        for i in range(len(self.sort_list)):
            self.news_base = "http://news.pchome.com.tw"
            self.news_url = []

            sort_url = self.sort_base + self.sort_list[i]
            self.get_url(sort_url)
            print("sort:%s, urls:%s  " %(i, len(self.news_url)))

            for j in range(len(self.news_url)):
                try:
                    url = self.news_base + self.news_url[j]
                except IndexError:
                    print("IndexError")
                else:
                    html = urlopen(url).read().decode('utf-8')
                    soup = BeautifulSoup(html, features='html.parser')
                    time = soup.find_all(name="time")
                    print("news loading=%s/%s, url=%s" % (j, len(self.news_url), url))
                    if time and (datetime.datetime.now() - datetime.datetime.strptime(          # get news before 24 hour
                            re.search(r'"(.+)" ', str(time)).group(1), '%Y-%m-%d %H:%M:%S')).days == 0:
                        time, title, content = self.news_cntent(soup)
                        with open('./%s/%s' % (self.local_time, self.file_name), 'a') as saveFile:
                            saveFile.write('%s\n%s\n%s' % (time, title, content))
                        self.file_name = self.file_name + 1

if __name__ == '__main__':
    news = crawler()
    news.main()
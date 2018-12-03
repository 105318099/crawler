# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 czh
#
# Distributed under terms of the MIT license.
import jieba.analyse
import psycopg2
import re
import time
import os


class Upload:
    def __init__(self):
        self.local_time = time.strftime("%Y-%m-%d", time.localtime())
        self.DIR = '/home/chtczh/PycharmProjects/WebExtract/%s' % self.local_time  # dir path
        self.file_num = len([name for name in os.listdir(self.DIR) if os.path.isfile(os.path.join(self.DIR, name))])
        # set connection data
        self.conn_inf = psycopg2.connect(database="DB", user="root", password="5471", host="127.0.0.1", port="5432")
        print("Connection established")
        self.cursor = self.conn_inf.cursor()

    # Drop previous table of same name if one exists
    def drop(self, table_name):
        self.cursor.execute("DROP TABLE IF EXISTS %s;" % table_name)
        print("Finished dropping table (if existed)")

    # Create table
    def create(self, table_name):
        self.cursor.execute("CREATE TABLE news (id serial PRIMARY KEY, date TEXT, title TEXT, content TEXT);")
        self.cursor.execute("CREATE TABLE keyword (id serial PRIMARY KEY, title TEXT, words TEXT, times INT);")
        print("Finished creating table")

    # Insert some data into table
    def insert_news(self, da, ti, co):
        self.cursor.execute("INSERT INTO news (date, title, content) VALUES (%s, %s, %s);", (da, ti, co))

    def insert_keyword(self, title, word, times):
        self.cursor.execute("INSERT INTO keyword (title, words, times) VALUES (%s, %s, %s);", (title, word, times))

    # search all rows
    def search(self, table_name):
        self.cursor.execute("SELECT * FROM %s;" %table_name)
        rows = self.cursor.fetchall()
        for row in rows:
            print("(%s, %s, %s, %s)" % (str(row[0]), str(row[1]), str(row[2]), str(row[3])))

    def get_words(self, content, nums):
        word_list = jieba.analyse.extract_tags(content, topK=nums, withWeight=False)
        seglist = jieba.cut(content, cut_all=False)
        hash = {}
        times = []
        for item in seglist:
            if item in hash:
                hash[item] += 1
            else:
                hash[item] = 1
        for i in range(len(word_list)):
            times.append(hash['%s' % word_list[i]])
        return word_list, times

    def main(self):
        for i in range(int(self.file_num)):
            news = []
            with open('%s/%s' %(self.DIR, i), 'r') as saveFile:
                for x in saveFile:
                    if x != "\n":   # filter null
                        x = re.sub(r'\n', '', x)
                        news.append(x)

                try:    # filter no content
                    self.insert_news(news[0], news[1], news[2])
                except IndexError as e:
                    print("IndexError")
                else:
                    keywords = self.get_words(news[2], 10)
                    for j in range(len(keywords[0])):
                        self.insert_keyword(news[1], keywords[0][j], keywords[1][j])


if __name__ == '__main__':

    news = Upload()
    news.main()
    # Cleanup
    news.conn_inf.commit()
    news.cursor.close()
    news.conn_inf.close()
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-02-10 23:09:21
# Project: ourtmx


from pyspider.libs.base_handler import *
import MySQLdb as mysql

class Mysql():
    
    def __init__(self, host='localhost', username='root', password='123456', database='dictionary'):
        try:
            self.db = mysql.connect(host, username, password, database, charset="utf8")
            self.cursor = self.db.cursor()
        except mysql.DatabaseError as error:
            print error

    def insert_data(self, table_name, data):
        keys = ", ".join(data.keys())
        values = ", ".join(['%s'] * len(data))
        sql_query = "insert into %s (%s) values (%s)" % (table_name, keys, values)
        try:
            self.cursor.execute(sql_query, data.values())
            self.db.commit()
        except mysql.DatabaseError as error:
            print format(error)
            self.db.rollback()

            
class Handler(BaseHandler):
    base_url = "http://dj.iciba.com/"
    end_url = "-1.html"
    mydb = Mysql()
    crawl_config = {
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36',
        }
    }

    def on_start(self):
        f = open("/var/py/dictionary/dic.txt")
        line = f.readline()
        while line:
            word = line.split('→')[0]
            url = self.base_url + word + self.end_url
            print url
            self.crawl(url, callback=self.page_detail, save={'word': word})
            line = f.readline()
            
        f.close()
            
    
    def page_detail(self, response):
        word = response.save['word']
        print word
        for item in response.doc('#container1 > li').items():
            eng = item.find('.stc_en_txt')
            chn = item.find('.stc_cn_txt')
            english = eng.text().split('.')[1].lstrip()
            chinese = chn.text().replace(' ','')
            print word
            data = {
                'word': word,
                'english': english,
                'chinese': chinese,
            }
            yield data
       
                
                  
    def on_result(self, result):
        self.mydb.insert_data('ourtmx', result)
        
        
    
    
    
    
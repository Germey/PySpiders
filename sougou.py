# !/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-02-10 20:26:22
# Project: sougou


from pyspider.libs.base_handler import *
import MySQLdb as mysql
import time

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
    base_url = "http://www.bing.com/dict/partnerapi/search?pname=sogou&mkt=zh-cn&setlang=zh&form=SGDICT&q="
    mydb = Mysql()
    crawl_config = {
    }

    def on_start(self):
        f = open("/var/py/dictionary/dic.txt")
        line = f.readline()
        while line:
            word = line.split('→')[0]
            url = self.base_url + word
            self.crawl(url, callback=self.page_detail, save={'word': word})
            line = f.readline()
            
        f.close()
            
    
    def page_detail(self, response):
        word = response.save['word']
        for item in response.doc('#sentenceSeg .se_li').items():
            sen = item.find('.sen_en')
            cen = item.find('.sen_cn')
            english = sen.text()
            chinese = cen.text().replace(' ','')
            print word
            data = {
                'word': word,
                'english': english,
                'chinese': chinese,
            }
            yield data
       
                
                  
    def on_result(self, result):
        self.mydb.insert_data('sougou', result)
        
    
    
    
    
# -*- encoding: utf-8 -*-
# Created on 2016-02-10 00:13:34
# Project: cidu

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
    base_url = "http://www.dictall.com/dictall/result.jsp?cd=UTF-8&keyword="
    mydb = Mysql()
    crawl_config = {
    }

    def on_start(self):
        f = open("/var/py/dictionary/dic.txt")
        line = f.readline()
        while line:
            word = line.split('→')[0]
            url = self.base_url + word
            self.crawl(url, callback=self.detail_page, save={'word': word})
            line = f.readline()
            
        f.close()
            
            
    def detail_page(self, response):
        word = response.save['word']
        for item in response.doc('#catelist > div').items():
            source = item.find('.en > span:first').text().split(')')[1].strip()
            for sen in item.find('.en_sen').items():
                cen = sen.next()
                sen.find('script').remove()
                english = sen.text()
                chinese = cen.text()
                print source
                data = {
                    'word': word,
                    'source': source,
                    'english': english,
                    'chinese': chinese
                }
                yield data
                
                  
    def on_result(self, result):
        self.mydb.insert_data('cidu', result)
        
        
                

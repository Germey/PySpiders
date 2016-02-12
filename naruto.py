#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-02-11 01:02:50
# Project: naruto

from pyspider.libs.base_handler import *
from qiniu import Auth
from qiniu import put_data
import re
import urllib
import MySQLdb as mysql


class Mysql():
    
    def __init__(self, host='localhost', username='root', password='123456', database='naruto'):
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



class Qiniu:
    
    access_key = 'IOImn35KC5pRX7Ov3scxbYkvNk6oIxB7zWsBRp16'
    secret_key = 's29vc9tlCvs23wRh7QScYTuzCDmIbUSi4EroKj1z'
    bucket_name = 'naruto'
    def __init__(self):
        self.q = Auth(self.access_key, self.secret_key)
        self.mime_type = "image/jpg"
        self.tail = '.jpg'
        self.mydb = Mysql()
        
    def upload(self, url, key):
        key = key+self.tail
        u = urllib.urlopen(url)
        file = u.read()
        token = self.q.upload_token(self.bucket_name, key)
        ret, info = put_data(token, key, file, mime_type=self.mime_type, check_crc=True)
        del u,file
        return ret['key']

class Handler(BaseHandler):
    crawl_config = {
    }

    def __init__(self):
        self.qn = Qiniu()
        self.mydb = Mysql()
    
    def on_start(self):
        self.crawl('http://www.fzdm.com/manhua/001/', callback=self.index_page)

    def index_page(self, response):
        for each in response.doc('.pure-u-lg-1-4 > a').items():
            title = each.text()
            print title
            self.crawl(each.attr.href, callback=self.detail_page, save={'title': title})

    def detail_page(self, response):
        title = response.save['title']
        url = response.url
        image = response.doc('#mh li img')
        for link in response.doc('.navigation #mhona').items():
            print link.text()
            result = re.match(re.compile(r"\D+(\d+)\D+"), link.text().encode('utf-8', 'ignore'))
            if result:
                page = result.group(1)
        
        name =url.split('/')[-2]
        key = name + '_' + page
        file_name = self.qn.upload(image.attr.src, key)
        
        content = {
            'title': title,
            'name': name,
        }
        print content
        self.mydb.insert_data('content', content)
        image = {
            'name': name,
            'url': file_name,
            'page': page,
        }
        print image
        self.mydb.insert_data('image', image)
        
        for link in response.doc('.navigation #mhona').items():
            if link.text().encode('utf-8', 'ignore') == '下一页':
                self.crawl(link.attr.href, callback=self.detail_page, save={'title': title})
                
                
   
                
                
                
                
                
        

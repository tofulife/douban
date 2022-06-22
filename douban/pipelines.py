# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
from twisted.enterprise import adbapi
import requests
import os
import logging


class DoubanPipeline:


    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('bScore') and float(adapter.get('bScore') )> 8:
            return item




# 管道文件中一个管道类对应将一组数据存储到一个平台或者载体中
class mysqlPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool
   

    @classmethod
    def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
        """
        数据库建立连接
        :param settings: 配置参数
        :return: 实例化参数
        """
        adbparams = dict(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            cursorclass=pymysql.cursors.DictCursor  # 指定cursor类型
        )

        # 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
        dbpool = adbapi.ConnectionPool('pymysql', **adbparams)
        # 返回实例化参数
        return cls(dbpool)



    def process_item(self, item, spider):
        """
        使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
        """
        # cursor 在调用self.dbpool.runInteraction(self.do_insert, item)的时候 会自动传递过去
        query = self.dbpool.runInteraction(self.do_insert, item)  # 指定操作方法和操作数据

        # 添加异常处理
        query.addCallback(self.handle_error)  # 处理异常
 
    def do_insert(self, cursor, item):
        # 对数据库进行插入操作，并不需要commit，twisted会自动commit
        insert_sql = """
        insert into book(bId, bScore, bTitle, bDate) VALUES (%s,%s,%s,%s)
        """

        pic_path = '../images/book'
        if  self.check_duplicate(cursor, item) < 1:
            cursor.execute(insert_sql, (item['bId'], item['bScore'], item['bTitle'], item['bDate']))
            self.download_picture(item,pic_path)

        else:
            update_book= """update book set bScore=%s,bTitle=%s,bDate=%s where bId=%s"""
            cursor.execute(update_book, (item['bScore'], item['bTitle']+"22", item['bDate'],item['bId']))
            logging.info("update 成功")

    def check_duplicate(self, cursor,item):
        check_sql = """select bId,bTitle from book where bId=%s"""
        cursor.execute(check_sql, (item['bId']))
        num = cursor.rowcount
        logging.info("num 为：%s，bId为：%s"%(num,item['bId']))
        return num

    def download_picture(self,item,path):
        if not os.path.exists(path):
            os.makedirs(path)
        filename = item['bId']+".jpg"
        logging.info("下载图片%s连接为：%s"%(filename,item['bPicUrl']))
        resp = requests.get(item['bPicUrl'])
        if resp.status_code == 200:
            with open(f'../images/book/{filename}', 'wb') as file:
                file.write(resp.content)
            logging.info("下载图片成功")

        
 
    def handle_error(self, failure):
        if failure:
            # 打印错误信息
            print(failure)

            
    def open_spider(self, spider):
        logging.info('爬虫开始！')
        # truncate_sql = 'truncate table book'
        # self.dbpool.runOperation(truncate_sql)
        # print('数据库清空！！！')
        

    
    def close_spider(self, spider):
        self.dbpool.close()
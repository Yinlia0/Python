import requests
import mysql.connector
from lxml import etree
import datetime
import threading

'''
CREATE TABLE `xl720_fanzuiju_index` (
`id` INT ( 255 ) NOT NULL AUTO_INCREMENT,
`movie_title` VARCHAR ( 255 ) NOT NULL,
`movie_url` VARCHAR ( 255 ) NOT NULL,
`timestamp` datetime NOT NULL,
PRIMARY KEY ( `id` )
) ENGINE = INNODB AUTO_INCREMENT = 1861 DEFAULT CHARSET = utf8mb4;
'''

# 获取xl720影片页面地址

class Xl720:
    def __init__(self):
        self.url = 'https://www.xl720.com/category/fanzuipian/page/1'
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3745.4 Safari/537.36"}
        self.proxy = {
                "http": "http://127.0.0.1:7890",
                "https": "http://127.0.0.1:7890"
            }
        self.sql = mysql.connector.connect(host="127.0.0.1",
                                           port="3306",
                                           user="root",
                                           passwd="******",
                                           db="python")
        self.mysql = self.sql.cursor()

    def fanzui(self):
        r = requests.get(self.url, headers=self.headers, proxies=self.proxy).text
        index_html = etree.HTML(r)
        movie_title = index_html.xpath('//h3/a/@title')
        movie_url = index_html.xpath('//h3/a/@href')
        nextpostslink = index_html.xpath('//div/a[@class="nextpostslink"]/@href')
        if not len(nextpostslink):
            print('页面获取完成')
            return
        else:
            pass

        try:
            for i in range(len(movie_title)):
                title = movie_title[i]
                url = movie_url[i]
                url_sql = "select * from xl720_fanzuiju_index where movie_url='{}'".format(url)
                self.mysql.execute(url_sql)
                if self.mysql.fetchall():
                    print("跳过 {}".format(title))
                    continue
                else:
                    sql = "insert into xl720_fanzuiju_index (movie_title, movie_url, timestamp) values ('{}', '{}', '{}')".format(title, url, datetime.datetime.now())
                    print(title)
                    self.mysql.execute(sql)
            if nextpostslink[0] is not None:
                print(nextpostslink)
                self.url = nextpostslink[0]
                # for i in range(10):
                #     t = threading.Thread(target=self.fanzui)
                #     t.start()
                self.fanzui()
            else:
                print('无页面')
        except Exception as e:
            print(e)
        finally:
            self.sql.commit()

    def run(self):
        self.fanzui()

if __name__ == "__main__":
    xl = Xl720()
    xl.run()

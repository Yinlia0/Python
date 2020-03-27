import requests
import mysql.connector
from lxml import etree
import datetime

class Xl720:
    def __init__(self):
        self.url = 'https://www.xl720.com/category/fanzuipian/page/1'
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3745.4 Safari/537.36"}
        self.proxy = {
                "http": "http://127.0.0.1:7890"
            }
        self.sql = mysql.connector.connect(host="10.154.4.192",
                                           port="3310",
                                           user="root",
                                           passwd="pLgn3k38F7PBISPZ",
                                           db="python")
        self.mysql = self.sql.cursor()

    def fanzui(self):
        r = requests.get(self.url, headers=self.headers, proxies=self.proxy).text
        index_html = etree.HTML(r)
        movie_title = index_html.xpath('//h3/a/@title')
        movie_url = index_html.xpath('//h3/a/@href')

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
                self.mysql.execute(sql)
        self.sql.commit()


    def run(self):
        self.fanzui()

if __name__ == "__main__":
    xl = Xl720()
    xl.run()

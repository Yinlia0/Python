from xl720 import Xl720
import requests
import datetime
from lxml import etree

'''
CREATE TABLE `xl720_magnet_down` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title_name` varchar(255) NOT NULL,
  `magnet_url` varchar(255) NOT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
'''
# 配合 xl720.py 进行磁力地址保存

xl = Xl720()

def magnet_down():
    sql = "select movie_url from xl720_fanzuiju_index;"
    xl.mysql.execute(sql)
    try:
        for i in xl.mysql.fetchall():
            if i is None:
                break
            else:
                r = requests.get(url=i[0], headers=xl.headers, proxies=xl.proxy).text
                index_html = etree.HTML(r)
                title_name = index_html.xpath('//div[@id="zdownload"][1]/div[@class="down_btn down_btn_cl"]/a/@title')
                title_magnet = index_html.xpath('//div[@id="zdownload"][1]/div[@class="down_btn down_btn_cl"]/a/@href')
                title_name_sql = "select * from xl720_magnet_down where title_name='{}'".format(title_name[0])
                xl.mysql.execute(title_name_sql)

                if not len(title_magnet):
                    print('无磁力链接')
                    continue
                elif xl.mysql.fetchall():
                    print("跳过 {}".format(title_name[0]))
                    continue
                else:
                    sql = "insert into xl720_magnet_down (title_name, magnet_url, timestamp) value ('{}', '{}', '{}')".format(
                        title_name[0], title_magnet[0], datetime.datetime.now())
                    xl.mysql.execute(sql)
                    xl.sql.commit()
                    print(title_magnet[0], title_name[0])
    except Exception as e:
        print(e)
    finally:
        xl.sql.commit()


if __name__ == "__main__":
    magnet_down()

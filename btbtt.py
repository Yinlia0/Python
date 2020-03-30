import requests, re, os, time
from queue import Queue
from lxml import etree
from multiprocessing import Process
import threading

# bt之家 种子文件下载，使用队列
# 需要创建8bt目录

class Bbtt:

    # 类方法，初始化 构建通用参数
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36"}
        # self.start_url = 'http://www.88btbtt.com/thread-index-fid-950-tid-4427440.htm'
        self.start_url = 'http://www.88btbtt.com/thread-index-fid-950-tid-4496457.htm'
        self.proxies = {'http': 'http://127.0.0.1:7890'}
        # 定义 三个队列
        self.al_index_url = Queue()
        self.download_al_url = Queue()
        self.al_file_url = Queue()



    # 通过xpath 获取 索引页名称，网址
    def bt_index(self):
        print('bt_index')
        try:
            index_html = requests.get(self.start_url, headers=self.headers, proxies=self.proxies, timeout=6)
            html = etree.HTML(index_html.content.decode('utf-8'))
            a_arr = html.xpath("//tbody/tr/td[@valign='top']/a")
            print(a_arr)
            for a in a_arr:
                al_name = a.xpath(".//text()")[0]
                al_url = a.xpath(".//@href")[0]
                name = re.sub('[/·？！：.:?!~～]', '', al_name)
                print({'name': name, 'url': al_url})
                self.al_index_url.put({'name': name, 'url': al_url})
        except Exception as e:
            print(e)


    # 获取实际文件下载页，并合成字典 加入队列
    def file_url(self):
            print('file_url, %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
            while True:
                url = self.al_index_url.get()
                try:
                    al_index_html = requests.get(url['url'], headers=self.headers, proxies=self.proxies, timeout=6)
                except Exception as e:
                    print('获取实际文件地址出错 %s' % e)
                else:
                    html = etree.HTML(al_index_html.content.decode('utf-8'))
                    url_name = html.xpath("//div[@class='attachlist']/table[@class='noborder']/tr/td/a/@href")
                    for i in url_name:
                        http = 'http://www.btbtt.us/' + i
                        print({'name': url['name'], 'url': http})
                        self.download_al_url.put({'name': url['name'], 'url': http})
                    self.al_index_url.task_done()



    # 获取真实文件地址，合成字典 加入队列
    def download_file_url(self):
        print('download_file_url %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
        while True:
            url = self.download_al_url.get()
            try:
                index_html = requests.get(url['url'], headers=self.headers, timeout=6)
            except Exception as e:
                print('download_file_url %s' % e)
            else:
                html = etree.HTML(index_html.content.decode('utf-8'))
                url_name = html.xpath("//div[@class='width border bg1']/dl/dd/a/@href")
                file_name = str(html.xpath("//div[@class='width border bg1']/dl/dd[1]/text()")[0]).strip()
                http = 'http://www.btbtt.us/' + url_name[0]
                print({'name': url['name'], 'file_name': file_name, 'url': http})
                self.al_file_url.put({'name': url['name'], 'file_name': file_name, 'url': http})
                self.download_al_url.task_done()


    # 下载种子并保存
    def download_file(self):
        print('download_file %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
        while True:
            url = self.al_file_url.get()
            try:
                rsp = requests.get(url['url'], headers=self.headers, proxies=self.proxies, timeout=6)
            except Exception as e:
                print('download_file error %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
                time.sleep(3)
            else:
                file_dir = os.path.join(os.getcwd(), '8bt', url['name'])
                files_name = os.path.join(os.getcwd(), '8bt', url['name'], url['file_name'])
                if not os.path.exists(file_dir):
                    os.mkdir(file_dir)
                with open(files_name, 'wb') as f:
                    f.write(rsp.content)
                    f.close()
                print(files_name)
                self.al_file_url.task_done()

    def run(self):
        self.bt_index()
        thread_list = []
        t = threading.Thread(target=self.file_url)
        thread_list.append(t)
        for i in range(100):
            t1 = threading.Thread(target=self.download_file_url)
            thread_list.append(t1)
        for i in range(300):
            t2 = threading.Thread(target=self.download_file)
            thread_list.append(t2)
        for t in thread_list:
            # 把子线程设置为守护线程, 该线程不重要,主线程结束,子线程也结束
            t.setDaemon(True)
            t.start()
        for q in [self.al_index_url, self.download_al_url, self.al_file_url]:
            # 阻塞线程,等待队列任务完成
            q.join()
        print("执行完毕")



if __name__ == '__main__':
    btzhijia = Bbtt()
    btzhijia.run()

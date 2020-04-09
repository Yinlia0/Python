import requests
import os
import shutil
from download import download
from lxml import etree

# 下载leagueskin.net网站软件并解压到桌面skin目录，win
# http://leagueskin.net
# pip install six download requests tqdm

def leagueskin():
    url = 'http://leagueskin.net/p/download-mod-skin-2020-chn'
    html = requests.get(url).text
    skin_html = etree.HTML(html)
    result = skin_html.xpath('//a[@id="link_download3"]/@href')
    return result[0]

def skin_download(skin_url):
    desktop_dir = os.path.join(os.path.expanduser("~"), 'Desktop', 'skin')
    if os.path.exists(desktop_dir):
        print('删除skin目录')
        shutil.rmtree(desktop_dir)
    else:
        print('无skin目录，跳过删除')
    download(skin_url, desktop_dir, replace=True, kind="zip", progressbar=True)


if __name__ == '__main__':
    skin_download(leagueskin())

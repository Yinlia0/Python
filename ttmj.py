import asyncio, requests, re, os
from lxml import etree
from openpyxl import Workbook

# 协程获取美剧列表，并保存到excel


wb = Workbook()
ws = wb.active
ws.title = '美剧'
url = 'http://www.ttkmj.org/c/qhkh'
num = 1

async def qhkx(url):
    global num
    r = requests.get(url).text
    html = etree.HTML(r)
    title = html.xpath('//li[@class="subject-item"]/div[@class="info"]/h2/a')
    for i in title:
        name = i.xpath('./text()')[0]
        title_name = re.sub('[/·？！：.:?!~～\r\t\n 下载]', '', name)
        title_url = i.xpath('./@href')[0]
        print(title_name, title_url)
        ws.cell(row=num, column=1).value = title_name
        ws.cell(row=num, column=2).value = title_url
        num += 1
    # print('end')

    extend = html.xpath('//div[@class="paginator"]/ul[@class="pagelist"]/div[@class="page_navi"]/a[@href]/text()')[-2]
    next = html.xpath('//div[@class="paginator"]/ul[@class="pagelist"]/div[@class="page_navi"]/a/@href')[-2]

    if extend == ' 下一页 ':
        await qhkx(next)
    else:
        wb.save(os.path.join(os.path.expanduser("~"), 'Desktop', '美剧列表.xlsx'))
        pass

    async def main():
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(qhkx(url))]
        for task in tasks:
            await task

loop = asyncio.get_event_loop()
loop.run_until_complete(qhkx(url))

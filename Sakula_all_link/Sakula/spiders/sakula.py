import copy
import time
from urllib.parse import unquote
import scrapy
import scrapy.downloadermiddlewares.chunked
from Sakula.items import SakulaItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from redis import Redis

### 爬取某天的所有链接，添加redis,换用chrome
class SakulaSpider(scrapy.Spider):
    name = 'sakula'
    # allowed_domains = ['yhdmd.com']
    start_urls = ['https://www.yhdmp.net/']
    conn = Redis(host='127.0.0.1', port='6379')
    print(conn)
    def parse(self, response):
        week = input('选择周几：')
        n = int(week)
        ###主页每周列表的格式化
        table_xpath = '/html/body/div[8]/div[2]/div[1]/div[3]/ul[%d]/li'%n
        ###主页某日列表
        li_list = response.xpath(table_xpath)
        order = 1
        for li in li_list:
            title = li.xpath('./a/text()').extract_first()
            num = li.xpath('./span/a/text()').extract_first()
            item = SakulaItem()
            item['title'] = title
            print(title + ' 更新至' + num )
            m = int(order)
        ###对某日某漫画xpath进行格式化，提取出动漫名字
            ep_xpath = '/html/body/div[8]/div[2]/div[1]/div[3]/ul[%d]/li[%d]/a/text()' % (n, m)
        ###解析动漫名字
            ep_title = response.xpath(ep_xpath).extract_first()
        ###对某日某漫画xpath进行格式化，提取出动漫播放地址
            comic_link_xpath = '/html/body/div[8]/div[2]/div[1]/div[3]/ul[%d]/li[%d]/a/@href' % (n, m)
        ###解析动漫播放地址
            comic_link = 'https://www.yhdmp.net' + response.xpath(comic_link_xpath).extract_first()
            print(ep_title, comic_link)
            ###深度爬取
            yield scrapy.Request(url = comic_link,callback = self.parse_decs,meta = {'item':copy.deepcopy(item),'comic_link':comic_link},dont_filter=True)###dont_filter=True不知道要不要加
            order = order + 1
    def parse_decs(self,response):
        ### edge无头设置
        # driverfile_path = "msedgedriver.exe"
        # EDGE = {
        #     "browserName": "MicrosoftEdge",
        #     "version": "",
        #     "platform": "WINDOWS",
        #     "ms:edgeOptions": {
        #         'extensions': [],
        #         'args': [
        #             '--headless',
        #             '--disable-gpu',
        #             '--remote-debugging-port=9222',
        #         ]}
        # }
        ###chrome无头设置
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--proxy-server=http://152.136.62.181:9999')
        # proxy_arr = [
        #              # '--proxy-server=http://223.71.157.10:3128',
        #              # '--proxy-server=http://221.125.138.189:80',
        #              '--proxy-server=http://192.168.31.45:808',
        #              # '--proxy-server=http://122.9.101.6:8888',
        #              # '--proxy-server=http://106.54.128.253:999'
        #              ]
        # proxy = random.choice(proxy_arr)
        # print(proxy)
        # chrome_options.add_argument(proxy)
        ###动漫分集列表
        li_list = response.xpath('//*[@id="main0"]/div[2]/ul/li')
        ###数据解析
        a = 1 ###循环次数计数
        driver1 = webdriver.Chrome(chrome_options=chrome_options)
        for li in li_list:
            item = response.meta['item']
            comic_link = response.meta['comic_link']
            driver1.get(comic_link)
            time.sleep(2)
            driver1.find_element_by_xpath("//ul[@id = 'menu0']/li[text() = '播放列表2']").click()
            driver1.implicitly_wait(1)
            ep = li.xpath('./a/@title').extract_first()###详情页中每一集的名字
            comic_ep_link_xpath = '//*[@id="main0"]/div[2]/ul/li[%d]/a/@href'%a
            comic_ep_link = 'https://www.yhdmp.net' + response.xpath(comic_ep_link_xpath).extract_first()
            ### edge对象创建
            # driver1 = Edge(executable_path=driverfile_path, capabilities=EDGE)
            driver1.get(comic_ep_link)
            time.sleep(2)
            # driver1.find_element_by_xpath("//ul[@id = 'menu0']/li[text() = '播放列表2']").click()
            # driver1.implicitly_wait(1)
            video_ifram_link = driver1.find_element_by_xpath('/html//iframe').get_attribute("src")
            ###unqoute两次才能将超长url恢复，不知道为什么
            unquote1_link = unquote(video_ifram_link)
            unquote2_link = unquote(unquote1_link)
            print(unquote2_link)
            ex = 'https.*?url=(.*?)&getplay_url.*?r=0'
            video_download_link = re.findall(ex,unquote2_link,re.S)[0]
            ex = self.conn.sadd('video_urls',video_download_link)
            if ex == 1:
                print('新连接已识别，开始下载。。。')
                print('已完成', item['title'], ep, '链接获取')
                item['link'] = video_download_link
                item['num'] = ep
                yield item
            else:
                print('链接已存在，不进行数据更新')
            a = a + 1
        driver1.quit()
        pass







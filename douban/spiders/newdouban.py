import scrapy
from scrapy import Selector, Request
from scrapy.http import HtmlResponse

from douban.items import DoubanItem


class NewdoubanSpider(scrapy.Spider):
    name = 'newdouban'
    allowed_domains = ['movie.douban.com']
    # start_urls = ['https://book.douban.com/latest?subcat=%E5%85%A8%E9%83%A8&p=2']

    def start_requests(self):
        for page in range(1):
            yield Request(url=f'https://book.douban.com/latest?subcat=%E5%85%A8%E9%83%A8&p={page}')


    def parse(self, response: HtmlResponse):
        sel = Selector(response)
        movie_items = sel.css('#content > div>  div.article > ul.chart-dashed-list > li > div.media__body')
        for movie_sel in movie_items:
            item = DoubanItem()
            item['bTitle'] = movie_sel.css(' a::text').extract_first()
            item['bTime'] = movie_sel.css('p.subject-abstract::text').extract_first().replace(' ','').split('/')[1]
            item['bScore'] = movie_sel.css('span.color-red::text').extract_first()
            yield item

        


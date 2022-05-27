import scrapy
from scrapy import Selector, Request
from scrapy.http import HtmlResponse

from douban.items import DoubanItem


class NewdoubanSpider(scrapy.Spider):
    name = 'newdouban'
    allowed_domains = ['douban.com']
    # start_urls = ['https://book.douban.com/latest?subcat=%E5%85%A8%E9%83%A8&p=2']

    def start_requests(self):
        for page in range(19):
            yield Request(url=f'https://book.douban.com/latest?subcat=%E5%85%A8%E9%83%A8&p={page}')


    def parse(self, response: HtmlResponse):
        sel = Selector(response)
        book_items = sel.css('#content > div>  div.article > ul.chart-dashed-list > li > div.media__body')
        for book_sel in book_items:
            # item = DoubanItem()
            # item['bTitle'] = book_sel.css(' a::text').extract_first()
            # item['bId'] = book_sel.css('a::attr(href)').extract_first().split('/')[-2]
            bDate = book_sel.css('p.subject-abstract::text').extract_first().replace(' ','').split('/')[-4]
            bScore= book_sel.css('span.color-red::text').extract_first()
            Detailurl = book_sel.css('a::attr(href)').extract_first()
            if bScore:
                yield scrapy.Request(url=Detailurl,callback=self.parse_bookDetail,meta={'bDate':bDate,'bScore':bScore})


            
    def parse_bookDetail(self, response: HtmlResponse):
        sel = Selector(response)
        item = DoubanItem()
        item['bTitle'] = self.str_format(sel.css('#wrapper h1 span::text').extract_first())
        item['bDate']= self.str_format(response.meta['bDate'])
        item['bScore'] = self.str_format(response.meta['bScore'])
        item['bId'] = self.str_format(response.url.split('/')[-2])
        yield item

    def str_format(self,str):
        return str.replace(' ','')
    



    


        


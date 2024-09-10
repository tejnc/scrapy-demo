import scrapy
from scrapy.loader import ItemLoader

from demo.items import DemoItem


class DemoSpider(scrapy.Spider):
    name = 'demo-crawler'

    def start_requests(self):
        self.start_url = 'https://books.toscrape.com'
        yield scrapy.Request(
            url=self.start_url,
            callback=self.parse,
        )
    
    def parse(self, response):
        articles = response.xpath("//article[@class='product_pod']")
        for article in articles:
            loader = ItemLoader(item=DemoItem(), selector=article)
            loader.add_xpath('title', './h3/a/text()')
            loader.add_xpath('price','./div[@class="product_price"]/p[@class="price_color"]/text()')
            loader.add_xpath('availability', './div[@class="product_price"]/p[@class="instock availability"]/text()')
            loader.add_xpath('image_src', './div[@class="image_container"]/a/img/@src')
            loader.add_xpath('rating', './p/@class')

            book_details = loader.load_item()
            details_page:str = article.xpath('./h3/a/@href').get()

            page_url = 'https://books.toscrape.com/'  + details_page if details_page.__contains__('catalogue') else 'https://books.toscrape.com/' + 'catalogue/' + details_page
            yield scrapy.Request(
                url=page_url,
                callback=self.parse_details,
                meta= {
                    'book_details': book_details,
                }
            )

        next_page = response.xpath('//a[text()="next"]/@href').get()
        if next_page is not None:
            next_url = 'https://books.toscrape.com/' + next_page
            print("next_page", next_url)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
            )

    def parse_details(self, response):
        book_details = response.request.meta['book_details']
        loader = ItemLoader(item=DemoItem(), selector=response)
        loader.add_xpath('description', './/div[@id="product_description"]/following-sibling::p/text()')
        
        page_details = loader.load_item()
        book_details.update(page_details)
        yield book_details

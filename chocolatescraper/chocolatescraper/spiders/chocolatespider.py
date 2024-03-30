import scrapy
from chocolatescraper.items import ChocolatescraperItem
from chocolatescraper.itemloaders import ChocolatescraperLoader as Loader


class ChocolatespiderSpider(scrapy.Spider):
    name = "chocolatespider"
    allowed_domains = ["chocolate.co.uk"]
    start_urls = ["https://www.chocolate.co.uk/collections/all"]

    def parse(self, response):
        products = get_products(response)

        for product in products:
            chocolate = Loader(item=ChocolatescraperItem(), selector=product)

            chocolate.add_css('name', 'a.product-item-meta__title::text')
            chocolate.add_css('price', 'span.price')
            chocolate.add_css(
                'url', 'div.product-item__image-wrapper a::attr(href)')

            yield chocolate.load_item()

        next_page = get_next_page(response)

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


def get_products(response):
    return response.css('product-item.product-item')


def get_next_page(response):
    return response.css('nav.pagination__nav a.pagination__nav-item[rel=next]::attr("href")').get()

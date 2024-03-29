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
            # chocolate.add_css(
            #     'price', 'span.price', re='<span class="price">\n              <span class="visually-hidden">Sale price</span>(.*)</span>')
            chocolate.add_css(
                'url', 'div.product-item__image-wrapper a::attr(href)')

            yield chocolate.load_item()

        next_page = get_next_page(response)

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


def get_products(response):
    return response.css('product-item.product-item')


def get_name_css():
    return 'a.product-item-meta__title::text'


def get_price(product):
    price = product.css('span.price').get().replace(
        '<span class="price">\n              <span class="visually-hidden">Sale price</span>', '').replace('</span>', '').replace('<span class=\"price price--highlight\">\n              <span class=\"visually-hidden\">Sale price', '').replace('<span class=\"price\">\n                <span class=\"visually-hidden\">Sale price', '').replace('From ', '').replace('\n', '')

    return price


def get_url(product):
    return product.css('div.product-item__image-wrapper a').attrib['href']


def get_next_page(response):
    return response.css('nav.pagination__nav a.pagination__nav-item[rel=next]::attr("href")').get()

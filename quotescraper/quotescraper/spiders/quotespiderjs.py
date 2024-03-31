from typing import Any
import scrapy
from quotescraper.items import QuotescraperItem
from scrapy_playwright.page import PageMethod


class QuotespiderjsSpider(scrapy.Spider):
    name = "quotespiderjs"

    def __init__(self):
        self.meta_request = {
            'playwright': True,
            'playwright_include_page': True,
            'playwright_page_methods': [PageMethod('wait_for_selector', 'div.quote')],
            'errback': self.errback
        }

    def start_requests(self):
        url = "https://quotes.toscrape.com/js/"
        yield scrapy.Request(url, meta=self.meta_request)

    async def parse(self, response):
        page = response.meta['playwright_page']
        await page.close()

        quotes = response.css('div.quote')

        for quote in quotes:
            item = QuotescraperItem()

            item['text'] = quote.css('span.text::text').get()
            item['author'] = quote.css('small.author::text').get()
            item['tags'] = quote.css('a.tag::text').getall()

            yield item

        next_page_link = response.css('li.next > a::attr(href)').get()

        if next_page_link is not None:
            yield response.follow(next_page_link, callback=self.parse, meta=self.meta_request)

    async def errback(self, failure):
        page = failure.request.meta['playwright_page']

        await page.close()

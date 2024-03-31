import scrapy
from scrapy_playwright.page import PageMethod
from quotescraper.items import QuotescraperItem


class QuotespiderscrollSpider(scrapy.Spider):
    name = "quotespiderscroll"

    def __init__(self):
        self.meta_request = {
            'playwright': True,
            'playwright_include_page': True,
            'playwright_page_methods': [
                PageMethod('wait_for_selector', 'div.quote'),
                PageMethod(
                    "evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                PageMethod(
                    # 10 per page
                    'wait_for_selector', 'div.quote:nth-child(11)')
            ],
            'errback': self.errback
        }

    def start_requests(self):
        url = "https://quotes.toscrape.com/scroll"
        yield scrapy.Request(url, meta=self.meta_request)

    async def parse(self, response):
        page = response.meta['playwright_page']

        # Take Screenshot
        await page.screenshot(path='example.png', full_page=True)

        await page.close()

        quotes = response.css('div.quote')

        for quote in quotes:
            item = QuotescraperItem()

            item['text'] = quote.css('span.text::text').get()
            item['author'] = quote.css('small.author::text').get()
            item['tags'] = quote.css('div.tags a.tag::text').getall()

            yield item

    async def errback(self, failure):
        page = failure.request.meta['playwright_page']
        await page.close()

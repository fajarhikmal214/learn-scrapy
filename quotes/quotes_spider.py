import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'https://quotes.toscrape.com/tag/humor/'
    ]

    def parse(self, response):
        quotes = response.css('div.quote')

        for quote in quotes:
            author = quote.css("small.author::text").get()
            text = quote.css("span.text::text").get()

            yield {
                author: author,
                text: text
            }

        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

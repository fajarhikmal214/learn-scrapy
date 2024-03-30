from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


class ChocolatescraperLoader(ItemLoader):

    default_output_processor = TakeFirst()

    url_in = MapCompose(lambda x: 'https://www.chocolate.co.uk' + x)

    raw_price_out = TakeFirst()
    price_in = MapCompose(
        lambda x: x.replace(
            '<span class="price">\n              <span class="visually-hidden">Sale price</span>', ''),
        lambda x: x.replace('</span>', ''),
        lambda x: x.replace(
            '<span class=\"price price--highlight\">\n              <span class=\"visually-hidden\">Sale price', ''),
        lambda x: x.replace(
            '<span class=\"price\">\n                <span class=\"visually-hidden\">Sale price', ''),
        lambda x: x.replace('From ', ''),
        lambda x: x.replace('\n', ''),
        lambda x: x.split('£')[-1]
    )

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
from dotenv import load_dotenv

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from mysql import connector as mysqlConn

load_dotenv()


class ChocolatescraperPipeline:
    def process_item(self, item, spider):
        return item


class PriceToUSDPipeline:
    gbpToUsdRate = 1.3

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('price'):
            floatPrice = float(adapter['price'])

            adapter['price'] = round(floatPrice * self.gbpToUsdRate, 2)
            return item
        else:
            raise DropItem(f"Missing price in {item}")


class DuplicatesPipeline:
    def __init__(self):
        self.name_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter['name'] in self.name_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.name_seen.add(adapter['name'])
            return item


class SavingToMysqlPipeline:
    def __init__(self):
        self.create_connection()

    def create_connection(self):
        self.connection = mysqlConn.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            port=os.getenv('MYSQL_PORT'),
            database=os.getenv('MYSQL_DATABASE')
        )

        self.curr = self.connection.cursor()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        sql = "INSERT INTO products (name, price, url) VALUES (%s, %s, %s)"
        val = (adapter['name'], adapter['price'], adapter['url'])

        self.curr.execute(sql, val)
        self.connection.commit()

        return item

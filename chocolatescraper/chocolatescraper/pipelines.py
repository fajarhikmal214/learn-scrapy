# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import io
import os
import json
import time

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from mysql import connector as mysqlConn

from minio import Minio
from minio.error import InvalidResponseError

from dotenv import load_dotenv
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


class MinioPipeline:
    def __init__(self):
        self.access_key = os.getenv('MINIO_ACCESS_KEY')
        self.secret_key = os.getenv('MINIO_SECRET_KEY')
        self.endpoint = os.getenv('MINIO_ENDPOINT')
        self.bucket_name = os.getenv('MINIO_BUCKET_NAME')

    def open_spider(self, spider):
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False
        )

        self.json_data_dump = []

    def process_item(self, item, spider):
        # Add processed row to the list
        self.json_data_dump.append(dict(item))

        return item

    def close_spider(self, spider):
        # Convert JSON data to string
        json_data = json.dumps(self.json_data_dump, indent=4)

        # Convert string to bytes
        data = json_data.encode('utf-8')

        # Create BytesIO object
        data_stream = io.BytesIO(data)

        filename = "%(name)s_%(time)s.json" % {
            "name": "chocolatescraper",
            "time": time.strftime("%Y%m%d%H%M%S")
        }

        try:
            self.client.put_object(
                self.bucket_name,
                object_name=filename,
                data=data_stream,
                length=len(data)
            )
        except InvalidResponseError as err:
            spider.logger.error(f"Failed to upload item to MinIO: {err}")

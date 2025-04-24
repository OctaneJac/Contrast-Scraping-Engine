import os
from pymongo import MongoClient
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """This method is used by Scrapy to instantiate the pipeline"""
        # Access environment variables for MongoDB credentials
        mongo_uri = os.getenv('MONGO_URI')  # Load Mongo URI from .env file
        mongo_db = os.getenv('MONGO_DB')  # Load DB name from .env file
        mongo_collection = os.getenv('MONGO_COLLECTION')  # Load collection name from .env file
        
        # Return an instance of the pipeline
        return cls(mongo_uri, mongo_db, mongo_collection)

    def open_spider(self, spider):
        """Open the MongoDB connection"""
        # Establish MongoDB connection using environment variables
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]

    def close_spider(self, spider):
        """Close the MongoDB connection when spider finishes"""
        self.client.close()

    def process_item(self, item, spider):
        """Process the item and insert or update it in MongoDB"""
        try:
            # Insert or update the product in MongoDB
            self.collection.update_one(
                {'url': item['url']}, {'$set': item}, upsert=True
            )
            spider.log(f"Upserted product: {item['name']}", level=logging.INFO)
        except Exception as e:
            spider.log(f"Error upserting product: {e}", level=logging.ERROR)
        return item

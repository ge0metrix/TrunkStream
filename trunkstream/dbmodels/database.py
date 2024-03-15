import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()

uri = os.environ.get("TS_MONGOURL", "")

# Create a new client and connect to the server
client = MongoClient(uri)
db = client.TrunkStream
collection = db["Calls"]

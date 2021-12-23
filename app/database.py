import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

client = motor.motor_asyncio.AsyncIOMotorClient(f"{os.getenv('MONGO_URI')}")

db = client.listing_service

from fastapi import FastAPI
from routes import listing

app = FastAPI()

app.include_router(listing.router)

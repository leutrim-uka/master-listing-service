from fastapi import APIRouter, status, HTTPException, Request, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional
import requests

from models.listing import ListingRequest, ResponseModel
from database import db
from utils import generate_listing_id, calculate_page_data, generate_pages_links, log_event

router = APIRouter()


@router.post("/", response_description="Listing request added to the database")
def add_listing_request(listing_request: ListingRequest, background_tasks: BackgroundTasks):
    listing_id = generate_listing_id()

    background_tasks.add_task(manage_listing_request, listing_request, listing_id)

    return f"Listing request with ID {listing_id} is now processing!"


async def manage_listing_request(listing_request: ListingRequest, listing_id: str):
    listing = jsonable_encoder(listing_request)
    listing["listing_id"] = listing_id

    try:
        new_listing = await db["listings"].insert_one(listing)
        created_listing = await db["listings"].find_one({"_id": new_listing.inserted_id})
        await log_event(db, listing_id, "Listing request stored into database")
    except Exception as e:
        message = f"Error while storing listing request: {e}"
        await log_event(db, listing_id, message)

    try:
        await log_event(db, listing_id, "Sent for mapping")
        requests.post(
            f"http://127.0.0.1:8007/{listing_id}",
        )
    except Exception as e:
        message = f"Error: Mapping request couldn't be sent: {e}"
        await log_event(db, listing_id, message)
        return message


@router.get("/marketplaces")
async def get_listing_request():
    marketplaces = await db["marketplaces"].find({}, {"_id": 0}).to_list(5)

    if not marketplaces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Marketplace not found"
        )

    return marketplaces


@router.get("/{listing_id}", response_description="List all listing requests")
async def get_listing_request(listing_id: str):
    listing_request = await db["listings"].find({"listing_id": listing_id}, {"_id": 0, "credentials": 0}).to_list(10)

    if listing_request:
        return ResponseModel(listing_request, "Listing retrieved successfully!")
    return ResponseModel(listing_request, "No listing request found with this ID!")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_listing_requests(
    request: Request,
    page: Optional[str] = Query("1", regex="^[1-9]\d*$"),
    size: Optional[str] = Query("20", regex="^[1-9]\d*$"),
):

    page = int(page)
    size = int(size)

    # get row count of the 'listings' table
    total_elements = await db["listings"].count_documents({})

    skip = (page - 1) * size
    listings = await db["listings"].find({}, {"_id": 0, "credentials": 0}).skip(skip).limit(size).to_list(size)

    cur_page_size = len(listings) if listings is not None else 1
    print(cur_page_size)

    page_data = calculate_page_data(page, size, cur_page_size, total_elements)
    pages_links = generate_pages_links(
        str(request.url), page, size, total_elements, page_data["total_pages"]
    )

    if not listings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No listings found!"
        )

    return {
        "page_data": page_data,
        "pages_links": pages_links,
        "listing_requests": listings,
    }


@router.delete("/{listing_id}", response_description="Delete a listing request")
async def delete_listing(listing_id: str):

    # IMPLEMENT DELETE METHOD
    pass

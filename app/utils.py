import uuid
import math
import re


def generate_listing_id():
    return str(uuid.uuid4())


def generate_pages_links(request_url, page, size, total_elements, total_pages):
    prev_page = 1 if page <= 1 else page - 1
    next_page = (
        math.ceil(total_elements / float(size))
        if page >= total_elements / float(size)
        else int(page) + 1
    )

    page = 1 if page < 1 else page

    return {
        "first": update_query_string_parameter(request_url, 1, size),
        "prev": update_query_string_parameter(request_url, prev_page, size),
        "self": update_query_string_parameter(request_url, page, size),
        "next": update_query_string_parameter(request_url, next_page, size),
        "last": update_query_string_parameter(request_url, total_pages, size),
    }


def calculate_page_data(page, size, cur_page_size, total_elements):
    page_size = size
    if page_size > 0:
        total_pages = (
            1
            if total_elements < page_size
            else math.ceil(total_elements / float(page_size))
        )
    else:
        total_pages = 0
    active_page = page

    return {
        "size": cur_page_size,
        "total_elements": total_elements,
        "total_pages": total_pages,
        "current_page": active_page,
        "has_next_page": active_page < total_pages,
    }


def update_query_string_parameter(uri, page, size):
    base_url = uri.split("?")[0] if "?" in uri else uri
    url = f"{base_url}?page={page}&size={size}"
    return url


def get_marketplace_name_from_id(db, relation, marketplace_id):
    return db.query(relation.name).filter(relation.id == marketplace_id).first().name


async def update_listing_status(db, listing_id, status):
    await db["listings"].update_one({"listing_id": listing_id}, {"$set": {"status": status}})
    updated_document = await db["listings"].find({"$and": [
        {"listing_id": listing_id},
        {"status": status}]},
        {"listing_id": 1, "status": 1, "_id": 0})

    return updated_document


async def log_event(db, listing_id, message):
    await db["listings"].update_one({"listing_id": listing_id}, {"$push": {"events": message}})
    return "Event logged"


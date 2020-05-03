import os
import logging
from algoliasearch.search_client import SearchClient
from utils import extract_domain

client = SearchClient.create(os.environ["ALGOLIA_APP_ID"], os.environ["ALGOLIA_API_KEY"])
index = client.init_index("prod_businesses")


def get_domains():
    for hit in index.browse_objects():
        urls = set()
        for key in (
            "gift-card-link",
            "online-store-link",
            "online-order-link",
            "order-groceries-link",
            "donations-link",
            "website",
        ):
            value = hit.get(key)
            if value:
                urls.add(value)

        yield {"urls": urls, "object_id": hit["objectID"], "name": hit["name"]}


def save_keywords(keywords_by_object_id):
    logging.warning(f"Starting save to index")
    partial_objects = [{"objectID": key, "scrapedKeywords": list(value)} for (key, value) in keywords_by_object_id.items()]
    resp = index.partial_update_objects(partial_objects, {"createIfNotExists": False})
    logging.warning(f"Saved scraped keywords {len(partial_objects)}")

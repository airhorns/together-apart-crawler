import logging
from twisted.internet import reactor, defer
from collections import defaultdict
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.log import configure_logging
from dragnet import extract_content
import yake
from utils import extract_domain
from backend import get_domains, save_keywords


class Content(scrapy.Item):
    object_id = scrapy.Field()
    content = scrapy.Field()


class KeywordSpider(CrawlSpider):
    name = "keyword"

    rules = (
        Rule(
            LinkExtractor(
                allow=(".*",),
                deny_domains=(
                    "ubereats.com",
                    "facebook.com",
                    "instagram.com",
                    "twitter.com",
                    "justeat.ca",
                    "skipthedishes.com",
                    "instacart.com",
                    "paypal.me",
                    "rogers.com",
                    "squareup.com",
                    "etsy.com",
                    "gofundme.com",
                    "onlinefoodorders.ca",
                ),
            ),
            callback="parse_keywords",
        ),
    )

    custom_settings = {"ROBOTSTXT_OBEY": True, "DEPTH_LIMIT": 3, "CLOSESPIDER_PAGECOUNT": 20}

    def __init__(self, start_urls, object_id, *args, **kwargs):
        super(KeywordSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.object_id = object_id
        self.allowed_domains = [domain for domain in set(map(extract_domain, start_urls)) if domain]

    def parse_keywords(self, response):
        item = Content()
        item["object_id"] = self.object_id
        item["content"] = extract_content(response.body)
        return item


class KeywordsPipeline:
    keywords = defaultdict(set)
    kw_extractor = yake.KeywordExtractor(lan="en", top=30)

    @staticmethod
    def reset():
        KeywordsPipeline.keywords = defaultdict(set)

    def process_item(self, item, spider):
        if item["content"] and len(item["content"]) > 0:
            keywords = KeywordsPipeline.kw_extractor.extract_keywords(item["content"])
            for (_score, keyword) in keywords:
                KeywordsPipeline.keywords[item["object_id"]].add(keyword)

        return item


configure_logging({"LOG_LEVEL": "WARN"})
runner = CrawlerRunner({"LOG_LEVEL": "WARN", "ITEM_PIPELINES": {"__main__.KeywordsPipeline": 100}})
domains = list(get_domains())


@defer.inlineCallbacks
def crawl():
    for domain in domains:
        yield runner.crawl(KeywordSpider, object_id=domain["object_id"], start_urls=domain["urls"])
        logging.warning(f"Processed {domain['name']} (ID {domain['object_id']})")

        if len(KeywordsPipeline.keywords) > 100:
            save_keywords(KeywordsPipeline.keywords)
            KeywordsPipeline.reset()

    save_keywords(KeywordsPipeline.keywords)
    reactor.stop()


crawl()
reactor.run()
logging.warning("Completed scrape")

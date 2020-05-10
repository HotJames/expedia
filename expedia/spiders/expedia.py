# -*- coding:utf-8 -*-
# @Author: james
# @Date: 2020-05-09
# @File: expedia.py
# @Software: PyCharm

import json
import logging
import re
from urlparse import urljoin

from scrapy import Request, Spider

from ..items import ExpediaItem
from csvwriter import CSVDumper

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def unicode_body(response):
    if isinstance(response.body, str):
        return response.body
    try:
        return response.body_as_unicode()
    except:
        try:
            return response.body.decode(response.encoding)
        except:
            raise Exception("Cannot convert response body to unicode!")


class Expedia(Spider):
    name = "expedia"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        # "EXTENSIONS": {
        #     'scrapy.telnet.TelnetConsole': None,
        # }
    }

    headers = {
        "referer": "https://www.expedia.com/Tokyo-Hotels.d179900.Travel-Guide-Hotels",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
    }

    start_url = "https://www.expedia.com/Hotel-Search?rfrrid=TG.LP.Hotels.Hotel&startDate=5%2F10%2F2020&endDate=5" \
                "%2F11%2F2020&regionId=179900"

    dumper = CSVDumper("data.csv")

    def start_requests(self):
        yield Request(url=self.start_url, headers=self.headers, callback=self.parse_list)

    def parse_list(self, response):
        body = unicode_body(response)

        data1 = re.search("window.__STATE__ = JSON.parse\((\"{.*}\")", body).group(1)

        data2 = json.loads(json.loads(data1))

        list_hotel = data2["searchResults"]["propertySearchListings"]

        logger.info("Get %d hotels in list ---" % len(list_hotel))

        for info in list_hotel:
            if info.get("resultType") == "HOTEL":
                item = ExpediaItem()
                try:
                    item["hotel_name"] = info["model"]["hotelName"]
                    item["hotel_id"] = info["model"]["hotelId"]
                    item["display_price"] = info["model"]["displayPrice"]
                    item["local"] = info["model"]["neighborhood"]
                    item["available_offer"] = info["model"]["hasAvailableOffer"]
                    rev = info["model"].get("reviews")
                    if rev:
                        item["reviews_count"] = rev["count"]
                        item["reviews_rate"] = rev["overallRating"]
                    else:
                        item["reviews_count"] = ""
                        item["reviews_rate"] = ""
                    item["url"] = urljoin("https://www.expedia.com/", info["model"]["infositeUrl"])
                    yield Request(item["url"], headers=self.headers, callback=self.parse_detail, meta={"item": item})
                except Exception as e:
                    logger.error("Err: %s" % e)
                    print info

            else:
                logger.info("Not a hotel in list ---")

    def parse_detail(self, response):
        item = response.meta["item"]

        body = unicode_body(response)

        data1 = re.search("window.__STATE__ = JSON.parse\((\"{.*}\")", body).group(1)

        data2 = json.loads(json.loads(data1))

        room_list = data2["currentHotel"]["offers"]["rooms"]

        logger.info("Hotel %s has room %d" % (item["hotel_id"], len(room_list)))

        room_data = []

        for info in room_list:
            room_data.append({info["name"]: info["ratePlans"][0]["price"] if len(info["ratePlans"]) > 0 else ""})

        item["room_price"] = room_data

        self.dumper.process_item(item)
        logger.info("SUCCESS GET A HOTEL %s" % item["hotel_id"])

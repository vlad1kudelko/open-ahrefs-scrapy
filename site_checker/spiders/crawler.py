import datetime
from urllib.parse import urlparse

import scrapy
from scrapy_redis.spiders import RedisSpider
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from site_checker.items import SiteCheckerItem


class MyCrawler(RedisSpider):
    name = "crawler"
    redis_key = "crawler:start_urls"

    def make_request_from_data(self, data):
        link = data.decode("utf-8")
        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S%f")
        return [
            scrapy.Request(
                link,
                callback=self.parse,
                errback=self.handle_error,
                meta={
                    "dont_retry": True,
                    "task": f"{timestamp}:{link}",
                },
            )
        ]

    def parse(self, response):
        # 0. Начальная проверка страницы
        isHTML = "text/html" in str(response.headers.get("Content-Type", b""))
        # 1. Создаем Item для текущей страницы
        item = SiteCheckerItem()
        item["url"] = response.url
        item["status"] = response.status
        item["title"] = response.css("title::text").get() if isHTML else None
        item["redirect_urls"] = response.meta.get("redirect_urls", [])
        item["referer"] = response.meta.get("prev_url", "")
        item["task"] = response.meta.get("task", None)
        yield item
        # 2. Если сейчас стоим на странице с нашим целевым доменом
        task = response.meta.get("task")
        target_domain = response.meta.get("target_domain")
        if not target_domain:
            target_domain = urlparse(response.url).netloc
        current_domain = urlparse(response.url).netloc
        if target_domain == current_domain and isHTML:
            # 3. Ищем ссылки для перехода дальше
            for link in response.css("a::attr(href)").getall():
                try:
                    yield response.follow(
                        link,
                        callback=self.parse,
                        errback=self.handle_error,
                        meta={
                            "dont_retry": True,
                            "task": task,
                            "target_domain": target_domain,
                            "prev_url": response.url,
                        },
                    )
                except ValueError as e:
                    yield {
                        "url": link,
                        "status": 888,
                        "title": f"Error: {str(e)}",
                        "redirect_urls": [],
                        "referer": response.url,
                        "task": task,
                    }

    def handle_error(self, failure):
        item = SiteCheckerItem()
        item["url"] = failure.request.url
        item["status"] = 999
        if failure.check(DNSLookupError):
            item["title"] = "Error: DNS Lookup Failed"
        elif failure.check(TCPTimedOutError):
            item["title"] = "Error: Connection Timeout"
        else:
            item["title"] = f"Error: {failure.getErrorMessage()}"
        item["redirect_urls"] = failure.request.meta.get("redirect_urls", [])
        item["referer"] = failure.request.meta.get("prev_url", "")
        item["task"] = failure.request.meta.get("task", None)
        yield item

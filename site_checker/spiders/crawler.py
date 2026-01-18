from urllib.parse import urlparse

from scrapy_redis.spiders import RedisSpider

from site_checker.items import SiteCheckerItem


class MyCrawler(RedisSpider):
    name = "crawler"
    redis_key = "crawler:start_urls"

    def parse(self, response):
        # 0. Начальная проверка страницы
        isHTML = "text/html" in str(response.headers.get("Content-Type", b""))

        # 1. Создаем Item для текущей страницы
        item = SiteCheckerItem()
        item["url"] = response.url
        item["status"] = response.status
        item["title"] = response.css("title::text").get() if isHTML else None
        item["redirect_times"] = response.meta.get("redirect_times", 0)
        item["redirect_urls"] = response.meta.get("redirect_urls", [])
        item["referer"] = response.meta.get("prev_url", "")
        yield item

        # 2. Если сейчас стоим на странице с нашим целевым доменом
        target_domain = response.meta.get("target_domain")
        if not target_domain:
            target_domain = urlparse(response.url).netloc
        current_domain = urlparse(response.url).netloc
        if target_domain == current_domain and isHTML:
            # 3. Ищем ссылки для перехода дальше
            for link in response.css("a::attr(href)").getall():
                yield response.follow(
                    link,
                    callback=self.parse,
                    meta={"target_domain": target_domain, "prev_url": response.url},
                )

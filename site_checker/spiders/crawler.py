from scrapy_redis.spiders import RedisSpider

from site_checker.items import SiteCheckerItem


class MyCrawler(RedisSpider):
    name = "crawler"
    redis_key = "crawler:start_urls"

    def parse(self, response):
        # 1. Создаем Item для текущей страницы
        item = SiteCheckerItem()
        item["url"] = response.url
        item["status"] = response.status
        item["title"] = response.css("title::text").get()
        item["redirect_times"] = response.meta.get("redirect_times", 0)
        item["redirect_urls"] = response.meta.get("redirect_urls", [])
        item["referer"] = response.meta.get("prev_url", "")
        yield item

        # 2. Ищем ссылки для перехода дальше
        for link in response.css("a::attr(href)").getall():
            yield response.follow(
                link, callback=self.parse, meta={"prev_url": response.url}
            )

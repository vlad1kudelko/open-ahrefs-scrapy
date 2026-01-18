import scrapy


class SiteCheckerItem(scrapy.Item):
    url = scrapy.Field()
    status = scrapy.Field()  # 200, 404, 500 и т.д.
    title = scrapy.Field()
    redirect_urls = scrapy.Field()  # Список URL в цепочке редиректов
    referer = scrapy.Field()  # Для отслеживания связей (откуда пришли)
    task = scrapy.Field()  # 20260118060512987654:https://example.com/404

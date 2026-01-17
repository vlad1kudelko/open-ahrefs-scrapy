import scrapy


class SiteCheckerItem(scrapy.Item):
    url = scrapy.Field()
    status = scrapy.Field()  # 200, 404, 500 и т.д.
    title = scrapy.Field()
    redirect_times = scrapy.Field()  # Сколько редиректов было пройдено
    redirect_urls = scrapy.Field()  # Список URL в цепочке редиректов
    referer = scrapy.Field()  # Для отслеживания связей (откуда пришли)

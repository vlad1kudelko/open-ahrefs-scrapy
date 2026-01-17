import os

BOT_NAME = "site_checker"
SPIDER_MODULES = ["site_checker.spiders"]
NEWSPIDER_MODULE = "site_checker.spiders"

# Допустимые уровни: CRITICAL, ERROR, WARNING, INFO, DEBUG
LOG_LEVEL = "WARNING"

# Включаем все типы ответов (404, 500 и др.)
HTTPERROR_ALLOW_ALL = True

# 1. Имитация Google-бота
USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
ROBOTSTXT_OBEY = True  # Google всегда слушается robots.txt

# 2. Интеграция с Redis (scrapy-redis)
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SCHEDULER_PERSIST = True  # Не очищать очередь при выходе

# 3. Настройки производительности и вежливости
CONCURRENT_REQUESTS = 16  # Не стоит ставить слишком много, чтобы не забанили
DOWNLOAD_DELAY = 0.5  # Задержка 500мс (как у вежливого бота)
COOKIES_ENABLED = False  # Ботам обычно не нужны куки

# 4. Включаем наш будущий Pipeline
ITEM_PIPELINES = {
    "scrapy_redis.pipelines.RedisPipeline": 300,
    #  "site_checker.pipelines.SiteCheckerPipeline": 300,
}

# 5. Глубина обхода
DEPTH_LIMIT = 50  # Чтобы не уйти в бесконечные циклы
DEPTH_PRIORITY = 1  # Обход в ширину (BFS) - лучше для SEO аудита
SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"

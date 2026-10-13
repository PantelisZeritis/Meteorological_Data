# Scrapy settings for main project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "main"

SPIDER_MODULES = ["main.spiders"]
NEWSPIDER_MODULE = "main.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "main (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "main.middlewares.mainSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "main.middlewares.mainDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "main.pipelines.mainPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
FEED_EXPORTERS = {
    'csv': 'main.exporters.HeadlessCsvItemExporter',
}

# ==========================================
# PLAYWRIGHT SETTINGS (Anti-Scraping Bypass)
# ==========================================

# 1. Λέμε στο Scrapy να χρησιμοποιεί το Playwright για HTTP και HTTPS
#DOWNLOAD_HANDLERS = {
#    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#}

# 2. Το Playwright απαιτεί Asyncio Reactor (το έχεις ήδη στα logs, αλλά το ορίζουμε για σιγουριά)
#TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# 3. Ορίζουμε ότι θέλουμε να χρησιμοποιηθεί ο Chromium
#PLAYWRIGHT_BROWSER_TYPE = "chromium"

# 4. Ορίζουμε τις παραμέτρους του Browser
#PLAYWRIGHT_LAUNCH_OPTIONS = {
#    "headless": True,  # True = Ο browser τρέχει αόρατα στο παρασκήνιο. False = Ανοίγει παράθυρο (χρήσιμο για debugging)
#    "args": [
#        "--disable-blink-features=AutomationControlled",  # Κρύβει το γεγονός ότι είναι bot
#    ]
#}
